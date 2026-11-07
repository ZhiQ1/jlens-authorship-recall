"""Batch 2, group C (addendum 12 items 2-1, 2-2, 2-11; addendum 13 item C-3b): the ONE place where the column names of
every result file written by the group-C scripts are defined (HANDOFF fixed rule 4). Every b2c script imports from here;
a writer calls `check(df, NAME)` before saving so a renamed/missing column fails at write time, not in the analysis.

No column module existed for Stage 13 before batch 2 (checked 2026-11-06: no shared module in ~/jlens_work); this file is
new and is used only by the group-C batch-2 scripts. Existing (frozen) scripts are not changed.
"""

# ---------------------------------------------------------------- C-3b (addendum 13): five-false-title probe, no exclusion
C3B_ROLE_LAYER = ['run', 'layer', 'version', 'spec', 'lo', 'hi', 'n', 'tc', 'tc_lo', 'tc_hi', 'tc_bins',
                  'ctrl_any', 'ctrl_any_lo', 'ctrl_any_hi', 'ctrl_field', 'ctrl_field_lo', 'ctrl_field_hi']
C3B_PRIMARY = ['version', 'quantity', 'est', 'lo', 'hi', 'n']
C3B_HARDCHECK = ['run', 'layer', 'version', 'column', 'new', 'published', 'abs_diff']

# ---------------------------------------------------------------- 2-1 Stage 9 Fit B
FITB_HARDCHECK = ['check', 'layer', 'value', 'reference', 'rel_diff', 'threshold', 'status']
FITB_MATRIX = ['layer', 'cos_A_B', 'relfro_A_B', 'cos_A_B_minus_I', 'normA', 'normB', 'cos_A_public', 'cos_B_public']
FITB_HOLDOUT = ['layer', 'lens', 'n_positions', 'kl_final_mean', 'kl_final_median', 'top1_final_agree', 'top10_overlap_final',
                'top10_overlap_A_B', 'top1_A_B_agree']
FITB_READ_KEYS = ['row_id']            # npz: row_id + '<lens>@<layer>' rank arrays (lens in FITB_LENSES)
FITB_LENSES = ['fitA', 'fitB']
FITB_SIGNAL = ['lens', 'layer', 'group', 'spec', 'lo', 'hi', 'n_papers', 'tc', 'tc_lo', 'tc_hi', 'tc_bins']
FITB_PARITY = ['cond', 'layer', 'n_rows', 'share_rank_equal', 'max_abs_log10rank_diff', 'mean_abs_log10rank_diff', 'threshold', 'status']

# ---------------------------------------------------------------- 2-2 F1 split-half by author team
F1H_SPLIT = ['paper_id', 'team', 'half', 'fit_row', 'group_tight']
F1H_HARDCHECK = ['layer', 'relfro_combined_vs_stored', 'maxabs', 'threshold', 'status']
F1H_MATRIX = ['layer', 'cos_A_B', 'cos_A_full', 'cos_B_full', 'cos_A_B_minus_I', 'relfro_A_B', 'top10_A_B', 'top10_A_full', 'top10_B_full']
F1H_READOUT = ['position', 'layer', 'lens', 'target', 'target_lo', 'target_hi', 'control', 'control_lo', 'control_hi',
               'tc', 'tc_lo', 'tc_hi', 'n_papers']

# ---------------------------------------------------------------- 2-11 model-generated names
GN_NAMES = ['paper_id', 'name_index', 'name', 'label', 'group_tight', 'recall_level', 'citation_bin', 'team', 'fold',
            'char_start', 'char_end', 'tok_first', 'tok_last', 'pos_pred_first', 'pos_last', 'n_name_tokens',
            'surname', 'surname_freq_cohort', 'given_is_initial', 'name_len_chars', 'name_n_words', 'name_index_rel']
GN_REPRO = ['paper_id', 'first_name_stored', 'first_name_greedy', 'match', 'greedy_text']
GN_PROBE = ['layer', 'position', 'subset', 'feature_set', 'auroc', 'auroc_lo', 'auroc_hi', 'n_M', 'n_H', 'C', 'shuffled_auroc']
GN_LAYERS = [16, 24, 32, 40, 48, 52, 56]
GN_POSITIONS = ['pred_first', 'last']


def check(df, name):
    """Raise if df's columns differ from the registered list `name` (a module-level constant)."""
    want = globals()[name]
    got = list(df.columns)
    if got != want:
        raise ValueError(f'columns of {name} differ: got {got}, want {want}')
    return df


# ---------------------------------------------------------------- 2-11 version 2 (deviation record D12-3)
GN2_NAMES = GN_NAMES + ['fullname_freq_cohort']
GN2_COUNTS = ['paper_id', 'group_tight', 'm_pkg', 'h_pkg', 'u_pkg', 'm_rebuilt', 'h_rebuilt', 'u_rebuilt', 'match']
GN2_PROBE = ['layer', 'position', 'subset', 'score', 'auroc_within', 'lo', 'hi', 'n_papers', 'n_pairs', 'n_M', 'n_H',
             'diff_vs_position', 'diff_pos_lo', 'diff_pos_hi', 'diff_vs_string', 'diff_str_lo', 'diff_str_hi', 'signal',
             'auroc_pooled_ref', 'shuffled_within']
