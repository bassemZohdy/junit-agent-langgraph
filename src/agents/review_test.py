from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from .base import BaseAgent


class ReviewTestAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ReviewTestAgent")

    async def process(self, state: dict) -> dict:
        test_classes = state.get("test_classes", [])
        
        if not test_classes:
            return {"last_action": "review_test_skipped", "error": "No tests to review"}
        
        latest_test = test_classes[-1]
        
        await self.log(f"Reviewing test class: {latest_test['name']}")
        
        review_comments = await self._review_test_code(latest_test)
        
        updated_test_classes = test_classes.copy()
        updated_test_classes[-1]["review_comments"] = review_comments
        
        if review_comments:
            updated_test_classes[-1]["status"] = "needs_fixes"
        else:
            updated_test_classes[-1]["status"] = "reviewed"
        
        return {
            "test_classes": updated_test_classes,
            "last_action": "test_reviewed"
        }

    async def _review_test_code(self, test_class: dict) -> List[str]:
        test_name = test_class.get("name", "")
        test_content = test_class.get("content", "")
        
        if not test_content:
            return ["Test content is empty"]
        
        system_prompt = """You are a senior code reviewer specialized in Java testing best practices.
Review the provided test code for:
1. Code quality and readability
2. Proper use of JUnit 5 and Spring Boot annotations
3. Test coverage and completeness
4. Mock usage and dependency injection
5. Assertion quality and accuracy
6. Naming conventions
7. Potential bugs or anti-patterns
8. Performance considerations
9. Security best practices
10. Maintainability

Provide specific, actionable comments for any issues found."""

        user_prompt = f"""Review the following test class:

Test Class Name: {test_name}

Test Code:
{test_content}

Provide your review as a list of specific comments. If the code follows best practices and has no issues, return an empty list.
Format each comment as a clear, actionable statement."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        if self._llm:
            response = await self._llm.ainvoke(messages)
            review_text = response.content.strip()
            
            if review_text.lower() in ["no issues found", "no issues", "looks good", "no comments"]:
                return []
            
            comments = []
            lines = review_text.split("\n")
            for line in lines:
                cleaned = line.strip()
                if cleaned and cleaned not in ["```", "Here are the review comments:", "Comments:", "-"]:
                    if cleaned.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")):
                        comments.append(cleaned.lstrip("-*•123456789. ").strip())
                    elif cleaned:
                        comments.append(cleaned)
            
            return comments
        
        return []

    async def _syntax_check_test(self, test_content: str) -> List[str]:
        errors = []
        
        if not test_content.strip():
            errors.append("Test file is empty")
        
        if "import org.junit.jupiter.api.Test" not in test_content:
            errors.append("Missing JUnit 5 Test import")
        
        if "@Test" not in test_content:
            errors.append("No @Test annotations found")
        
        if "assert" not in test_content.lower():
            errors.append("No assertions found in test methods")
        
        return errors
