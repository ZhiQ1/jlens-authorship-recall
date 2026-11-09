# Addendum 12 items 2-7 / 2-9: patchscope with the source at the name positions; x4tok at every layer

**ONE-SHARD GATE (--partial): shards 0.**
Plan `381_stage13/config/prereg_addendum12.json` (sha256 c97533d5...). Papers: 50 (tune 17, test 33). D = mean score(self source) - mean score(partner source), log10(1/rank) of the answer tokens at the output; 95% team-cluster bootstrap; * = CI excludes 0.

- Per-paper published raw/pscope values (title + colon + none, 4350 cells): max |diff| 4.44e-16, exact share 1.0000.
- HARD 2-7 title-source D vs published (63 cells): max |diff| 7.83e-17 (tol 0.005) -> PASS.
- WARN-only 2-7 colon-source D vs published (63 cells): max |diff| 8.49e-17 (tol 0.005) -> PASS.
- HARD 2-7 named value (test, first author, title, L8): +0.0130 vs +0.0130 -> PASS.
- HARD 2-9 x4tok (title source, L8/L40) vs published (8 cells): max |diff| 4.16e-17 -> PASS; n equal -> PASS.
- Hard checks: **PASS**

