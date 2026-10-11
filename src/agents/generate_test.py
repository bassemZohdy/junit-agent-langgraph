import os
from typing import Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from .base import BaseAgent


class GenerateTestAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="GenerateTestAgent")

    async def process(self, state: dict) -> dict:
        current_class = state.get("current_class")
        
        if not current_class:
            return {"last_action": "generate_test_failed", "error": "No class to generate tests for"}
        
        class_name = current_class.get("name", "")
        class_content = current_class.get("content", "")
        methods = current_class.get("methods", [])
        fields = current_class.get("fields", [])
        
        if not class_content:
            return {"last_action": "generate_test_failed", "error": "No class content available"}
        
        await self.log(f"Generating tests for class: {class_name}")
        
        test_content = await self._generate_test_content(class_name, class_content, methods, fields,
                                                        state.get('review_feedback',[]))
        
        test_class_name = f"{class_name}Test"
        test_file_path = os.path.join(
            state.get("project_path", ""),
            "src/test/java",
            *(current_class.get("package") or "").split("."),
            f"{test_class_name}.java"
        )
        
        test_class_state = {
            "name": test_class_name,
            "file_path": test_file_path,
            "content": test_content,
            "target_class": class_name,
            "status": "generated",
            "errors": [],
            "review_comments": []
        }
        
        return {
            "test_classes": state.get("test_classes", []) + [test_class_state],
            "last_action": "test_generated"
        }

    async def _generate_test_content(self, class_name: str, class_content: str, methods: List[Dict], fields: List[Dict], review_feedback=None) -> str:
        methods_str = self._format_methods_for_prompt(methods)
        fields_str = self._format_fields_for_prompt(fields)
        
        system_prompt = """You are a senior Java developer specialized in writing comprehensive JUnit and Spring Boot test classes. 
Generate high-quality, well-structured test code following best practices."""

        user_prompt = f"""Generate a Java unit test class using the project's existing test dependencies:

Class Name: {class_name}

Source code:
{class_content}

Fields:
{fields_str}

Methods:
{methods_str}

Previous review feedback to address:
{chr(10).join(review_feedback or []) or 'Initial generation; no previous feedback.'}

Requirements:
1. Use the JUnit version available in the project, preserving its POM
2. Use Spring test annotations only if their test dependencies are available
3. Use Mockito only when available and needed for the class's actual dependencies
4. Write test methods for each public method with meaningful test cases
5. Include both positive and negative test cases where applicable
6. Use assertions from available test libraries; do not add dependencies
7. Use descriptive test names; @DisplayName requires JUnit Jupiter
8. Follow AAA pattern (Arrange, Act, Assert)
9. Include proper setUp/tearDown methods if needed

Generate only the Java test code without any explanations or markdown formatting."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        if self._llm:
            response = await self._llm.ainvoke(messages)
            test_code = response.content.strip()
            
            if test_code.startswith("```"):
                test_code = test_code.split("```")[1]
                if test_code.startswith("java"):
                    test_code = test_code[4:].strip()
            
            return test_code
        
        return self._generate_default_test(class_name, methods)

    def _format_methods_for_prompt(self, methods: List[Dict]) -> str:
        if not methods:
            return "No methods found"
        
        formatted = []
        for method in methods:
            modifiers = ", ".join(method.get("modifiers", []))
            return_type = method.get("return_type", "void")
            params = ", ".join([f"{p['type']} {p['name']}" for p in method.get("parameters", [])])
            formatted.append(f"  {modifiers} {return_type} {method['name']}({params})")
        
        return "\n".join(formatted)

    def _format_fields_for_prompt(self, fields: List[Dict]) -> str:
        if not fields:
            return "No fields found"
        
        formatted = []
        for field in fields:
            modifiers = ", ".join(field.get("modifiers", []))
            field_type = field.get("type", "Object")
            formatted.append(f"  {modifiers} {field_type} {field['name']}")
        
        return "\n".join(formatted)

    def _generate_default_test(self, class_name: str, methods: List[Dict]) -> str:
        test_class_name = f"{class_name}Test"
        
        test_methods = []
        for method in methods:
            if method.get("is_public", False):
                test_methods.append(f"""
    @Test
    @DisplayName("Test {method['name']}")
    void test{method['name'].capitalize()}() {{
        // Arrange
        // Act
        // Assert
        fail("Not implemented yet");
    }}""")
        
        return f"""import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class {test_class_name} {{
{''.join(test_methods)}
}}"""
