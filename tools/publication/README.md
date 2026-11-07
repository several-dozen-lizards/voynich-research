# Publication build provenance

These are the scripts used to inventory, select, copy and organize this archive. They expect the original workspace layout: `github-export/research-archive-tools/` beside `github-export/voynich-research/`. They are retained for inspection, not as an instruction to rebuild into a live research tree.

`inventory.py` enumerates in-scope files. `prepare.py` applies the documented exclusions, scans copied bytes for credential-shaped patterns, writes resumable copy accounting, compresses large files losslessly, and builds the indexes. `finish.py` adds thematic navigation and moves undeclared staging leftovers to a separate local quarantine. Original experiment files are not moved or edited.

The input inventory is a filesystem listing, not a complete historical provenance ledger. URL extraction considers copied text files up to 10,000,000 bytes; larger files remain fully preserved where publishable and are not automatically treated as bibliographic records. URLs can be examples or failed retrievals. Source records must be read in context.

Run the portable `../verify_archive.py` from this repository to verify export integrity. The export verification receipt is distinct from every historical experiment receipt.
