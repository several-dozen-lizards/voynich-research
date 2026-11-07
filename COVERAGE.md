# Coverage and exclusions

This is an inventory-backed snapshot of the local Voynich workspace. It is not a claim that all historical conversations and external attachments have been recovered.

Every file in the input inventory is assigned a disposition in `catalog/FILES.csv` and `catalog/FILES.json`. Published paths point to exact copies, or gzip/XZ streams retaining exact original bytes. Excluded entries retain their original path and byte count; no checksum is claimed for contents that were not read. The scanned-directory exclusions are listed in `catalog/SNAPSHOT.json`.

## Dispositions

- `publish`: code, reports, checks, protocols, source ledgers and result artifacts accepted by the documented selection rule and credential-pattern scan.
- `third-party-source-review`: imported corpora, raw transcriptions and source directories. Their provenance records elsewhere remain available. Public availability does not establish permission to redistribute.
- `third-party-media-review`: PDF, manuscript/source images and fonts requiring individual rights attribution/review.
- `custody-or-blinding-review`: paths designated private, vault, registrar-only, rater-only, packets, sealed or human-registration. Publication must not silently expose a reserve or invalidate independent registration.
- `model-or-binary-data`: model checkpoints and binary arrays. Existing published weights have a separate repository. Other weights/arrays remain local and indexed.
- `nested-archive-review`: compressed packages that could duplicate or conceal the above material. They remain indexed; any unpacked publishable originals are handled separately.
- `dependency-or-cache`: installed dependencies, caches and environment material.
- `unclassified-review`, `credential-pattern-review`, `copy-error`: unresolved material retained in the ledger rather than silently published.

Directory/name rules are conservative triage, not an individual legal or custody determination. A report can describe an excluded dataset without making that dataset available. `catalog/SNAPSHOT.json` records counts, source-stat changes, and errors. This archive does not certify historical blinding or restore an exposed holdout.

## Known gaps

The original running chronology is not current for all lab extensions. Historical references can name external attachments or older chats not retained here. Review all local source records before claiming exhaustive bibliography or successful reproduction. A URL extracted from code may be a template, example, or failed retrieval; it is not automatically a consulted source.

The archive copies the currently retained state. It does not reconstruct deleted files or invent Git history. The earlier source tree remains untouched. Original scripts may contain machine-specific paths or expect excluded datasets and will require the recorded source intake and environment.
