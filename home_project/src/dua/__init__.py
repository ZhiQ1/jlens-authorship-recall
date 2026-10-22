"""Dreaming Up Authors: factual prevalence and LLM hallucinations in
academic authorship attribution.

Package layout mirrors the pipeline stages described in README.md:

    dua.data         Stage A  corpus construction and filtering
    dua.sampling     Stage B  the 9,108-paper stratified evaluation sample
    dua.proxy        Stage C  Google hits and Infini-gram prevalence proxies
    dua.collect      Stage D  LLM response collection
    dua.evaluate     Stage E  name matching and hallucination metrics
    dua.recognition  Stage F  multiple-choice recognition (Section 6)
    dua.probing      Stage G  hidden-state probing and steering (Section 7)
    dua.analysis     Stage H  every table and figure in the paper
"""

__version__ = "1.0.0"
