from enum import Enum


class TestStatus(str, Enum):
    """Status values for test classes."""
    GENERATED = "generated"
    REVIEWED = "reviewed"
    NEEDS_FIXES = "needs_fixes"
    FIXED = "fixed"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    COMPILATION_FAILED = "compilation_failed"


class BuildStatus(str, Enum):
    """Status values for build operations."""
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    NOT_BUILT = "not_built"
    RUNNING = "running"


class ClassStatus(str, Enum):
    """Status values for Java classes."""
    ANALYZED = "analyzed"
    ERROR = "error"
    PENDING = "pending"


class AgentAction(str, Enum):
    """Action identifiers for agent workflow tracking."""
    ANALYZED_PROJECT = "analyzed_project"
    CLASS_ANALYSIS_SKIPPED = "class_analysis_skipped"
    CLASS_ANALYSIS_COMPLETED = "class_analysis_completed"
    TESTS_GENERATED = "tests_generated"
    TESTS_REVIEWED = "tests_reviewed"
    TESTS_VALIDATED = "tests_validated"
    TESTS_FIXED = "tests_fixed"
    PROJECT_VALIDATED = "project_validated"
    WORKFLOW_FAILED = "workflow_failed"


class MavenScope(str, Enum):
    """Maven dependency scopes."""
    COMPILE = "compile"
    PROVIDED = "provided"
    RUNTIME = "runtime"
    TEST = "test"
    SYSTEM = "system"
    IMPORT = "import"


class ProjectType(str, Enum):
    """Java project types."""
    MAVEN = "maven"
    GRADLE = "gradle"
    PLAIN = "plain"


class PackagingType(str, Enum):
    """Maven packaging types."""
    JAR = "jar"
    WAR = "war"
    EAR = "ear"
    POM = "pom"
