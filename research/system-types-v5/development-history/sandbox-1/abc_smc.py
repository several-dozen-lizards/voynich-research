"""S_fit-only ABC-SMC engine with bounded uniform priors and importance weights.

The caller supplies a distance simulator; this module never imports held.py.
Tolerance schedules, priors, seeds and simulation budgets must be frozen by caller.
"""
import math
import numpy as np
from scipy.special import logsumexp
from scipy.stats import multivariate_normal

class SimulationBudgetExceeded(RuntimeError):
    pass

def run(distance, bounds, tolerances, particles=2000, seed=54024, max_simulations=1000000):
    bounds = np.asarray(bounds, dtype=float)
    if bounds.ndim != 2 or bounds.shape[1] != 2 or not np.all(np.isfinite(bounds)) or np.any(bounds[:, 1] <= bounds[:, 0]):
        raise ValueError('finite increasing [low,high] bounds required')
    if particles < 2 or not tolerances or any(not math.isfinite(x) or x <= 0 for x in tolerances):
        raise ValueError('positive finite tolerances and at least two particles required')
    if any(b >= a for a, b in zip(tolerances, tolerances[1:])):
        raise ValueError('tolerances must strictly decrease')
    rng = np.random.default_rng(seed)
    low, high = bounds.T
    dimension = len(bounds)
    generations = []
    total = 0
    for generation, epsilon in enumerate(tolerances):
        accepted, distances, seeds, log_weights = [], [], [], []
        attempts = 0
        proposals = 0
        if generation:
            old = np.asarray(generations[-1]['parameters'])
            weights = np.asarray(generations[-1]['weights'])
            covariance = 2*np.atleast_2d(np.cov(old.T, aweights=weights))
            # Machine-scale ridge protects collapsed finite-sample covariance.
            covariance += np.diag(((high-low)*1e-8)**2)
        else:
            covariance = None
        while len(accepted) < particles:
            proposals += 1
            if proposals > max_simulations * 100:
                raise SimulationBudgetExceeded('bounded-kernel proposals exhausted')
            if generation:
                parent = rng.choice(particles, p=weights)
                theta = rng.multivariate_normal(old[parent], covariance)
                if np.any(theta < low) or np.any(theta > high):
                    continue
            else:
                theta = rng.uniform(low, high)
            if total >= max_simulations:
                raise SimulationBudgetExceeded(f'{total} simulations, generation {generation}, accepted {len(accepted)}/{particles}; not a completed posterior')
            sim_seed = int(rng.integers(0, 2**63-1))
            value = float(distance(theta, sim_seed))
            total += 1
            attempts += 1
            if math.isnan(value) or value < 0:
                raise ValueError('invalid ABC distance')
            if value > epsilon:
                continue
            if generation:
                log_density = multivariate_normal.logpdf(old, mean=theta, cov=covariance)
                log_weight = -float(logsumexp(np.log(weights)+log_density))
            else:
                log_weight = 0.
            accepted.append(theta.tolist())
            distances.append(value)
            seeds.append(sim_seed)
            log_weights.append(log_weight)
        log_weights = np.asarray(log_weights)
        normalized = np.exp(log_weights - logsumexp(log_weights))
        generations.append(dict(generation=generation, epsilon=epsilon, parameters=accepted,
                                distances=distances, simulation_seeds=seeds, weights=normalized.tolist(),
                                covariance=None if covariance is None else covariance.tolist(),
                                simulations=attempts, proposals=proposals,
                                effective_sample_size=float(1/np.sum(normalized**2))))
    return dict(status='COMPLETE', seed=seed, particles=particles, total_simulations=total,
                bounds=bounds.tolist(), generations=generations)
