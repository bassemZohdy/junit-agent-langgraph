# Workflow baseline and migration status

The initial remote baseline is `9d3833aa937bc9f094ea44decc62c45ec0c38173`.
This batch retains class-analysis results and full source in generation prompts,
bounds review regeneration and compile-repair attempts, replaces duplicate attempts,
and rejects the empty-test success path. The retry budget supplied at workflow creation
cannot be expanded through input state.

Review receives the retained production source. Its requested JSON comment arrays
are parsed explicitly, including an empty array; unknown response formats remain
issues rather than silent approval. Regeneration receives the previous review's
feedback and uses the project's available libraries instead of forcing JUnit 5,
Spring testing and AssertJ. Actual `compilation_failed` statuses enter the bounded
fix agent. These are workflow regressions, not evidence of generated-test parity.

Offline regressions use fake agents and models. They check bounded failure, successful
routing, source retention, marker annotations and tool function calls. Existing integration
tests retain their behavior checks while using the real tool schema, a temporary accessor
fixture with fields, a real temporary Git repository, the actual state API and distinct
path/SQL/secret validation APIs. Maven metadata now invokes decorated tools correctly.
Permission decisions are logged; getter generation uses Java field declarators.

Install `requirements-test.txt` and run `python -m pytest tests -q` to execute both
pytest functions and unittest cases. Schema types use `typing_extensions.TypedDict`
for the Python 3.11 CI baseline.
`python tests/migration_adapter.py /path/to/corpus` checks the same three original parser
fixtures as other candidate engines without creating a model client.
Passing parser/workflow tests is not generated-test compilation, mutation, cost or speed
evidence. Source-writing tools and full generation/runtime behavior still require
independent safety and consumer acceptance before retirement.

The original local checkout remains unchanged with 24 commits ahead of this baseline
and further unpublished changes. State persistence, transactions/rollback, tools, and
JUnit 4/5 samples are preserved in place and have not been completely migrated.
Keep branch/tag history, visibility, provenance and source rights; missing license files
do not grant redistribution rights. No archive, ref deletion or capability removal occurs
in this batch.
