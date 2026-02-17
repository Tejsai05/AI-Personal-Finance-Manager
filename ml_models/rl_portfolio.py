"""
Reinforcement Learning (PPO) for Dynamic Portfolio Allocation
"""
import numpy as np
from typing import Dict
import os

try:
    import gymnasium as gym
    from gymnasium import spaces
    from stable_baselines3 import PPO
    HAS_RL = True
except ImportError:
    HAS_RL = False


class PortfolioOptimizer:
    """Portfolio optimization (with or without RL)"""
    
    def __init__(self, initial_amount: float = 100000):
        self.initial_amount = initial_amount
        self.model = None
        self.is_trained = False
    
    def get_allocation(self, risk_level: str) -> Dict:
        """Get optimal portfolio allocation"""
        risk_map = {"Low": 0, "Medium": 1, "High": 2}
        level = risk_map.get(risk_level, 1)
        
        allocations = {
            0: {"SIP": 30, "MutualFunds": 25, "Stocks": 10, "FD": 25, "Savings": 10, "Insurance": 0},
            1: {"SIP": 25, "MutualFunds": 30, "Stocks": 20, "FD": 15, "Savings": 5, "Insurance": 5},
            2: {"SIP": 20, "MutualFunds": 25, "Stocks": 40, "FD": 5, "Savings": 5, "Insurance": 5},
        }
        
        return {
            "recommended_allocation": allocations.get(level, allocations[1]),
            "total_amount": self.initial_amount,
            "risk_level": risk_level,
            "method": "rule_based"
        }


def get_optimal_allocation(amount: float, risk_level: str) -> Dict:
    """Get optimal portfolio allocation"""
    optimizer = PortfolioOptimizer(amount)
    return optimizer.get_allocation(risk_level)
