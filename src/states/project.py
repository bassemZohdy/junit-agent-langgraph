from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ImportState(TypedDict):
    name: str
    is_static: bool
    is_wildcard: bool
    line_number: Optional[int]


class FieldState(TypedDict):
    name: str
    type: str
    modifiers: list[str]
    is_static: bool
    is_final: bool
    default_value: Optional[str]
    annotations: list["AnnotationState"]
    line_number: Optional[int]


class AnnotationState(TypedDict):
    name: str
    elements: dict[str, str]
    target: Optional[str]
    line_number: Optional[int]


class MethodState(TypedDict):
    name: str
    return_type: str
    parameters: list[dict[str, str]]
    modifiers: list[str]
    annotations: list[AnnotationState]
    throws: list[str]
    body: Optional[str]
    is_abstract: bool
    line_number: Optional[int]


class JavaClassState(TypedDict):
    name: str
    file_path: str
    package: Optional[str]
    content: Optional[str]
    type: str
    modifiers: list[str]
    extends: Optional[str]
    implements: list[str]
    annotations: list[AnnotationState]
    fields: list[FieldState]
    methods: list[MethodState]
    imports: list[ImportState]
    inner_classes: list[JavaClassState]
    status: str
    errors: list[str]
    line_number: Optional[int]


class TestClassState(TypedDict):
    name: str
    file_path: str
    package: Optional[str]
    content: Optional[str]
    target_class: str
    test_methods: list[MethodState]
    status: str
    errors: list[str]
    review_comments: list[str]


class MavenDependencyState(TypedDict):
    group_id: str
    artifact_id: str
    version: str
    type: str
    scope: Optional[str]
    is_test: bool
    dependencies: list[dict]


class MavenPluginState(TypedDict):
    group_id: str
    artifact_id: str
    version: str
    configuration: dict
    executions: list[dict]


class MavenBuildState(TypedDict):
    last_build_time: Optional[str]
    build_status: str
    build_duration: Optional[str]
    goals: list[str]
    output_directory: str
    test_results: dict[str, str | bool]
    compilation_errors: list[str]


class ProjectState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    project_path: str
    project_name: str
    packaging_type: str
    version: str
    description: Optional[str]
    
    java_classes: list[JavaClassState]
    test_classes: list[TestClassState]
    current_class: Optional[JavaClassState]
    
    maven_group_id: str
    maven_artifact_id: str
    dependencies: list[MavenDependencyState]
    test_dependencies: list[MavenDependencyState]
    transitive_dependencies: list[MavenDependencyState]
    dependency_graph: dict
    plugins: list[MavenPluginState]
    
    build_status: MavenBuildState
    last_action: str
    summary_report: Optional[str]
    
    source_directory: str
    test_directory: str
    output_directory: str
    
    has_spring: bool
    has_junit: bool
    has_mockito: bool
    
    retry_count: int
    max_retries: int
    test_results: dict
    all_tests_passed: bool
