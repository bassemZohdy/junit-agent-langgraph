import asyncio
import argparse
from pathlib import Path
from langchain_core.messages import HumanMessage
from .graphs.workflow import create_workflow
from .states import ProjectState
from .cli import EnhancedCLI


def parse_args():
    parser = argparse.ArgumentParser(description="LangGraph + Ollama Application")
    parser.add_argument("--project-path", type=str, required=True, help="Path to the project directory")
    return parser.parse_args()


async def main(project_path: str):
    project_path_obj = Path(project_path)
    
    if not project_path_obj.exists():
        print(f"Error: Project path '{project_path}' does not exist")
        return
    
    if not project_path_obj.is_dir():
        print(f"Error: Project path '{project_path}' is not a directory")
        return
    
    cli = EnhancedCLI(project_path)
    cli.print_header()
    
    app = create_workflow()
    
    initial_state: ProjectState = {
        "messages": [],
        "project_path": str(project_path_obj.absolute()),
        "project_name": project_path_obj.name,
        "packaging_type": "jar",
        "version": "1.0.0",
        "description": None,
        "java_classes": [],
        "test_classes": [],
        "current_class": None,
        "maven_group_id": "",
        "maven_artifact_id": "",
        "dependencies": [],
        "test_dependencies": [],
        "transitive_dependencies": [],
        "dependency_graph": {},
        "plugins": [],
        "build_status": {
            "last_build_time": None,
            "build_status": "not_built",
            "build_duration": None,
            "goals": [],
            "output_directory": "target/classes",
            "test_results": {},
            "compilation_errors": []
        },
        "last_action": "initialized",
        "summary_report": None,
        "source_directory": "src/main/java",
        "test_directory": "src/test/java",
        "output_directory": "target",
        "has_spring": False,
        "has_junit": False,
        "has_mockito": False,
        "retry_count": 0,
        "max_retries": 3,
        "test_results": {},
        "all_tests_passed": False
    }
    
    try:
        while True:
            user_input = cli.print_prompt()
            
            if user_input.lower() in ("exit", "quit"):
                cli.print_success("Goodbye!")
                cli.save_history()
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ("help", "?"):
                cli.print_help()
                continue
            
            if user_input.lower() in ("clear", "cls"):
                cli.clear_screen()
                cli.print_header()
                continue
            
            cli.print_command(user_input)
            
            try:
                new_message = HumanMessage(content=user_input)
                updated_state = initial_state.copy()
                updated_state["messages"] = [*initial_state["messages"], new_message]
                
                with cli.show_progress_bar("Processing...", total=100):
                    response = await app.ainvoke(updated_state)
                    cli.print_success("Processing complete")
                
                message = response["messages"][-1]
                cli.print_assistant(message.content)
                
                initial_state = response
            except Exception as e:
                cli.print_error(str(e))
                cli.print_info("Please try again or use 'help' for available commands")
    
    except KeyboardInterrupt:
        cli.print_warning("\nInterrupted by user")
        cli.save_history()
    except Exception as e:
        cli.print_error(f"Unexpected error: {str(e)}")
        cli.save_history()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.project_path))
