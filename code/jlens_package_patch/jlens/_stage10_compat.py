"""Compat shim for jlens_work Stage 10 (2026-10-24), active only when the running script is 351_stage10.py.

transformers 5.x does not set `hf_device_map` on a model loaded whole onto one GPU, and the frozen Stage 10 script
reads it after from_pretrained. Jobs already queued run that frozen script unchanged, so this gives the attribute a
fallback (the set of devices holding parameters/buffers) instead. A real hf_device_map, when transformers sets one,
lives in the instance dict and wins. Other programs never see this.
"""
import os
import sys


def _install():
    if not os.path.basename(sys.argv[0] if sys.argv else '').startswith('351_stage10'):
        return
    try:
        from transformers.modeling_utils import PreTrainedModel
    except Exception:
        return
    if 'hf_device_map' in PreTrainedModel.__dict__:
        return

    class _Fallback:  # non-data descriptor: instance attribute (set by a real dispatch) takes precedence
        def __get__(self, obj, owner=None):
            if obj is None:
                return self
            devs = sorted({str(t.device) for t in [*obj.parameters(), *obj.buffers()]})
            return {f'_device{i}': d for i, d in enumerate(devs)}

    PreTrainedModel.hf_device_map = _Fallback()


_install()
