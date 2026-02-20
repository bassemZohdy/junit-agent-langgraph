import asyncio
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from ..states.project import (
    ProjectState,
    MavenDependencyState,
    MavenPluginState,
    MavenBuildState
)
from .java_tools import create_java_class_state


async def maven_build_async(directory: str, goals: str = "compile") -> dict:
    """Run Maven build with specified goals and return structured result."""
    try:
        path = Path(directory)
        if not path.exists():
            return {
                "success": False,
                "returncode": 1,
                "stdout": "",
                "stderr": f"Error: Directory '{directory}' does not exist"
            }
        
        pom_xml = path / "pom.xml"
        if not pom_xml.exists():
            return {
                "success": False,
                "returncode": 1,
                "stdout": "",
                "stderr": f"Error: pom.xml not found in '{directory}'"
            }
        
        process = await asyncio.create_subprocess_exec(
            "mvn",
            *goals.split(),
            cwd=str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else ""
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": f"Error running Maven: {str(e)}"
        }


async def maven_test_async(directory: str) -> dict:
    """Run Maven tests and return structured result."""
    try:
        path = Path(directory)
        if not path.exists():
            return {
                "success": False,
                "returncode": 1,
                "stdout": "",
                "stderr": f"Error: Directory '{directory}' does not exist"
            }
        
        process = await asyncio.create_subprocess_exec(
            "mvn",
            "test",
            cwd=str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else ""
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": f"Error running Maven tests: {str(e)}"
        }


async def maven_clean_async(directory: str) -> dict:
    """Run Maven clean to remove build artifacts."""
    try:
        path = Path(directory)
        if not path.exists():
            return {
                "success": False,
                "returncode": 1,
                "stdout": "",
                "stderr": f"Error: Directory '{directory}' does not exist"
            }
        
        process = await asyncio.create_subprocess_exec(
            "mvn",
            "clean",
            cwd=str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "success": True,
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else ""
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": f"Error running Maven clean: {str(e)}"
        }


async def maven_package_async(directory: str) -> dict:
    """Package project into JAR."""
    try:
        path = Path(directory)
        if not path.exists():
            return {
                "success": False,
                "returncode": 1,
                "stdout": "",
                "stderr": f"Error: Directory '{directory}' does not exist"
            }
        
        process = await asyncio.create_subprocess_exec(
            "mvn",
            "package",
            cwd=str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else ""
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": f"Error running Maven package: {str(e)}"
        }


async def parse_pom_xml_async(pom_path: str) -> dict:
    """Parse pom.xml and extract Maven project information."""
    try:
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
            "success": True,
            "group_id": group_id,
            "artifact_id": artifact_id,
            "version": version,
            "packaging": packaging
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "group_id": "",
            "artifact_id": "",
            "version": "",
            "packaging": "jar"
        }


async def extract_dependencies_async(project_path: str) -> list[MavenDependencyState]:
    """Extract all dependencies from pom.xml."""
    try:
        pom_xml = Path(project_path) / "pom.xml"
        if not pom_xml.exists():
            return []
        
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
    except Exception as e:
        return []


async def extract_plugins_async(project_path: str) -> list[MavenPluginState]:
    """Extract all plugins from pom.xml."""
    try:
        pom_xml = Path(project_path) / "pom.xml"
        if not pom_xml.exists():
            return []
        
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
    except Exception as e:
        return []
