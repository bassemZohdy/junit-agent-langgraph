#!/usr/bin/env python3
"""
Simple Test Generation Script

This script generates test classes for sample projects without the interactive CLI.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langchain_core.messages import HumanMessage
from src.graphs.workflow import create_test_generation_workflow
from src.states import ProjectState
from src.tools.java_tools import analyze_java_class


async def generate_tests_for_project(project_path: str, sample_name: str):
    """Generate test classes for a given project."""
    project_dir = Path(project_path)
    
    print(f"\n{'='*60}")
    print(f"Generating tests for: {sample_name}")
    print(f"{'='*60}\n")
    
    if not project_dir.exists():
        print(f"Error: Project path '{project_path}' does not exist")
        return False

    # Find Java source files
    java_files = sorted(project_dir.rglob("*.java"))
    if not java_files:
        print(f"No Java files found in {project_path}")
        return False

    file_list = [str(f) for f in java_files]

    print(f"Found {len(file_list)} Java files to process")
    
    # Initialize workflow
    workflow = create_test_generation_workflow()
    
    # Initialize state
    initial_state: ProjectState = {
        "messages": [],
        "project_path": str(project_dir.absolute()),
        "project_name": sample_name,
        "packaging_type": "jar",
        "version": "1.0.0",
        "description": f"Test generation for {sample_name}",
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
        # Process each Java file and generate tests
        for i, file_path in enumerate(file_list, 1):
            print(f"\n[{i}/{len(file_list)}] Processing: {Path(file_path).name}")

            # Analyze class
            class_state = analyze_java_class(path=file_path)
            
            if class_state.get("errors"):
                print(f"  [WARNING] Errors parsing class, skipping...")
                continue
            
            # Add message to trigger analysis and test generation
            state = initial_state.copy()
            state["java_classes"] = [class_state]
            state["current_class"] = class_state
            
            message = HumanMessage(content=f"Generate comprehensive tests for {class_state['name']}")
            state["messages"] = [*initial_state["messages"], message]
            
            # Run workflow to generate tests
            result = await workflow.ainvoke(state)
            
            if result.get("test_classes"):
                test_classes = result["test_classes"]
                print(f"  [OK] Generated {len(test_classes)} test classes")
                
                # Write test classes to files
                for test_class in test_classes:
                    if test_class.get("content"):
                        class_name = test_class.get("name", "Unknown")
                        content = test_class.get("content", "")
                        
                        # Determine file path
                        test_file_path = project_dir / "src" / "test" / "java" / "com" / "example" / f"{class_name}.java"
                        
                        # Create directory if needed
                        test_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Write test file
                        with open(test_file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"    [OK] Created: {test_file_path.relative_to(project_dir)}")
        
        print(f"\n{'='*60}")
        print(f"Test generation complete for: {sample_name}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] During test generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function to generate tests for all sample projects."""
    script_dir = Path(__file__).parent
    samples_dir = script_dir / "tests" / "samples"
    
    samples = [
        {
            "name": "junit4-sample",
            "path": samples_dir / "junit4-sample"
        },
        {
            "name": "junit5-sample",
            "path": samples_dir / "junit5-sample"
        },
        {
            "name": "springboot-sample",
            "path": samples_dir / "springboot-sample"
        },
        {
            "name": "multi-module",
            "path": samples_dir / "multi-module"
        }
    ]
    
    results = {}
    
    for sample in samples:
        results[sample["name"]] = await generate_tests_for_project(
            str(sample["path"]),
            sample["name"]
        )
    
    # Summary
    print("\n" + "="*60)
    print("TEST GENERATION SUMMARY")
    print("="*60 + "\n")
    
    for name, success in results.items():
        if success:
            status = "[OK]"
        else:
            status = "[FAILED]"
        print(f"{name}: {status}")
    
    print(f"\nTotal samples: {len(samples)}")
    print(f"Successful: {sum(results.values())}")
    print(f"Failed: {len(results) - sum(results.values())}")


if __name__ == "__main__":
    asyncio.run(main())
