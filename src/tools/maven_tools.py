import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
from ..exceptions.handler import MavenError, FileOperationError, create_error_response
from ..utils.validation import (
    validate_directory_exists,
    validate_project_directory,
    validate_not_empty,
    validate_maven_goal,
    validate_pom_xml,
    validate_positive_integer
)
from ..states.java_project_states import (
    ProjectState,
    MavenDependencyState,
    MavenPluginState,
    MavenBuildState,
    JavaClassState
)
from .java_tools import create_java_class_state


@tool
def maven_build(directory: str, goals: str = "compile") -> str:
    """Run Maven build with specified goals."""
    try:
        validate_not_empty(directory, "directory")
        validate_not_empty(goals, "goals")
        
        path = validate_project_directory(directory)
        
        goal_list = goals.split()
        for goal in goal_list:
            validate_maven_goal(goal)
        
        result = subprocess.run(
            ["mvn", *goal_list],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"Maven build successful:\n{result.stdout}"
        else:
            return f"Maven build failed:\n{result.stderr}"
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error running Maven: {response['errors'][0]}"


@tool
def maven_test(directory: str) -> str:
    """Run Maven tests."""
    try:
        path = validate_project_directory(directory)
        
        result = subprocess.run(
            ["mvn", "test"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"Tests passed:\n{result.stdout}"
        else:
            return f"Tests failed:\n{result.stderr}"
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error running Maven tests: {response['errors'][0]}"


@tool
def maven_clean(directory: str) -> str:
    """Run Maven clean to remove build artifacts."""
    try:
        path = validate_project_directory(directory)
        
        result = subprocess.run(
            ["mvn", "clean"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        
        return f"Maven clean completed:\n{result.stdout}"
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error running Maven clean: {response['errors'][0]}"


@tool
def maven_package(directory: str) -> str:
    """Package project into JAR."""
    try:
        path = validate_project_directory(directory)
        
        result = subprocess.run(
            ["mvn", "package"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"Maven package successful:\n{result.stdout}"
        else:
            return f"Maven package failed:\n{result.stderr}"
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error running Maven package: {response['errors'][0]}"


@tool
def maven_dependency_tree(directory: str) -> str:
    """Show Maven dependency tree."""
    try:
        path = validate_project_directory(directory)
        
        result = subprocess.run(
            ["mvn", "dependency:tree"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        
        return result.stdout
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error showing dependency tree: {response['errors'][0]}"


@tool
def maven_info(directory: str) -> str:
    """Get Maven project information."""
    try:
        path = validate_project_directory(directory)
        
        result = subprocess.run(
            ["mvn", "help:effective-pom"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        
        return result.stdout
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting Maven info: {response['errors'][0]}"


@tool
def create_project_state(project_path: str) -> ProjectState:
    """Create ProjectState by reading directly from file system."""
    try:
        path = Path(project_path)
        if not path.exists() or not path.is_dir():
            return _create_error_project_state(project_path, "Path does not exist or is not a directory")
        
        pom_xml = path / "pom.xml"
        has_maven = pom_xml.exists()
        
        maven_info = {}
        dependencies = []
        plugins = []
        has_spring = False
        has_junit = False
        has_mockito = False
        
        if has_maven:
            try:
                pom_data = parse_pom_xml(pom_path=str(pom_xml))
                maven_info = pom_data
                dependencies = extract_dependencies(project_path)
                plugins = extract_plugins(project_path)
                
                for dep in dependencies:
                    if "spring" in dep["artifact_id"].lower():
                        has_spring = True
                    if "junit" in dep["artifact_id"].lower():
                        has_junit = True
                    if "mockito" in dep["artifact_id"].lower():
                        has_mockito = True
            except Exception as e:
                pass
        
        java_files = list(path.rglob("*.java"))
        java_classes = [create_java_class_state(str(f)) for f in java_files]
        
        return {
            "messages": [],
            "project_path": str(path.absolute()),
            "project_name": path.name,
            "packaging_type": maven_info.get("packaging", "jar") if maven_info else "jar",
            "version": maven_info.get("version", "1.0.0") if maven_info else "1.0.0",
            "description": None,
            "java_classes": java_classes,
            "test_classes": [],
            "current_class": None,
            "maven_group_id": maven_info.get("group_id", "") if maven_info else "",
            "maven_artifact_id": maven_info.get("artifact_id", "") if maven_info else "",
            "dependencies": dependencies,
            "test_dependencies": [d for d in dependencies if d.get("is_test", False)],
            "transitive_dependencies": [],
            "dependency_graph": {},
            "plugins": plugins,
            "build_status": {
                "last_build_time": None,
                "build_status": "not_built",
                "build_duration": None,
                "goals": [],
                "output_directory": "target/classes",
                "test_results": {},
                "compilation_errors": []
            },
            "last_action": "initialized_from_filesystem",
            "summary_report": None,
            "source_directory": "src/main/java",
            "test_directory": "src/test/java",
            "output_directory": "target",
            "has_spring": has_spring,
            "has_junit": has_junit,
            "has_mockito": has_mockito
        }
    except Exception as e:
        return _create_error_project_state(project_path, str(e))


def _create_error_project_state(project_path: str, error_msg: str) -> ProjectState:
    """Create error ProjectState."""
    path = Path(project_path)
    return {
        "messages": [],
        "project_path": str(path.absolute()),
        "project_name": path.name if path.exists() else "",
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
            "build_status": "error",
            "build_duration": None,
            "goals": [],
            "output_directory": "target/classes",
            "test_results": {},
            "compilation_errors": [error_msg]
        },
        "last_action": "error",
        "summary_report": None,
        "source_directory": "src/main/java",
        "test_directory": "src/test/java",
        "output_directory": "target",
        "has_spring": False,
        "has_junit": False,
        "has_mockito": False
    }


@tool
def refresh_project_state(project_state: ProjectState) -> ProjectState:
    """Refresh ProjectState by re-reading from file system."""
    return create_project_state(project_state["project_path"])


@tool
def refresh_java_class_state(java_class_path: str) -> JavaClassState:
    """Refresh JavaClassState by re-reading from file system."""
    return create_java_class_state(java_class_path)


@tool
def record_build_result(project_path: str, success: bool, duration: Optional[str] = None, errors: Optional[list[str]] = None) -> str:
    """Record build result to build.log file in project directory."""
    try:
        path = validate_directory_exists(project_path)
        
        build_log_path = path / ".build.log"
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        log_entry = f"\n=== Build at {timestamp} ===\n"
        log_entry += f"Status: {'SUCCESS' if success else 'FAILURE'}\n"
        if duration:
            log_entry += f"Duration: {duration}\n"
        if errors:
            log_entry += f"Errors:\n" + "\n".join([f"  - {e}" for e in errors])
        
        if build_log_path.exists():
            existing = build_log_path.read_text(encoding="utf-8")
            build_log_path.write_text(existing + log_entry, encoding="utf-8")
        else:
            build_log_path.write_text(log_entry, encoding="utf-8")
        
        return f"Build result recorded to .build.log"
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error recording build result: {response['errors'][0]}"


@tool
def get_build_history(project_path: str, limit: int = 10) -> str:
    """Read build history from .build.log file."""
    try:
        path = validate_directory_exists(project_path)
        validate_positive_integer(limit, "limit")
        
        build_log_path = path / ".build.log"
        
        if not build_log_path.exists():
            return "No build history found"
        
        content = build_log_path.read_text(encoding="utf-8")
        entries = content.split("=== Build at ")
        
        if limit:
            entries = entries[-limit:]
        
        return "\n".join([f"=== Build at {e}" for e in entries if e.strip()])
    except (MavenError, FileOperationError) as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error reading build history: {response['errors'][0]}"


@tool
def parse_pom_xml(pom_path: str) -> dict:
    """Parse pom.xml and extract Maven project information."""
    try:
        validate_pom_xml(pom_path)
        
        tree = ET.parse(pom_path)
        root = tree.getroot()
        
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        
        def get_text(path: str) -> str:
            elem = root.find(path, ns)
            return elem.text if elem is not None else ""
        
        group_id = get_text("mvn:groupId")
        artifact_id = get_text("mvn:artifactId")
        version = get_text("mvn:version")
        packaging = get_text("mvn:packaging") or "jar"
        
        return {
            "group_id": group_id,
            "artifact_id": artifact_id,
            "version": version,
            "packaging": packaging
        }
    except (MavenError, FileOperationError) as e:
        return {}
    except Exception as e:
        return {}


@tool
def extract_dependencies(project_path: str) -> list[MavenDependencyState]:
    """Extract all dependencies from pom.xml."""
    try:
        pom_xml = validate_project_directory(project_path) / "pom.xml"
        
        tree = ET.parse(pom_xml)
        root = tree.getroot()
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        
        dependencies = []
        
        for dep in root.findall(".//mvn:dependency", ns):
            group_id = dep.find("mvn:groupId", ns)
            artifact_id = dep.find("mvn:artifactId", ns)
            version = dep.find("mvn:version", ns)
            scope = dep.find("mvn:scope", ns)
            dep_type = dep.find("mvn:type", ns)
            
            dep_info: MavenDependencyState = {
                "group_id": group_id.text if group_id is not None else "",
                "artifact_id": artifact_id.text if artifact_id is not None else "",
                "version": version.text if version is not None else "",
                "type": dep_type.text if dep_type is not None else "jar",
                "scope": scope.text if scope is not None else "compile",
                "is_test": scope.text == "test" if scope is not None else False,
                "dependencies": []
            }
            dependencies.append(dep_info)
        
        return dependencies
    except (MavenError, FileOperationError) as e:
        return []
    except Exception as e:
        return []


@tool
def extract_plugins(project_path: str) -> list[MavenPluginState]:
    """Extract all plugins from pom.xml."""
    try:
        pom_xml = validate_project_directory(project_path) / "pom.xml"
        
        tree = ET.parse(pom_xml)
        root = tree.getroot()
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        
        plugins = []
        
        for plugin in root.findall(".//mvn:plugin", ns):
            group_id = plugin.find("mvn:groupId", ns)
            artifact_id = plugin.find("mvn:artifactId", ns)
            version = plugin.find("mvn:version", ns)
            
            plugin_info: MavenPluginState = {
                "group_id": group_id.text if group_id is not None else "org.apache.maven.plugins",
                "artifact_id": artifact_id.text if artifact_id is not None else "",
                "version": version.text if version is not None else "",
                "configuration": {},
                "executions": []
            }
            plugins.append(plugin_info)
        
        return plugins
    except (MavenError, FileOperationError) as e:
        return []
    except Exception as e:
        return []


maven_tools = [
    maven_build,
    maven_test,
    maven_clean,
    maven_package,
    maven_dependency_tree,
    maven_info,
    create_project_state,
    refresh_project_state,
    refresh_java_class_state,
    record_build_result,
    get_build_history,
    parse_pom_xml,
    extract_dependencies,
    extract_plugins
]
