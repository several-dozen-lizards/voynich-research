# Decisions frozen before fitting

- User Phase7 request explicitly authorizes this new C15/Naibbe-family training/held-out experiment. C12 terminal closure remains unchanged; C16-KH qualification/scoring holds remain closed.
- Fit the published Naibbe table-mixture weights and respacing, not arbitrary glyph strings, language-specific plaintext transformations, learned abbreviations or table permutations chosen after outcomes. Search family and standardization declared in PROTOCOL.md.
- Fix Transformer/T1 for all probes because that is the original instrument producing the referenced94.02% ZL A/B result. Keep source/config/probe functions unchanged. Do not select different instruments according to held-out accuracy.
- Fit separate A/B settings and a pooled single setting independently for each plaintext language. Italian is a replication of the procedure, not a second plaintext language mixed into a single corpus. C9 has no plaintext language and is reported once.
- Single-table null receives the same78-candidate training search; two-table C9 receives the same78-arrangement search with the original inventories. Also report its pooled single-arrangement reference. This extra reference changes no generator settings or selector.
- Keep all original pages for section-probe comparability. Unknown A/B pages use the pooled setting; exclude them from A/B fingerprints/probes. No inferred labels. A/B-conditioned section baseline and within-A/B probes diagnose inherited map confounding without changing the primary section score.
- Fixed disjoint2*N source-character chunks per page allow exact ciphertext word-slot layout and consistent plaintext across arms without repetition or held-out-source overlap. Discard unused suffixes explicitly; log all spans.
- Clean-only primary experiment; no added noise grid. Approximate94% and section-near-baseline are descriptive references, not thresholds optimized or retrofitted into pass/fail gates.

- Pre-registration checkpoint preflight: only original ZL seed1729 has saved weights. Use it as a fixed reference; five paired seeds apply to controls. Do not estimate ZL model-seed variation from unavailable weights. Preserve the failed setup attempts.
