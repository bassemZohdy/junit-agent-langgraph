from typing import Literal
from langgraph.graph import StateGraph, END, START
from ..llm import create_llm
from ..states.project import ProjectState
from ..agents.analyze_project import AnalyzeProjectAgent
from ..agents.class_analysis import ClassAnalysisAgent
from ..agents.generate_test import GenerateTestAgent
from ..agents.review_test import ReviewTestAgent
from ..agents.validate_test import ValidateTestAgent
from ..agents.fix_test import FixTestAgent
from ..agents.project_validator import ProjectValidatorAgent


def create_test_generation_workflow(llm=None, max_retries=3):
    if llm is None:
        llm = create_llm()
    
    analyze_project_agent = AnalyzeProjectAgent(llm=llm)
    class_analysis_agent = ClassAnalysisAgent(llm=llm)
    generate_test_agent = GenerateTestAgent(llm=llm)
    review_test_agent = ReviewTestAgent(llm=llm)
    validate_test_agent = ValidateTestAgent(llm=llm)
    fix_test_agent = FixTestAgent(llm=llm)
    project_validator_agent = ProjectValidatorAgent(llm=llm)

    async def analyze_project_node(state: ProjectState):
        result = await analyze_project_agent.process(state)
        return result

    async def class_analysis_node(state: ProjectState):
        java_classes = state.get("java_classes", [])
        
        if not java_classes:
            return {"last_action": "class_analysis_skipped", "current_class": None}
        
        results = []
        for java_class in java_classes:
            class_state = state.copy()
            class_state["current_class"] = java_class
            result = await class_analysis_agent.process(class_state)
            results.append(result)
        
        return {"last_action": "class_analysis_completed"}

    async def generate_test_node(state: ProjectState):
        java_classes = state.get("java_classes", [])
        
        if not java_classes:
            return {"last_action": "generate_test_failed", "error": "No classes to generate tests for"}
        
        test_classes = state.get("test_classes", [])
        
        for java_class in java_classes:
            class_state = state.copy()
            class_state["current_class"] = java_class
            class_state["test_classes"] = test_classes
            result = await generate_test_agent.process(class_state)
            test_classes = result.get("test_classes", test_classes)
        
        return {"test_classes": test_classes, "last_action": "tests_generated"}

    async def review_test_node(state: ProjectState):
        test_classes = state.get("test_classes", [])
        
        results = []
        for test_class in test_classes:
            test_state = state.copy()
            test_state["test_classes"] = [test_class]
            result = await review_test_agent.process(test_state)
            results.append(result)
        
        updated_test_classes = test_classes.copy()
        for i, result in enumerate(results):
            updated_test_classes[i] = result.get("test_classes", [test_classes[i]])[0]
        
        return {"test_classes": updated_test_classes, "last_action": "tests_reviewed"}

    async def validate_test_node(state: ProjectState):
        test_classes = state.get("test_classes", [])

        all_passed = True
        updated_test_classes = []
        all_test_results = {}

        for test_class in test_classes:
            test_state = state.copy()
            test_state["test_classes"] = [test_class]
            result = await validate_test_agent.process(test_state)

            updated_test = result.get("test_classes", [test_class])[0]
            updated_test_classes.append(updated_test)
            all_test_results.update(result.get("test_results", {}))

            if updated_test.get("status") != "passed":
                all_passed = False

        return {
            "test_classes": updated_test_classes,
            "test_results": all_test_results,
            "all_tests_passed": all_passed,
            "last_action": "tests_validated"
        }

    async def fix_test_node(state: ProjectState):
        test_classes = state.get("test_classes", [])
        
        failed_tests = [t for t in test_classes if t.get("status") in ["failed", "needs_fixes"]]
        
        updated_test_classes = test_classes.copy()
        
        for test_class in failed_tests:
            test_state = state.copy()
            test_state["test_classes"] = [test_class]
            result = await fix_test_agent.process(test_state)
            
            fixed_test = result.get("test_classes", [test_class])[0]
            
            for i, tc in enumerate(updated_test_classes):
                if tc["name"] == fixed_test["name"]:
                    updated_test_classes[i] = fixed_test
                    break
        
        return {
            "test_classes": updated_test_classes,
            "retry_count": state.get("retry_count", 0) + 1,
            "last_action": "tests_fixed"
        }

    async def project_validator_node(state: ProjectState):
        result = await project_validator_agent.process(state)
        return result

    def should_continue_review(state: ProjectState) -> Literal["generate_test", "validate_test"]:
        test_classes = state.get("test_classes", [])
        
        if not test_classes:
            return "validate_test"
        
        for test_class in test_classes:
            if test_class.get("status") in ["needs_fixes", "review_comments"]:
                return "generate_test"
        
        return "validate_test"

    def should_validate(state: ProjectState) -> Literal["fix_test", "project_validator", "end_failed"]:
        all_passed = state.get("all_tests_passed", True)
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)
        
        if all_passed:
            return "project_validator"
        elif retry_count < max_retries:
            return "fix_test"
        else:
            return "end_failed"

    async def end_failed_node(state: ProjectState):
        return {
            "build_status": "failed",
            "summary_report": "Max retries reached. Test generation failed.",
            "last_action": "workflow_failed"
        }

    workflow = StateGraph(ProjectState)
    
    workflow.add_node("analyze_project", analyze_project_node)
    workflow.add_node("class_analysis", class_analysis_node)
    workflow.add_node("generate_test", generate_test_node)
    workflow.add_node("review_test", review_test_node)
    workflow.add_node("validate_test", validate_test_node)
    workflow.add_node("fix_test", fix_test_node)
    workflow.add_node("project_validator", project_validator_node)
    workflow.add_node("end_failed", end_failed_node)
    
    workflow.add_edge(START, "analyze_project")
    workflow.add_edge("analyze_project", "class_analysis")
    workflow.add_edge("class_analysis", "generate_test")
    workflow.add_edge("generate_test", "review_test")
    
    workflow.add_conditional_edges(
        "review_test",
        should_continue_review,
        {
            "generate_test": "generate_test",
            "validate_test": "validate_test"
        }
    )
    
    workflow.add_conditional_edges(
        "validate_test",
        should_validate,
        {
            "fix_test": "fix_test",
            "project_validator": "project_validator",
            "end_failed": "end_failed"
        }
    )
    
    workflow.add_edge("fix_test", "validate_test")
    workflow.add_edge("project_validator", END)
    workflow.add_edge("end_failed", END)
    
    return workflow.compile()
