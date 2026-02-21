from typing import Dict, List, Optional
from pathlib import Path
from langchain_core.tools import tool
from xml.etree import ElementTree as ET
from ..exceptions.handler import MavenError, create_error_response
from ..utils.validation import validate_project_directory, validate_pom_xml
from ..states.project import MavenDependencyState


@tool
def get_transitive_dependencies(project_path: str) -> str:
    """Get all transitive dependencies (direct and indirect) from Maven project."""
    try:
        pom_path = validate_project_directory(project_path) / "pom.xml"
        result = _run_maven_command(project_path, "dependency:tree")
        return f"Transitive dependencies:\n{result}"
    except (MavenError, Exception) as e:
        response = create_error_response(e)
        return f"Error getting transitive dependencies: {response['errors'][0]}"


@tool
def build_dependency_graph(project_path: str) -> Dict:
    """Build a dependency graph of all Maven dependencies."""
    try:
        pom_path = validate_pom_xml(Path(project_path) / "pom.xml")
        
        tree = ET.parse(pom_path)
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        
        graph = {"nodes": {}, "edges": []}
        
        dependencies = tree.findall(".//mvn:dependency", ns)
        
        for dep in dependencies:
            group_id_elem = dep.find("mvn:groupId", ns)
            artifact_id_elem = dep.find("mvn:artifactId", ns)
            version_elem = dep.find("version", ns)
            scope_elem = dep.find("mvn:scope", ns)
            
            group_id = group_id_elem.text if group_id_elem is not None else ""
            artifact_id = artifact_id_elem.text if artifact_id_elem is not None else ""
            version = version_elem.text if version_elem is not None else ""
            scope = scope_elem.text if scope_elem is not None else "compile"
            
            dep_key = f"{group_id}:{artifact_id}:{version}"
            
            graph["nodes"][dep_key] = {
                "group_id": group_id,
                "artifact_id": artifact_id,
                "version": version,
                "scope": scope,
                "type": "dependency"
            }
        
        result = _run_maven_command(project_path, "dependency:resolve")
        parse_output(result["stdout"], graph)
        
        return graph
    except (MavenError, Exception) as e:
        response = create_error_response(e)
        return {
            "nodes": {},
            "edges": [],
            "error": response['errors'][0]
        }


@tool
def detect_dependency_conflicts(project_path: str) -> str:
    """Detect dependency version conflicts in Maven project."""
    try:
        validate_project_directory(project_path)
        
        result = _run_maven_command(project_path, "dependency:analyze")

        conflicts = []
        lines = result["stdout"].split('\n')
        
        for line in lines:
            if "conflict" in line.lower() and "version" in line.lower():
                conflicts.append(line.strip())
        
        if conflicts:
            return f"Found {len(conflicts)} conflicts:\n" + "\n".join(conflicts[:10])
        else:
            return "No dependency conflicts found"
    except (MavenError, Exception) as e:
        response = create_error_response(e)
        return f"Error detecting conflicts: {response['errors'][0]}"


@tool
def suggest_dependency_updates(project_path: str) -> str:
    """Suggest dependency updates using Maven versions plugin."""
    try:
        validate_project_directory(project_path)
        
        result = _run_maven_command(project_path, "versions:display-dependency-updates")
        return f"Suggested updates:\n{result}"
    except (MavenError, Exception) as e:
        response = create_error_response(e)
        return f"Error suggesting updates: {response['errors'][0]}"


def _run_maven_command(project_path: str, command: str) -> Dict:
    """Helper to run Maven command and return structured result."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["mvn", *command.split()],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "command": command,
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "command": command,
            "returncode": -1,
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }
    except Exception as e:
        return {
            "command": command,
            "returncode": -1,
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }


def parse_output(output: str, graph: Dict) -> None:
    """Parse Maven dependency tree output and build graph structure."""
    lines = output.split('\n')
    
    current_node = None
    current_depth = 0
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("[INFO]"):
            parts = line.split()
            if len(parts) >= 3:
                info_level, rest = parts[0], parts[1]
                current_node = rest.strip().rstrip(":")
                current_depth = info_level.count("-") + 1
        
        elif line.startswith("|- ") and current_node:
            parts = line.split(" ", 1)
            depth = parts[0].count("-") + 1
            dependency = parts[1].strip().rstrip(":")
            
            if dependency in graph["nodes"]:
                graph["edges"].append({
                    "source": current_node,
                    "target": dependency,
                    "depth": current_depth
                })
        
        elif not line.strip():
            current_node = None
            current_depth = 0
