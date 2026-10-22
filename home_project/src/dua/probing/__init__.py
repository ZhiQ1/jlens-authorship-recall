"""Section 7 / Appendix A8: hidden-state probing and activation steering.

Two halves, with very different requirements:

* ``dua.probing.stages`` runs open-weight models on a GPU to extract hidden
  states, fit probes, and apply activation steering. Needs weights, a GPU, and
  tens of gigabytes of scratch. See ``README.md``.
* ``dua.probing.tables`` turns the resulting CSVs -- shipped in
  ``data/release/probing/`` -- into the appendix tables and figures. Needs
  neither.
"""
