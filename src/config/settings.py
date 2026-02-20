import os
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    project_path: str = ""
    
    test_source_directory: str = "src/test/java"
    test_output_directory: str = "target/test-classes"
    
    max_retries: int = 3
    retry_delay_seconds: int = 1
    
    llm_timeout_seconds: int = 120
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    
    maven_timeout_seconds: int = 300
    maven_goals: str = "clean compile"
    maven_test_goals: str = "test"
    
    source_directory: str = "src/main/java"
    output_directory: str = "target/classes"
    
    java_file_extensions: list = field(default_factory=lambda: ["*.java"])
    
    skip_tests: bool = False
    parallel_file_operations: bool = False
    cache_enabled: bool = True
    
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        config = cls()
        
        config.project_path = os.getenv("PROJECT_PATH", config.project_path)
        config.test_source_directory = os.getenv("TEST_SOURCE_DIR", config.test_source_directory)
        config.max_retries = int(os.getenv("MAX_RETRIES", str(config.max_retries)))
        config.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT", str(config.llm_timeout_seconds)))
        config.llm_temperature = float(os.getenv("LLM_TEMPERATURE", str(config.llm_temperature)))
        config.maven_timeout_seconds = int(os.getenv("MAVEN_TIMEOUT", str(config.maven_timeout_seconds)))
        config.skip_tests = os.getenv("SKIP_TESTS", "false").lower() == "true"
        config.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        config.log_level = os.getenv("LOG_LEVEL", config.log_level)
        
        return config
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if self.project_path and not Path(self.project_path).exists():
            errors.append(f"Project path does not exist: {self.project_path}")
        
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        
        if self.llm_timeout_seconds <= 0:
            errors.append("llm_timeout_seconds must be positive")
        
        if self.maven_timeout_seconds <= 0:
            errors.append("maven_timeout_seconds must be positive")
        
        if self.llm_temperature < 0 or self.llm_temperature > 2:
            errors.append("llm_temperature must be between 0 and 2")
        
        return errors
    
    def get_test_class_path(self, class_name: str, package: Optional[str] = None) -> str:
        """
        Get the file path for a test class.
        
        Args:
            class_name: Name of the test class
            package: Optional package name (with dots)
        
        Returns:
            Full file path for the test class
        """
        if package:
            package_path = package.replace(".", os.sep)
            path_parts = [self.project_path, self.test_source_directory, package_path, f"{class_name}.java"]
        else:
            path_parts = [self.project_path, self.test_source_directory, f"{class_name}.java"]
        
        return os.path.join(*path_parts)


def get_config() -> AppConfig:
    """Get the application configuration (from env or defaults)."""
    return AppConfig.from_env()
