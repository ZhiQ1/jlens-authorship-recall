# Dreaming Up Authors -- reproduction targets.
#
# Everything under `make all` runs from the artifacts in data/release/. No
# network, no API key, no GPU. The stages that need those are separate targets
# and are documented in README.md as "archived, not regenerable".

PYTHON ?= python
DUA    ?= $(PYTHON) -m dua.cli

# Inputs and outputs for the Section 7 GPU stages (see README.md, Section 7).
PROMPTS_CSV ?= data/interim/probing_prompts_9108.csv
RUNS_ROOT   ?= runs
STEER_OUT   ?= results/position_probe

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --------------------------------------------------------------------------
# setup
# --------------------------------------------------------------------------

# pyproject requires >=3.11,<3.13. The pin is not cosmetic: scikit-learn
# 1.5.2 is what ethnicseer's pickled model expects, and the pinned
# statsmodels/scipy pair has no 3.13+ wheels. A newer interpreter fails at
# `pip install` with a message that does not say which version to use, so
# the version is chosen here rather than inherited from whatever `python` is.
PY_VERSIONS := 3.12 3.11

.PHONY: install
install:  ## Create .venv and install the package with dev extras
	@if command -v uv >/dev/null 2>&1; then \
	  uv venv --python 3.12 .venv || uv venv --python 3.11 .venv; \
	  uv pip install --python .venv -e ".[dev]"; \
	else \
	  interp=""; \
	  for v in $(PY_VERSIONS); do \
	    command -v python$$v >/dev/null 2>&1 && { interp=python$$v; break; }; \
	  done; \
	  if [ -z "$$interp" ]; then \
	    echo "No suitable interpreter found. This package needs Python 3.11 or 3.12"; \
	    echo "(see requires-python in pyproject.toml). Install one, or install uv,"; \
	    echo "which will fetch it: https://docs.astral.sh/uv/"; \
	    exit 1; \
	  fi; \
	  echo "Using $$interp"; \
	  $$interp -m venv .venv; \
	  .venv/bin/python -m pip install -q --upgrade pip; \
	  .venv/bin/python -m pip install -e ".[dev]"; \
	fi
	@echo "Activate with: source .venv/bin/activate"

.PHONY: install-all
install-all:  ## Install every optional extra except probing (which needs torch)
	@if command -v uv >/dev/null 2>&1; then \
	  uv pip install --python .venv -e ".[dev,api,data,ethnicity]"; \
	else \
	  .venv/bin/python -m pip install -e ".[dev,api,data,ethnicity]"; \
	fi

# --------------------------------------------------------------------------
# the reproduction path
# --------------------------------------------------------------------------

.PHONY: all
all: tables figures metrics  ## Regenerate every table, figure, and quoted number

.PHONY: tables figures
tables figures: analysis  ## (both are produced by the same pass)

.PHONY: analysis
analysis:  ## Sections 4-6 and their appendices, from data/release/
	$(DUA) analyse

.PHONY: probing-tables
probing-tables:  ## Appendix A8, from the shipped probing CSVs. No GPU.
	$(DUA) probing-tables

.PHONY: prompt-sensitivity
prompt-sensitivity:  ## Appendix A6.13
	$(DUA) prompt-sensitivity

.PHONY: ethnicity
ethnicity:  ## Appendix A6.10. Needs the `ethnicity` extra; takes ~10 minutes.
	$(DUA) ethnicity

.PHONY: metrics
metrics: analysis probing-tables prompt-sensitivity  ## Collect every quoted number
	$(DUA) metrics

# --------------------------------------------------------------------------
# checking
# --------------------------------------------------------------------------

.PHONY: test
test:  ## Unit tests
	$(PYTHON) -m pytest -q

.PHONY: verify
verify: test  ## Tests, checksums, and cross-artifact invariants
	$(DUA) verify

.PHONY: check-tables
check-tables:  ## Compile every generated table, so \input into the paper is safe
	$(PYTHON) tools/check_tables_compile.py

.PHONY: lint
lint:  ## Style and import checks
	$(PYTHON) -m ruff check src tests tools

.PHONY: checksums
checksums:  ## Rewrite data/release/checksums.sha256 after editing an artifact
	$(PYTHON) tools/build_release.py --checksums-only

