"""Pre-registration syntax/source binding only; no semantic gate execution."""
import ast,json,unittest,gzip,hashlib
from pathlib import Path

class Engineering(unittest.TestCase):
    def test_module_syntax(self):
        root=Path(__file__).parent
        for name in ['adapter.py','fixtures.py','run.py']:ast.parse((root/name).read_text(encoding='utf-8'))
    def test_acquired_archive_integrity(self):
        root=Path(__file__).parent/'sources';receipt=json.loads((root/'ACQUISITION_SUCCESS.json').read_text())
        raw=(root/'text16e6.evt').read_bytes()
        self.assertEqual(gzip.decompress((root/'text16e6.evt.gz').read_bytes()),raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),receipt['sha256_raw'])

if __name__=='__main__':unittest.main()
