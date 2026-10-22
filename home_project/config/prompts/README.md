# Prompt templates

Each file here is the verbatim template that produced a set of shipped
responses. Placeholders are Python `str.format` fields.

| File | Used by | Placeholders |
|---|---|---|
| `authorship_fewshot_paper.txt` | GPT-4o open-ended collection (Section 4.2) | `{question}` |
| `authorship_fewshot_openrouter.txt` | DeepSeek-R1 and Claude Sonnet 4.5 collection | `{question}` |
| `mc_recognition.txt` | Multiple-choice recognition (Section 6) | `{title}`, `{year}`, `{option_a}`…`{option_d}` |
| `self_eval.txt` | LLM-as-judge evaluation (Appendix A6.5) | `{question}`, `{reference}`, `{generated}` |

`{question}` is always built as:

```
Who are the authors of the paper titled '{title}' which was published in {year}?
```

## Two known divergences, recorded rather than silently fixed

1. **The two collection prompts differ by one line.** The OpenRouter template
   used for DeepSeek-R1 and Claude Sonnet 4.5 adds
   `If there are more than 20 authors, only list the first 20 and add ', ...' at the end.`
   to the second bullet. The GPT-4o template does not have it. Appendix A5.2 of
   the paper prints the GPT-4o version. Since the evaluation sample excludes
   papers with 20+ authors (Section 2.1, filter 2), the clause cannot fire on
   any ground-truth item, but the two models did receive different system text.

2. **The paper quotes the year, the code does not.** Appendix A5.2 renders the
   final line as `... which was published in '{year}'?`. Every collection
   script built it without quotes. The shipped responses were produced by the
   unquoted form, which is what these files contain.
