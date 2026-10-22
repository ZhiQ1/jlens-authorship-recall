"""Command-line entry point.

One command per pipeline stage, so a reviewer can go from a fresh clone to
every table and figure without reading any Python:

    dua verify                     # tests + checksums + the invariants below
    dua analyse                    # every table and figure from data/release/
    dua evaluate  <input> <output> # re-score raw LLM answers
    dua sample    --corpus PATH    # redraw the 9,108-paper evaluation sample
    dua filter    --corpus PATH    # run the five-stage quality filter
    dua distributions              # Section 2.2 corpus statistics
    dua collect   --model gpt-4o   # query a model (needs an API key)
    dua recognise --model gpt-4o --analyse   # multiple-choice experiment + tables
    dua metrics                    # collect every quoted number into one JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--seed", type=int, default=None,
                        help="override the seed in config/config.yaml")


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def cmd_analyse(args) -> int:
    from dua.analysis import (
        author_count,
        eval_agreement,
        hr_decomposition,
        position,
        regression,
        results,
        stratum_stability,
        title_length,
    )

    modules = {
        "results": results, "hr_decomposition": hr_decomposition,
        "eval_agreement": eval_agreement, "position": position,
        "author_count": author_count, "title_length": title_length,
        "regression": regression, "stratum_stability": stratum_stability,
    }
    if args.only:
        unknown = set(args.only) - set(modules)
        if unknown:
            print(f"unknown analysis: {sorted(unknown)}", file=sys.stderr)
            print(f"available: {sorted(modules)}", file=sys.stderr)
            return 2
        modules = {k: modules[k] for k in args.only}

    for name, module in modules.items():
        print(f"[{name}]", flush=True)
        module.run_all()
    print("\nWrote tables to results/tables/, figures to results/figures/, "
          "values to results/metrics/.")
    return 0


def cmd_probing_tables(args) -> int:
    from dua.probing import tables

    tables.run_all()
    print("Wrote Appendix A8 tables and figures.")
    return 0


def cmd_prompt_sensitivity(args) -> int:
    from dua.analysis import prompt_sensitivity

    prompt_sensitivity.run_all()
    print("Wrote Appendix A6.13 tables.")
    return 0


def cmd_ethnicity(args) -> int:
    from dua.analysis import ethnicity

    out = ethnicity.run_all()
    for model, modes in out["models"].items():
        print(f"{model:20s} population V={modes['population']['cramers_v']:.3f} "
              f"diversity V={modes['diversity']['cramers_v']:.3f}")
    return 0


def cmd_evaluate(args) -> int:
    from dua.evaluate import Evaluator
    from dua.io import read_csv_rows, read_ndjson, write_csv_rows

    source = Path(args.input)
    reader = read_ndjson if source.suffix in (".ndjson", ".jsonl") else read_csv_rows
    evaluator = Evaluator(match_level_threshold=args.match_level_threshold)

    def scored():
        for record in reader(source):
            record.update(evaluator.evaluate_record(record).as_columns())
            yield record

    n = write_csv_rows(args.output, scored())
    print(f"Scored {n:,} records -> {args.output}")
    return 0


def cmd_sample(args) -> int:
    from dua.io import write_csv_rows, write_json
    from dua.sampling import draw

    rows, report = draw(args.corpus, per_stratum=args.per_stratum, seed=args.seed)
    write_csv_rows(args.output, rows)
    write_json(Path(args.output).with_suffix(".report.json"), report, seed=report["seed"])
    print(f"Drew {report['n_selected']:,} papers across "
          f"{report['n_populated_strata']} populated strata "
          f"(theoretical maximum {report['theoretical_max']:,}).")
    if args.verify_against:
        from dua.sampling import verify_against

        print(json.dumps(verify_against(rows, args.verify_against), indent=2))
    return 0


def cmd_filter(args) -> int:
    from dua.data import filter_corpus

    summary = filter_corpus(args.corpus, args.output, args.funnel, limit=args.limit)
    if not summary["language_model_loaded"]:
        print("WARNING: no FastText model found, so the language filter passed "
              "everything through. Retention will not match the paper. See "
              "README.md.", file=sys.stderr)
    for stage in summary["stages"]:
        print(f"  {stage['stage']:24s} {stage['in']:>10,} -> {stage['out']:>10,} "
              f"({stage['pct_removed']:>5.1f}% removed)")
    print(f"  {'TOTAL':24s} {summary['initial']:>10,} -> {summary['final']:>10,} "
          f"({summary['retention_pct']}% retained)")
    return 0


def cmd_distributions(args) -> int:
    from dua.data import distributions

    summary = distributions.run(args.corpus, limit=args.limit)
    print(f"{summary['n_papers']:,} papers | mean citations "
          f"{summary['mean_citations']:.1f}, median {summary['median_citations']:.0f} | "
          f"mean authors {summary['mean_authors']:.2f} | "
          f"{summary['n_disciplines']} disciplines, eight fields cover "
          f"{summary['eight_field_coverage_pct']:.2f}%")
    return 0


def _require_api_key(model_key: str, group: str) -> None:
    """Check the key before doing work that will be thrown away without it.

    Building the multiple-choice items takes about a minute over 9,108 papers.
    The key was only read at the first request, so a reviewer without one
    waited for that build to finish before being told. Touch the property up
    front instead; it raises MissingAPIKeyError, which main() reports cleanly.
    """
    from dua.collect.client import ChatClient
    from dua.config import load_models

    models = load_models()
    spec = models[group].get(model_key)
    if spec is None:
        return  # unknown key: let the command's own lookup raise the better error
    _ = ChatClient(spec["access"]).api_key  # raises MissingAPIKeyError


def cmd_collect(args) -> int:
    from dua.analysis.loaders import load_sample
    from dua.collect.authorship import collect

    _require_api_key(args.model, "behavioral")
    papers = load_sample().to_dict("records")
    n = 0
    for _ in collect(papers, args.model, args.output, limit=args.limit):
        n += 1
        if n % 100 == 0:
            print(f"  {n:,} collected", flush=True)
    print(f"Collected {n:,} responses -> {args.output}")
    return 0


def cmd_recognise(args) -> int:
    from dua.analysis.loaders import load_sample
    from dua.recognition.distractors import verify_items
    from dua.recognition.run import build_items, run

    if not args.build_only:
        _require_api_key(args.model, "recognition")
    papers = load_sample().to_dict("records")
    collaborators = None
    if args.mode == "collaborator_swap":
        from dua.config import load_config
        from dua.recognition.collaborators import CollaboratorIndex, coverage

        index = CollaboratorIndex(load_config().path("cache") / "collaborators")
        first_authors = [p["authors"][0] for p in papers if p["authors"]]
        collaborators = index.build(first_authors, offline=args.offline)
        print(json.dumps(coverage(collaborators), indent=2))

    items = build_items(papers, args.mode, collaborators)
    print(json.dumps(verify_items(items), indent=2))
    if args.build_only:
        return 0

    n = 0
    for _ in run(items, args.output, model_key=args.model):
        n += 1
        if n % 100 == 0:
            print(f"  {n:,} answered", flush=True)
    print(f"Answered {n:,} items -> {args.output}")

    if args.analyse:
        return cmd_recognition_tables(
            argparse.Namespace(results={args.mode: args.output}, model="gpt-4o"))
    print("Now run: dua recognition-tables --results "
          f"{args.mode}={args.output}")
    return 0


def cmd_recognition_tables(args) -> int:
    """Turn scored multiple-choice runs into the Section 6 tables and figures."""
    import pandas as pd

    from dua.recognition.analyze import merge_with_recall, run_all

    runs = {}
    for spec in (args.results.items() if isinstance(args.results, dict)
                 else (s.split("=", 1) for s in args.results)):
        mode, path = spec
        path = Path(path)
        if not path.exists():
            print(f"{path} not found", file=sys.stderr)
            return 2
        frame = (pd.read_json(path, lines=True) if path.suffix in (".ndjson", ".jsonl")
                 else pd.read_csv(path))
        runs[mode] = merge_with_recall(frame)
        print(f"  {mode:20s} {len(runs[mode]):,} scored items")

    out = run_all(runs)
    overall = out["full_results"]["overall"]
    print(f"MC accuracy {overall['mc_accuracy_raw']:.3f} raw, "
          f"{overall['mc_accuracy_cc']:.3f} chance-corrected; "
          f"recall {overall['recall_accuracy']:.3f}")
    return 0


def cmd_proxy(args) -> int:
    """Stage C: collect or analyse the prevalence proxies (Section 3)."""
    import pandas as pd

    from dua.analysis.loaders import load_sample
    from dua.config import load_config
    from dua.proxy import analyze, google_hits, infinigram, subsample

    if args.action == "sample":
        from dua.io import write_csv_rows, write_json

        rows, report = subsample.draw(args.corpus)
        write_csv_rows(args.output, rows)
        write_json(Path(args.output).with_suffix(".report.json"), report)
        print(f"Drew {report['n_selected']:,} papers, target {report['target_per_bin']}/bin")
        return 0

    papers = (pd.read_csv(args.papers).to_dict("records") if args.papers
              else load_sample().to_dict("records"))
    for paper in papers:
        if isinstance(paper.get("authors"), str):
            paper["authors"] = json.loads(paper["authors"])

    def _write(rows, out, source: str, key: str) -> int:
        """Write a proxy collection, and say so plainly when it is empty.

        Offline runs against an empty cache used to write an all-null CSV and
        exit 0, which then fed `analyse` a frame of NaNs. This repository ships
        no proxy cache -- none was found on the machine the release was built
        from -- so that is the *expected* path for anyone following README, and
        it should say what is missing rather than fail three steps later.
        """
        found = sum(1 for r in rows if r[key] is not None)
        print(f"{source}: {found:,} of {len(rows):,} queries resolved"
              f"{' from cache' if args.offline else ''}", flush=True)
        if args.offline and not found:
            print(f"\nNothing resolved: the {source} cache is empty. This repository "
                  f"ships no proxy cache.\nDrop the cached responses into "
                  f"{load_config().path('cache')} and re-run, "
                  f"or\nrerun without --offline and an API key to collect them.",
                  file=sys.stderr)
            return 1
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(out, index=False)
        return 0

    if args.action in ("google", "both"):
        rc = _write(list(google_hits.collect(papers, offline=args.offline)),
                    args.google_out, "google", "hits")
        if rc:
            return rc

    if args.action in ("infinigram", "both"):
        rc = _write(list(infinigram.collect(papers, offline=args.offline)),
                    args.infinigram_out, "infinigram", "count")
        if rc:
            return rc

    if args.action == "analyse":
        absent = [p for p in (args.google_out, args.infinigram_out) if not Path(p).exists()]
        if absent:
            print(f"Missing proxy collections: {', '.join(absent)}\n"
                  f"Produce them with `dua proxy both` (needs API keys) or "
                  f"`dua proxy both --offline`\n(needs a cached proxy response set, which "
                  f"this repository does not ship).", file=sys.stderr)
            return 2
        google = pd.read_csv(args.google_out)
        infini = pd.read_csv(args.infinigram_out)
        report = analyze.run_all(google, infini)
        print(f"outlier filter: {report['outlier_filter']['n_before']:,} -> "
              f"{report['outlier_filter']['n_after']:,} papers")
    return 0


def cmd_probing_prompts(args) -> int:
    """Rebuild the --data_csv the GPU stages take, from the released sample."""
    from dua.config import load_config
    from dua.probing.prompts import build_prompt_csv

    sample = args.sample or (load_config().path("release") / "eval_sample_9108.csv.gz")
    n = build_prompt_csv(Path(sample), Path(args.output))
    print(f"Wrote {n} prompts to {args.output}")
    return 0


def cmd_probing_rundir(args) -> int:
    """Unpack the per-paper scores a steering re-run reads as --run_dir."""
    from dua.config import load_config
    from dua.probing.rundir import MODELS, materialize_run_dir

    release = load_config().path("release")
    models = [args.model] if args.model else list(MODELS)
    for model in models:
        dst = materialize_run_dir(release, model, Path(args.out_root) / model)
        print(f"Wrote {dst}")
    return 0


def cmd_metrics(args) -> int:
    from dua.metrics_report import build

    path = build()
    print(f"Wrote {path}")
    return 0


def cmd_verify(args) -> int:
    from dua.verify import run_all

    report = run_all(strict=not args.no_strict)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dua", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("analyse", aliases=["analyze"],
                       help="regenerate every table and figure from data/release/")
    p.add_argument("--only", nargs="+", help="run only these analyses")
    p.set_defaults(func=cmd_analyse)

    p = sub.add_parser("probing-tables", help="Appendix A8 tables (no GPU needed)")
    p.set_defaults(func=cmd_probing_tables)

    p = sub.add_parser("prompt-sensitivity", help="Appendix A6.13 tables")
    p.set_defaults(func=cmd_prompt_sensitivity)

    p = sub.add_parser("ethnicity", help="Appendix A6.10 (needs the ethnicity extra)")
    p.set_defaults(func=cmd_ethnicity)

    p = sub.add_parser("evaluate", help="score raw LLM answers into (M, H, U)")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--match-level-threshold", type=float, default=None,
                   help="override evaluation.match_level_threshold")
    p.set_defaults(func=cmd_evaluate)

    p = sub.add_parser("sample", help="redraw the stratified evaluation sample")
    p.add_argument("--corpus", required=True)
    p.add_argument("--output", default="data/interim/eval_sample.csv.gz")
    p.add_argument("--per-stratum", type=int, default=None)
    p.add_argument("--verify-against", default=None,
                   help="compare against a released sample CSV")
    _add_common(p)
    p.set_defaults(func=cmd_sample)

    p = sub.add_parser("filter", help="run the five-stage quality filter")
    p.add_argument("--corpus", required=True)
    p.add_argument("--output", default="data/interim/filtered.ndjson.gz")
    p.add_argument("--funnel", default="results/tables/filter_funnel.json")
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=cmd_filter)

    p = sub.add_parser("distributions", help="Section 2.2 corpus statistics (needs the corpus)")
    p.add_argument("--corpus", default=None, help="defaults to paths.corpus / DUA_CORPUS")
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=cmd_distributions)

    p = sub.add_parser("collect", help="query a model for author attributions")
    p.add_argument("--model", required=True,
                   choices=["gpt-4o", "deepseek-r1", "claude-sonnet-4.5"])
    p.add_argument("--output", required=True)
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("recognise", aliases=["recognize"],
                       help="run the multiple-choice recognition experiment")
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--mode", default="random_field",
                   choices=["random_field", "same_field_swap", "collaborator_swap"])
    p.add_argument("--output", default="data/interim/mc_results.ndjson")
    p.add_argument("--build-only", action="store_true",
                   help="construct and verify items without querying a model")
    p.add_argument("--offline", action="store_true",
                   help="use only the cached collaborator lookups")
    p.add_argument("--analyse", "--analyze", action="store_true", dest="analyse",
                   help="emit the Section 6 tables and figures once collection finishes")
    p.set_defaults(func=cmd_recognise)

    p = sub.add_parser("recognition-tables",
                       help="Section 6 tables from an already-scored MC run")
    p.add_argument("--results", nargs="+", required=True, metavar="MODE=PATH",
                   help="e.g. random_field=data/interim/mc_random_field.ndjson")
    p.add_argument("--model", default="gpt-4o", help="which model's recall to compare against")
    p.set_defaults(func=cmd_recognition_tables)

    p = sub.add_parser("proxy", help="Section 3 prevalence proxies (needs API keys or a cache)")
    p.add_argument("action", choices=["sample", "google", "infinigram", "both", "analyse"])
    p.add_argument("--corpus", default=None, help="for `sample`")
    p.add_argument("--papers", default=None,
                   help="CSV of papers to query; defaults to the evaluation sample")
    p.add_argument("--output", default="data/interim/proxy_sample.csv.gz")
    p.add_argument("--google-out", default="data/interim/google_hits.csv")
    p.add_argument("--infinigram-out", default="data/interim/infinigram_counts.csv")
    p.add_argument("--offline", action="store_true",
                   help="read only the shipped cache; never call an API")
    p.set_defaults(func=cmd_proxy)

    p = sub.add_parser("probing-prompts",
                       help="rebuild the --data_csv the Section 7 GPU stages need")
    p.add_argument("--sample", default=None,
                   help="evaluation sample (default: data/release/eval_sample_9108.csv.gz)")
    p.add_argument("--output", default="data/interim/probing_prompts_9108.csv")
    p.set_defaults(func=cmd_probing_prompts)

    p = sub.add_parser("probing-rundir",
                       help="unpack the --run_dir a steering re-run needs")
    p.add_argument("--model", default=None,
                   choices=["qwen3_32b", "mistral_small_3_2_24b"],
                   help="default: both")
    p.add_argument("--out-root", default="runs",
                   help="parent directory; one subdirectory per model")
    p.set_defaults(func=cmd_probing_rundir)

    p = sub.add_parser("metrics", help="collect every quoted number into one JSON")
    p.set_defaults(func=cmd_metrics)

    p = sub.add_parser("verify", help="tests, checksums, and cross-artifact invariants")
    p.add_argument("--no-strict", action="store_true",
                   help="report problems without a non-zero exit")
    p.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    from dua.config import load_config
    from dua.seeds import set_all_seeds

    set_all_seeds(getattr(args, "seed", None) or load_config().seed)

    from dua.collect.client import MissingAPIKeyError
    try:
        return args.func(args)
    except MissingAPIKeyError as exc:
        # A missing credential is a setup problem, not a crash. The exception
        # message already names the variable and where to put it.
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
