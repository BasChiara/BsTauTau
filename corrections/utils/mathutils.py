# binomial efficiency + Clopper-Pearson 68% CI via scipy
from scipy.stats import beta as beta_dist
import numpy as np

def compute_efficiency(n_all, n_match):
    """
    Compute binomial efficiency and Clopper-Pearson 68% confidence interval.
    """
    
    eff = np.where(n_all > 0, n_match / n_all, 0.)
    lo  = beta_dist.ppf(0.16, n_match,     n_all - n_match + 1)
    hi  = beta_dist.ppf(0.84, n_match + 1, n_all - n_match    )
    lo  = np.where(n_all > 0, lo, 0.)
    hi  = np.where(n_all > 0, hi, 0.)

    return eff, lo, hi