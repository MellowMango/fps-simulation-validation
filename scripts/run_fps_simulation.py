#!/usr/bin/env python3
"""
Lightweight FPS simulation for frontend.
Returns JSON data for visualization.
"""

import sys
import os
import json
import argparse
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fps.dynamics import FPSDynamics
from fps.metrics import FPSMetrics
from fps.config import create_default_config


def run_simulation_for_frontend(config_override=None):
    """Run FPS simulation and return results for frontend."""
    
    # Create configuration (smaller for faster frontend response)
    config = create_default_config(N=5, T=20.0, seed=42)
    
    if config_override:
        config.update(config_override)
    
    # Run FPS simulation
    fps_model = FPSDynamics(config)
    results = fps_model.run_simulation(input_scenario="constant", use_extended=False)
    
    # Run validation metrics
    metrics_engine = FPSMetrics(results)
    validation = metrics_engine.run_all_validations()
    
    # Format for frontend
    frontend_data = {
        't': results['time'].tolist(),
        'S': results['S'].tolist(),
        'C': results['C'].tolist(),
        'r': results['r'].tolist(),
        'validation': {
            'all_passed': validation['all_passed'],
            'pass_rate': validation['summary']['pass_rate'],
            'failed_metrics': validation['summary']['failed_metrics']
        },
        'config': config
    }
    
    return frontend_data


def main():
    parser = argparse.ArgumentParser(description='Run FPS simulation for frontend')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--scenario', default='constant', choices=['constant', 'step', 'ramp'])
    parser.add_argument('-N', type=int, default=5, help='Number of strates')
    parser.add_argument('-T', type=float, default=20.0, help='Simulation time')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    try:
        # Configuration override
        config_override = {
            'system': {
                'N': args.N,
                'T': args.T,
                'seed': args.seed
            }
        }
        
        # Run simulation
        results = run_simulation_for_frontend(config_override)
        
        if args.json:
            # Output JSON for frontend
            print(json.dumps(results))
        else:
            # Human-readable output
            print(f"FPS Simulation Results:")
            print(f"- Time points: {len(results['t'])}")
            print(f"- S(t) range: [{min(results['S']):.3f}, {max(results['S']):.3f}]")
            print(f"- C(t) range: [{min(results['C']):.3f}, {max(results['C']):.3f}]")
            print(f"- r(t) range: [{min(results['r']):.3f}, {max(results['r']):.3f}]")
            print(f"- Validation passed: {results['validation']['all_passed']}")
            print(f"- Pass rate: {results['validation']['pass_rate']:.1%}")
            
            if not results['validation']['all_passed']:
                print(f"- Failed metrics: {results['validation']['failed_metrics']}")
    
    except Exception as e:
        if args.json:
            error_response = {
                'error': 'Simulation failed',
                'details': str(e)
            }
            print(json.dumps(error_response))
            sys.exit(1)
        else:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main() 