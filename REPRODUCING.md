# Reproduction and archive verification

This snapshot did not rerun historical analyses, retrain models, consume a statistical budget, or open a held-out scoring gate. Existing verification receipts are historical evidence, not freshly passing tests for this export.

To restore copied artifacts to their original relative filenames, run `python tools/unpack_research.py <new-directory>`. It writes only to a separate new or empty directory, verifies restored SHA-256 values, and does not run research code. Restoration can require substantially more disk space than the stored archive. Excluded inputs remain excluded.

Run `python tools/verify_archive.py` from the repository root to verify every copied research artifact against its manifest, including gzip/XZ integrity, original and published SHA-256, and Git blob identity. This uses Python's standard library and does not run research code.

Files larger than 1,000,000 bytes are stored with `.gz` appended; the largest table uses `.xz` to fit GitHub's individual-file limit. For reproduction, unpack them to a separate working copy with the original relative path. Use the original study's README, protocol, environment and source receipt. Many pipelines require external corpora, specific environments, or source intake that is intentionally not redistributed here. Do not treat a missing input as authorization to reacquire a closed reserve, alter a freeze, or score a withheld arm.

Older reports and scripts may retain links to a filename without the added `.gz`. The generated catalogue and manifest resolve the stored location. HTML reports and JavaScript dashboards are archival assets; GitHub's file viewer will not execute them. The archive's generated landing-page links are checked separately from every historical reference.

Check `catalog/SNAPSHOT.json` for observed changes between inventory and copy. Each copied file was checked for changes during its own read; this does not assert an atomic filesystem-wide snapshot of concurrent research.
