from typing import List
import json
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
        
        target = latest_test.get('target_class') or latest_test['name'].removesuffix('Test')
        source = next((item.get('content','') for item in state.get('java_classes',[])
                       if item.get('name')==target),'')
        review_comments = await self._review_test_code(latest_test,source)
        
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

    async def _review_test_code(self, test_class: dict, source_content: str = '') -> List[str]:
        test_name = test_class.get("name", "")
        test_content = test_class.get("content", "")
        
        if not test_content:
            return ["Test content is empty"]
        
        system_prompt = """You are a senior code reviewer specialized in Java testing best practices.
Review the provided test code for:
1. Code quality and readability
2. Proper use of the candidate's actual JUnit version and available dependencies
3. Test coverage and completeness
4. Mock usage and dependency injection
5. Assertion quality and accuracy
6. Naming conventions
7. Potential bugs or anti-patterns
8. Performance considerations
9. Security best practices
10. Maintainability

Preserve production code and POMs. Do not require unavailable libraries or invent
source behavior. Return only a JSON array of actionable defects, or [] if none."""

        user_prompt = f"""Review the following test class:

Test Class Name: {test_name}

Production Source:
{source_content or 'Not provided; do not assume implementation behavior.'}

Test Code:
{test_content}

Return a JSON array of specific comments. If there are no actionable defects, return []."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        if self._llm:
            response = await self._llm.ainvoke(messages)
            review_text = response.content.strip()
            structured = review_text
            if structured.startswith('```') and structured.endswith('```'):
                structured = '\n'.join(structured.splitlines()[1:-1]).strip()
            try:
                comments = json.loads(structured)
                if isinstance(comments,list) and all(isinstance(item,str) for item in comments):
                    return comments
            except (ValueError,TypeError):
                pass
            
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
