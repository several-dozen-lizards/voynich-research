# Phase 7 sources

Naibbe code/glyph tables: Michael A. Greshko (2025), The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext, Cryptologia, https://doi.org/10.1080/01611194.2025.2566408 ; https://github.com/greshko/naibbe-cipher pinned719f2f4c4d1eacf95fabf48381cd84fc6cd94279. Original naibbe.py, not naibbe_v2.py. Original copyright/license/citation text is preserved in author/naibbe.py and author/THIRD_PARTY_NOTICES.md. All copied source/table hashes are in REGISTRATION.json. Pinned source notes are copied to author/PRIOR_SOURCES.md.

Naibbe tables were developed against Voynich statistics. This experiment additionally fits mixture weights and respacing to the training target. They are not blind controls. No claim that adjusted weights/respacing are the exact published procedure; this is a declared family extension with published glyph mappings fixed.

C1: Hildegard, Causae et curae, Kaiser1903 edition, Archive public-domain source. C2: Mattioli, I discorsi, Venice1568, Archive/Getty public-domain source. OCR and original lab normalized source slices are unchanged; full attribution/URLs retained in the original voynich-lab/SOURCES.md. Source-file hashes, fixed source-slice config and normalized plaintext allocation receipts are frozen. OCR is not corrected transcription.

ZL ordinary running text, Currier labels, section labels and original leaf split are existing lab inputs. Their target is previously examined; held-out here means excluded from THIS encoder fit, not never examined historically. Hash the complete source before training fitting; copy only training strings into fitting inputs. Borrowed page map/line word-slot counts are explicit layout conditioning shared across all arms.

C9: unchanged original lab simplified prefix/middle/suffix shuffled cyclic512-cell grille, not a claimed historical Rugg replication. Exact source/hash copied with the measuring instrument. Independent arrangements preserve its inventories; no historical-table identification claim.

Probe references: original lab Phase4 cached ZL baseline Transformer/T1 model (saved seed1729 only) and Phase5 src.probes functions/probes.csv. Original hashes and checkpoints frozen; exact primary-seed replay required. No C11 or C16 material is used.
