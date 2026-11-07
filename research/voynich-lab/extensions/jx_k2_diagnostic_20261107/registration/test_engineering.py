"""Pre-registration engineering only. Adapter semantic fixtures run after registration."""
import unittest,ast
from pathlib import Path

class Engineering(unittest.TestCase):
    def test_module_syntax_without_import_or_adapter_execution(self):
        root=Path(__file__).resolve().parent
        tree=ast.parse((root/'diagnostic.py').read_text(encoding='utf-8'))
        funcs={n.name for n in tree.body if isinstance(n,ast.FunctionDef)}
        self.assertTrue({'register','gate_adapter','decomposition','verify','run'}.issubset(funcs))
    def test_authority_is_bound_primary_source_findings(self):
        import json
        a=json.loads((Path(__file__).parent/'authority.json').read_text())
        self.assertEqual(len(a['sources']),2)
        self.assertTrue(all(s['url'].startswith('https://www.voynich.nu/') for s in a['sources']))

if __name__=='__main__':unittest.main()
