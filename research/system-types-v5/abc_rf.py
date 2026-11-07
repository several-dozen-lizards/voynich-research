"""Pudlo-style selected-model probability, not forest votes as posteriors."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

def model_choice(reference_summaries, family_labels, observed, seed=55024, trees=500):
    X = np.asarray(reference_summaries, dtype=float)
    y = np.asarray(family_labels)
    observed = np.asarray(observed, dtype=float).reshape(1, -1)
    if X.ndim != 2 or len(X) != len(y) or X.shape[1] != observed.shape[1] or len(set(y)) < 2:
        raise ValueError('at least two families with aligned summary vectors required')
    if not np.all(np.isfinite(X)) or not np.all(np.isfinite(observed)):
        raise ValueError('missing/unsupported held statistics require a frozen policy; no silent imputation')
    classifier = RandomForestClassifier(n_estimators=trees, oob_score=True, bootstrap=True,
                                        random_state=seed, n_jobs=1)
    classifier.fit(X, y)
    probabilities = classifier.oob_decision_function_
    valid = probabilities.sum(axis=1) > 0
    if not valid.all():
        raise ValueError('some records have no out-of-bag prediction; increase frozen forest size')
    errors = (classifier.classes_[probabilities.argmax(axis=1)] != y).astype(float)
    error_regressor = RandomForestRegressor(n_estimators=trees, random_state=seed+1, n_jobs=1)
    error_regressor.fit(X, errors)
    selected = str(classifier.predict(observed)[0])
    return dict(selected_family=selected, selected_model_posterior_probability_approximation=float(1-error_regressor.predict(observed)[0]),
                prior_predictive_oob_error=float(errors.mean()), seed=seed, trees=trees,
                descriptive_vote_fractions=dict(zip(map(str, classifier.classes_), map(float, classifier.predict_proba(observed)[0]))),
                all_family_posterior_probabilities=None,
                limitation='Selected-model probability estimated by OOB allocation-error regression. Vote fractions are not posterior model probabilities; remaining probabilities not identified by this method.')
