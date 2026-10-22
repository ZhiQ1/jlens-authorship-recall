"""Stage C: citation count as a proxy for factual prevalence (Section 3)."""

from dua.proxy.google_hits import GoogleHitsClient
from dua.proxy.google_hits import build_query as build_google_query
from dua.proxy.infinigram import InfiniGramClient
from dua.proxy.infinigram import build_query as build_infinigram_query

__all__ = ["GoogleHitsClient", "InfiniGramClient", "build_google_query",
           "build_infinigram_query"]