.PHONY: clean
clean:  ## Remove generated outputs (never touches data/release/)
	rm -f results/tables/*.tex results/tables/*.json
	rm -f results/figures/*.pdf results/figures/*.png
	rm -f results/metrics/*.json
	rm -rf $(RUNS_ROOT) $(STEER_OUT) $(PROMPTS_CSV)

# --------------------------------------------------------------------------
# stages that reach outside the repository
# --------------------------------------------------------------------------

.PHONY: probing-prompts
probing-prompts:  ## Rebuild the --data_csv every Section 7 GPU stage needs
	$(DUA) probing-prompts --output $(PROMPTS_CSV)

.PHONY: probing-rundir
probing-rundir:  ## Unpack the --run_dir a steering re-run reads
	$(DUA) probing-rundir --out-root $(RUNS_ROOT)

.PHONY: steering-controls
steering-controls: probing-prompts probing-rundir  ## Stage 24. Regenerates Table A25. Needs a GPU.
	@case "$${DUA_MODEL_KEY:?set DUA_MODEL_KEY=qwen3_32b or mistral_small_3_2_24b}" in \
	  qwen3_32b)             layer=48 ;; \
	  mistral_small_3_2_24b) layer=22 ;; \
	  *) echo "unknown DUA_MODEL_KEY: $$DUA_MODEL_KEY" >&2; exit 2 ;; \
	esac; \
	steer="$${DUA_STEER_DIR:-data/release/probing/steering/$$DUA_MODEL_KEY}"; \
	set -x; \
	$(PYTHON) -m dua.probing.stages.stage24_position_probe_steering \
	  --model_path "$${DUA_MODEL:?set DUA_MODEL to the weights, e.g. Qwen/Qwen3-32B}" \
	  --run_dir    "$${DUA_RUN_DIR:-$(RUNS_ROOT)/$$DUA_MODEL_KEY}" \
	  --data_csv   $(PROMPTS_CSV) \
	  --meta_json  "$$steer/steering_meta.json" \
	  --layer      "$${DUA_LAYER:-$$layer}" \
	  --vectors    "diff_of_means=$$steer/steering_vector.npy" \
	               "probe=$$steer/probe_direction.npy" \
	  --norm_match_to diff_of_means \
	  --positions  all p1_and_gen prompt_only \
	  --pool_mode  eval_high --n_eval 50 --n_random_seeds 5 --alpha 2.0 --seed 42 \
	  --out_dir    "$${DUA_OUT_DIR:-$(STEER_OUT)/$$DUA_MODEL_KEY}"

.PHONY: check-steering-controls
check-steering-controls:  ## Diff a Stage 24 re-run against the shipped artifact
	$(PYTHON) tools/check_steering_controls.py \
	  "$${DUA_OUT_DIR:-$(STEER_OUT)/$${DUA_MODEL_KEY:?set DUA_MODEL_KEY}}"

.PHONY: corpus-filter
corpus-filter:  ## Stage A. Needs the 10M OAG pool; set DUA_OAG_POOL.
	$(DUA) filter --corpus "$${DUA_OAG_POOL:?set DUA_OAG_POOL to the OAG sample}"

.PHONY: distributions
distributions:  ## Section 2.2 tables. Needs the 1.92M corpus; set DUA_CORPUS.
	$(DUA) distributions

.PHONY: resample
resample:  ## Stage B. Needs the 1.92M corpus; set DUA_CORPUS.
	$(DUA) sample --corpus "$${DUA_CORPUS:?set DUA_CORPUS to the curated corpus}" \
	  --verify-against data/release/eval_sample_9108.csv.gz

.PHONY: collect
collect:  ## Stage D. Needs OPENAI_API_KEY or OPENROUTER_API_KEY.
	$(DUA) collect --model $${MODEL:-gpt-4o} --output data/interim/$${MODEL:-gpt-4o}.ndjson

.PHONY: recognise-build
recognise-build:  ## Build and verify MC items without querying a model
	$(DUA) recognise --mode $${MODE:-random_field} --build-only

.PHONY: recognise
recognise:  ## Section 6. Needs OPENAI_API_KEY.
	$(DUA) recognise --mode $${MODE:-random_field} \
	  --output data/interim/mc_$${MODE:-random_field}.ndjson
