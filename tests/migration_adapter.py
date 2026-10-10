"""Offline metadata adapter. No generation, model client or network request."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.tools.java_tools import analyze_java_class

corpus = Path(sys.argv[1])
results = []
for name in ('Ledger', 'TaxService', 'StatusService'):
    path = next(corpus.rglob(name + '.java'))
    before = path.read_bytes()
    data = analyze_java_class.invoke({'path': str(path)})
    results.append({'class': data['name'], 'package': data['package'],
                    'public_methods': sorted(m['name'] for m in data['methods']
                                             if 'public' in m.get('modifiers', [])),
                    'error': data.get('errors') or None})
    assert path.read_bytes() == before, 'Parser changed source'
print(json.dumps(results))
