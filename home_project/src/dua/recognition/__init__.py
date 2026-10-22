"""Section 6 / Appendix A7: multiple-choice recognition.

Not byte-identical to the paper. This package was reimplemented from the
appendix description, since no code for Section 6 existed in either original
source tree. It meets every integrity check the appendix states, but
distractor sampling is seeded differently from the original run, GPT-4o at
temperature 0 is not deterministic, and the collaborator-swap control reads
Semantic Scholar records that drift. Expect numbers close to the paper's, not
equal to them. The recall side of the gap comes from the shipped responses and
is exact.
"""

from dua.recognition.analyze import chance_corrected, gap_by_bin, merge_with_recall
from dua.recognition.distractors import DistractorBuilder, MCItem, build_field_pools

__all__ = ["DistractorBuilder", "MCItem", "build_field_pools", "chance_corrected",
           "gap_by_bin", "merge_with_recall"]
