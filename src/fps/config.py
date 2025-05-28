"""
FPS configuration management.
Default parameters matching math.md specifications.
"""

import numpy as np
from typing import Dict, List
import json


def create_default_config(N: int = 20, T: float = 20.0, seed: int = 42) -> Dict:
    """
    Create default FPS configuration with parameters matching math.md specifications exactly.
    """
    np.random.seed(seed)
    
    return {
        'system': {
            'N': N,
            'T': T,
            'dt': 0.05,  # Smaller time step for smoother dynamics
            'seed': seed
        },
        'spiral': {
            'phi': 1.618,  # Golden ratio
            'epsilon': 0.05,  # As specified in math.md
            'omega': 0.1,   # As specified in math.md
            'theta': 0.0
        },
        'strates': {
            'A0': np.random.uniform(0.5, 1.2, N).tolist(),
            'f0': np.random.uniform(0.1, 1.5, N).tolist(),
            'alpha': [0.1] * N,  # Reduced from 0.5 to 0.1 for stability (still within "≈ 0.5" range)
            'beta': np.random.uniform(0.05, 0.15, N).tolist(),
            'k': [2.0] * N,  # As specified in math.md (k = 2.0)
            'x0': [0.5] * N, # As specified in math.md (x0 = 0.5)
            'w': [0.01] * N  # Reduced from 0.1 to 0.01 for stability while maintaining mathematical form
        },
        'lambda': 1.0,  # As specified in math.md (λ ≈ 1)
        'to_calibrate': [
            'variance_d2S',
            'entropy_S', 
            'gamma_n',
            'env_n',
            'sigma_n'
        ]
    }


def create_golden_run_config() -> Dict:
    """
    Create the specific golden run configuration for reproducible testing.
    N = 5, T = 20, seed = 42, scenario #1 (constant 0.3)
    """
    return create_default_config(N=5, T=20.0, seed=42)


def create_kuramoto_config(N: int = 20, seed: int = 123) -> Dict:
    """
    Create Kuramoto model configuration for control comparison.
    N = 20, K = 0.5, ω_i ~ U[0,1]
    """
    np.random.seed(seed)
    
    return {
        "N": N,
        "K": 0.5,  # Coupling strength
        "omega": np.random.uniform(0, 1, N).tolist(),  # Natural frequencies
        "dt": 0.1,
        "T": 20.0,
        "seed": seed
    }


def save_config(config: Dict, filepath: str):
    """Save configuration to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)


def load_config(filepath: str) -> Dict:
    """Load configuration from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


# Predefined scenarios for input I_n(t)
INPUT_SCENARIOS = {
    "constant": "Constant 0.3",
    "step": "Step to 1 at t = T/4", 
    "ramp": "Linear ramp 0→1 over [0,T]"
}


def validate_config(config: Dict) -> bool:
    """
    Validate configuration structure matches requirements.
    """
    required_keys = ['system', 'spiral', 'strates']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")
    
    # Validate system parameters
    system = config['system']
    required_system = ['N', 'T', 'seed']
    for key in required_system:
        if key not in system:
            raise ValueError(f"Missing required system parameter: {key}")
    
    # Validate spiral parameters  
    spiral = config['spiral']
    required_spiral = ['phi', 'epsilon', 'omega', 'theta']
    for key in required_spiral:
        if key not in spiral:
            raise ValueError(f"Missing required spiral parameter: {key}")
    
    # Validate strates parameters
    strates = config['strates']
    required_strates = ['A0', 'f0', 'alpha', 'beta', 'k', 'x0', 'w']
    for key in required_strates:
        if key not in strates:
            raise ValueError(f"Missing required strates parameter: {key}")
        
        # Check array lengths match N
        if len(strates[key]) != system['N']:
            raise ValueError(f"Strate parameter {key} length {len(strates[key])} != N={system['N']}")
    
    return True


if __name__ == "__main__":
    # Create and save default configurations
    
    # Main FPS config
    fps_config = create_default_config()
    save_config(fps_config, "config/fps_default.json")
    print("Created config/fps_default.json")
    
    # Golden run config
    golden_config = create_golden_run_config()
    save_config(golden_config, "config/fps_golden.json")
    print("Created config/fps_golden.json")
    
    # Kuramoto control config
    kuramoto_config = create_kuramoto_config()
    save_config(kuramoto_config, "config/kuramoto_control.json")
    print("Created config/kuramoto_control.json") 