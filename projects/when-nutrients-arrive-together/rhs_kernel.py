"""Allocation-light candidate; not used by the frozen reference experiments."""
import numpy as np


def rhs(state, supply, uptake, gain):
    x, resources = np.exp(state[:6]), state[6:]
    result = np.empty(36)
    result[:6] = gain @ resources - 0.3
    result[6:] = supply - (0.5 + uptake.T @ x) * resources
    return result
