import asyncio
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from src.agents.class_analysis import ClassAnalysisAgent
from src.agents.generate_test import GenerateTestAgent
from src.agents.validate_test import ValidateTestAgent
from src.agents.review_test import ReviewTestAgent
from src.tools.java_tools import analyze_java_class
from src.graphs import workflow


class WorkflowTests(unittest.TestCase):
    def test_analysis_retains_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Ledger.java'
            source = 'public class Ledger { public int total() { return 2; } }'
            path.write_text(source, encoding='utf-8')
            result = asyncio.run(ClassAnalysisAgent().process(
                {'current_class': {'name': 'Ledger', 'file_path': str(path)}}))
            self.assertEqual(source, result['current_class']['content'])
            self.assertEqual('total', result['current_class']['methods'][0]['name'])
            self.assertEqual('analyzed', result['current_class']['status'])

    def test_generator_receives_source(self):
        llm = SimpleNamespace(ainvoke=AsyncMock(return_value=SimpleNamespace(content='class LedgerTest {}')))
        agent = GenerateTestAgent(llm)
        asyncio.run(agent._generate_test_content('Ledger', 'SOURCE_SENTINEL', [], []))
        messages = llm.ainvoke.call_args.args[0]
        self.assertIn('SOURCE_SENTINEL', messages[-1].content)

    def test_marker_annotation_preserves_primary_class(self):
        data = analyze_java_class.invoke({'source_code':
                 'package fixture; @Deprecated public class Ledger { public int total() { return 2; } }'})
        self.assertEqual('analyzed', data['status'])
        self.assertEqual('fixture', data['package'])
        self.assertEqual('total', data['methods'][0]['name'])

    def test_validator_writes_through_function_api(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'LedgerTest.java'
            result = asyncio.run(ValidateTestAgent()._write_test_file(str(path), 'class LedgerTest {}'))
            self.assertTrue(result['success'])
            self.assertEqual('class LedgerTest {}', path.read_text())

    def invoke_stubbed(self, *, reviews_fail=False, validation_fail=False, empty=False, retries=1, failure_status='failed'):
        classes = [] if empty else [{'name': 'Ledger', 'file_path': 'Ledger.java'}]
        analyze = AsyncMock(return_value={'java_classes': classes})
        enrich = AsyncMock(side_effect=lambda state: {'current_class':
                            {**state['current_class'], 'content': 'ENRICHED'}})
        generated = []

        async def generate(state):
            self.assertEqual('ENRICHED', state['current_class']['content'])
            if reviews_fail and generated:
                self.assertEqual(['Use existing dependencies'],state['review_feedback'])
            generated.append(1)
            return {'test_classes': [{'name': 'LedgerTest', 'status': 'generated'}]}

        review = AsyncMock(side_effect=lambda state: {'test_classes':
                            [{**state['test_classes'][0], 'status': 'needs_fixes' if reviews_fail else 'reviewed',
                              'review_comments': ['Use existing dependencies'] if reviews_fail else []}]})
        validate = AsyncMock(side_effect=lambda state: {'test_classes':
                            [{**state['test_classes'][0], 'status': failure_status if validation_fail else 'passed'}]})
        fix = AsyncMock(side_effect=lambda state: {'test_classes': state['test_classes']})
        project = AsyncMock(return_value={'build_status': 'passed'})
        mocks = [analyze, enrich, generate, review, validate, fix, project]
        names = ['AnalyzeProjectAgent', 'ClassAnalysisAgent', 'GenerateTestAgent', 'ReviewTestAgent',
                 'ValidateTestAgent', 'FixTestAgent', 'ProjectValidatorAgent']
        from contextlib import ExitStack
        with ExitStack() as stack:
            for name, process in zip(names, mocks):
                stack.enter_context(patch.object(workflow, name, return_value=SimpleNamespace(process=process)))
            graph = workflow.create_test_generation_workflow(llm=object(), max_retries=retries)
            result = asyncio.run(graph.ainvoke({'project_path': '.', 'max_retries': 999},
                                               {'recursion_limit': 40}))
        return result, generated, fix, project

    def test_persistent_review_failure_is_bounded_without_duplicates(self):
        result, generated, _, project = self.invoke_stubbed(reviews_fail=True)
        self.assertEqual('failed', result['build_status'])
        self.assertEqual(2, len(generated))
        self.assertEqual(1, len(result['test_classes']))
        project.assert_not_awaited()

    def test_compiler_retry_limit_cannot_be_overridden_by_state(self):
        result, _, fix, project = self.invoke_stubbed(validation_fail=True)
        self.assertEqual('failed', result['build_status'])
        self.assertEqual(1, fix.await_count)
        project.assert_not_awaited()

    def test_compilation_failure_reaches_the_bounded_fix_agent(self):
        result, _, fix, project = self.invoke_stubbed(validation_fail=True,failure_status='compilation_failed')
        self.assertEqual('failed',result['build_status'])
        fix.assert_awaited_once()
        project.assert_not_awaited()

    def test_reviewer_receives_source_and_empty_array_means_no_issues(self):
        llm = SimpleNamespace(ainvoke=AsyncMock(return_value=SimpleNamespace(content='[]')))
        result = asyncio.run(ReviewTestAgent(llm).process({'java_classes':[
            {'name':'Ledger','content':'PRODUCTION_SOURCE_SENTINEL'}], 'test_classes':[
            {'name':'LedgerTest','target_class':'Ledger','content':'class LedgerTest {}'}]}))
        self.assertIn('PRODUCTION_SOURCE_SENTINEL',llm.ainvoke.call_args.args[0][-1].content)
        self.assertEqual('reviewed',result['test_classes'][0]['status'])
        self.assertEqual([],result['test_classes'][0]['review_comments'])

    def test_structured_reviews_retain_issues_and_handle_fenced_empty_arrays(self):
        for text,expected in (('["Wrong assertion"]',['Wrong assertion']),('```json\n[]\n```',[])):
            llm = SimpleNamespace(ainvoke=AsyncMock(return_value=SimpleNamespace(content=text)))
            result = asyncio.run(ReviewTestAgent(llm)._review_test_code({'name':'LedgerTest','content':'TEST'}))
            self.assertEqual(expected,result)

    def test_unrecognized_review_format_is_not_silent_approval(self):
        for text in ('[','{"status":"passed"}','[null]'):
            llm = SimpleNamespace(ainvoke=AsyncMock(return_value=SimpleNamespace(content=text)))
            result = asyncio.run(ReviewTestAgent(llm)._review_test_code({'name':'LedgerTest','content':'TEST'}))
            self.assertTrue(result)

    def test_generator_receives_previous_review_feedback(self):
        llm = SimpleNamespace(ainvoke=AsyncMock(return_value=SimpleNamespace(content='class LedgerTest {}')))
        asyncio.run(GenerateTestAgent(llm)._generate_test_content('Ledger','SOURCE',[],[],['REPAIR_SENTINEL']))
        self.assertIn('REPAIR_SENTINEL',llm.ainvoke.call_args.args[0][-1].content)

    def test_empty_tests_fail(self):
        result, _, _, project = self.invoke_stubbed(empty=True)
        self.assertEqual('failed', result['build_status'])
        project.assert_not_awaited()

    def test_passed_tests_reach_project_validation(self):
        result, _, _, project = self.invoke_stubbed()
        self.assertEqual('passed', result['build_status'])
        project.assert_awaited_once()

    def test_bad_retry_limit_is_rejected(self):
        for retries in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                workflow.create_test_generation_workflow(llm=object(), max_retries=retries)


if __name__ == '__main__':
    unittest.main()
