# Stage 7.3A frozen title controls

50 targets × 20 shuffles = 1000 title contexts.

Tier counts: {0: 334, 1: 487, 2: 179}

Cross-pool source-author overlaps: 199.

- All 20 shuffles are selected by metadata only; scored outputs were not read
- Same original target year retained in all shuffled prompts; source title year may differ
- Author overlap is checked against target paper authors by normalized name strings, not external registry
- Matched title source may have a real author included in frozen false candidates; flagged, not hidden
- Repeated source title use across distinct target papers is allowed; dependent null contexts require care
