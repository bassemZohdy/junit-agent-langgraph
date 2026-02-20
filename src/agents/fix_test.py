from typing import Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from .base import BaseAgent


class FixTestAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="FixTestAgent")

    async def process(self, state: dict) -> dict:
        test_classes = state.get("test_classes", [])
        test_results = state.get("test_results", {})
        
        if not test_classes:
            return {"last_action": "fix_test_failed", "error": "No tests to fix"}
        
        latest_test = test_classes[-1]
        test_name = latest_test.get("name", "")
        
        await self.log(f"Fixing test class: {test_name}")
        
        current_test_content = latest_test.get("content", "")
        validation_result = test_results.get(test_name, {})
        errors = validation_result.get("errors", [])
        stack_traces = validation_result.get("stack_traces", [])
        
        if not current_test_content:
            return {"last_action": "fix_test_failed", "error": "No test content to fix"}
        
        fixed_test_content = await self._generate_fixed_test(
            current_test_content,
            errors,
            stack_traces,
            latest_test
        )
        
        updated_test_classes = test_classes.copy()
        updated_test_classes[-1]["content"] = fixed_test_content
        updated_test_classes[-1]["status"] = "fixed"
        
        retry_count = state.get("retry_count", 0) + 1
        
        return {
            "test_classes": updated_test_classes,
            "retry_count": retry_count,
            "last_action": "test_fixed"
        }

    async def _generate_fixed_test(self, test_content: str, errors: List[str], stack_traces: List[str], test_class: dict) -> str:
        test_name = test_class.get("name", "")
        target_class = test_class.get("target_class", "")
        
        errors_str = "\n".join([f"- {error}" for error in errors])
        
        stack_traces_str = "\n\n".join(stack_traces[:3])
        
        system_prompt = """You are a senior Java developer specializing in fixing failing test cases.
Analyze the errors and stack traces to understand what's wrong, then provide a corrected version of the test code.
Focus on:
1. Fixing the root cause of the failures
2. Maintaining test quality and best practices
3. Ensuring proper mocking and assertions
4. Handling edge cases properly
5. Following JUnit 5 and Spring Boot conventions"""

        user_prompt = f"""Fix the following failing test class based on the errors and stack traces:

Test Class Name: {test_name}
Target Class: {target_class}

Current Test Code:
{test_content}

Errors Encountered:
{errors_str}

Stack Traces:
{stack_traces_str}

Instructions:
1. Analyze the errors and stack traces to understand the failures
2. Fix the test code to resolve all issues
3. Ensure the fixes are minimal and focused on the actual problems
4. Maintain the existing test structure and best practices
5. Provide only the corrected Java test code without any explanations or markdown formatting"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        if self._llm:
            response = await self._llm.ainvoke(messages)
            fixed_code = response.content.strip()
            
            if fixed_code.startswith("```"):
                fixed_code = fixed_code.split("```")[1]
                if fixed_code.startswith("java"):
                    fixed_code = fixed_code[4:].strip()
            
            return fixed_code
        
        return self._apply_simple_fixes(test_content, errors)

    def _apply_simple_fixes(self, test_content: str, errors: List[str]) -> str:
        fixed_content = test_content
        
        for error in errors:
            if "NullPointerException" in error:
                if "mock" in error.lower() and "@Mock" not in fixed_content:
                    import_section = fixed_content.split("class")[0]
                    if "import org.mockito.Mock" not in import_section:
                        fixed_content = fixed_content.replace(
                            "import org.junit.jupiter.api.Test;",
                            "import org.junit.jupiter.api.Test;\nimport org.mockito.Mock;"
                        )
            
            if "cannot find symbol" in error.lower():
                if "import" not in fixed_content:
                    fixed_content = "// TODO: Add missing imports\n" + fixed_content
        
        return fixed_content
