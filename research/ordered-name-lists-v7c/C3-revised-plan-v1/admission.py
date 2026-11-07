"""Preparation has no real-scoring or vault executor."""


def require_scientific_release(*args, **kwargs):
    raise RuntimeError(
        'C3 PREPARATION ONLY: source collation, independent registration, '
        'adopted source/model freeze and scientific qualification are absent. '
        'No real fitting or vault execution is available here.'
    )
