"""
Kuramoto model implementation for control comparison.
Standard phase-coupled oscillators as falsifiability anchor.
"""

import numpy as np
from typing import Dict, List, Tuple
import time


class KuramotoModel:
    """
    Standard Kuramoto model for control comparison.
    dθᵢ/dt = ωᵢ + (K/N) Σⱼ sin(θⱼ - θᵢ)
    """
    
    def __init__(self, config: Dict):
        """Initialize Kuramoto model."""
        self.N = config['N']
        self.K = config['K']  # Coupling strength
        self.omega = np.array(config['omega'])  # Natural frequencies
        self.dt = config.get('dt', 0.1)
        self.T = config['T']
        self.seed = config['seed']
        
        # Set random seed
        np.random.seed(self.seed)
        
        # Initialize phases
        self.reset_state()
    
    def reset_state(self):
        """Reset system state."""
        self.t_steps = int(self.T / self.dt)
        self.time = np.linspace(0, self.T, self.t_steps)
        
        # Initial random phases
        self.theta_initial = 2 * np.pi * np.random.random(self.N)
        
        # History arrays
        self.theta_history = np.zeros((self.t_steps, self.N))
        self.r_history = np.zeros(self.t_steps)  # Order parameter
        self.psi_history = np.zeros(self.t_steps)  # Average phase
        
        # Performance tracking
        self.cpu_times = []
    
    def compute_order_parameter(self, theta: np.ndarray) -> Tuple[float, float]:
        """
        Compute Kuramoto order parameter and average phase.
        r = |⟨e^(iθ)⟩|, ψ = arg⟨e^(iθ)⟩
        """
        z = np.mean(np.exp(1j * theta))
        r = np.abs(z)
        psi = np.angle(z)
        return r, psi
    
    def compute_derivatives(self, theta: np.ndarray) -> np.ndarray:
        """
        Compute phase derivatives according to Kuramoto equation.
        dθᵢ/dt = ωᵢ + (K/N) Σⱼ sin(θⱼ - θᵢ)
        """
        dtheta_dt = np.zeros(self.N)
        
        for i in range(self.N):
            coupling_sum = 0.0
            for j in range(self.N):
                coupling_sum += np.sin(theta[j] - theta[i])
            
            dtheta_dt[i] = self.omega[i] + (self.K / self.N) * coupling_sum
        
        return dtheta_dt
    
    def run_simulation(self) -> Dict:
        """
        Run Kuramoto simulation using Euler integration.
        """
        start_time = time.time()
        
        # Initialize
        theta = self.theta_initial.copy()
        
        for t_idx in range(self.t_steps):
            step_start = time.time()
            
            # Store current state
            self.theta_history[t_idx, :] = theta
            
            # Compute order parameter
            r, psi = self.compute_order_parameter(theta)
            self.r_history[t_idx] = r
            self.psi_history[t_idx] = psi
            
            # Compute derivatives and update
            if t_idx < self.t_steps - 1:
                dtheta_dt = self.compute_derivatives(theta)
                theta = theta + self.dt * dtheta_dt
                
                # Keep phases in [0, 2π]
                theta = theta % (2 * np.pi)
            
            # Track CPU time
            step_time = time.time() - step_start
            self.cpu_times.append(step_time)
        
        total_time = time.time() - start_time
        
        return {
            'time': self.time,
            'theta': self.theta_history,
            'r': self.r_history,
            'psi': self.psi_history,
            'cpu_times': np.array(self.cpu_times),
            'total_time': total_time,
            'config': {
                'N': self.N,
                'K': self.K,
                'omega': self.omega.tolist(),
                'dt': self.dt,
                'T': self.T,
                'seed': self.seed
            }
        }
    
    def compute_synchronization_metrics(self, results: Dict) -> Dict:
        """
        Compute synchronization metrics for comparison with FPS.
        """
        r = results['r']
        theta = results['theta']
        
        # Mean order parameter (synchronization level)
        mean_r = np.mean(r)
        
        # Synchronization variance
        sync_variance = np.var(r)
        
        # Phase coherence (how aligned phases become)
        final_phases = theta[-1, :]
        phase_spread = np.std(final_phases)
        
        # Regularity metric (similar to FPS regulation)
        # Measure stability of order parameter
        r_diff = np.diff(r)
        regulation_metric = np.mean(np.abs(r_diff))
        
        return {
            'mean_order_parameter': mean_r,
            'synchronization_variance': sync_variance,
            'phase_spread': phase_spread,
            'regulation_metric': regulation_metric
        }


def run_kuramoto_control(config: Dict) -> Dict:
    """
    Run Kuramoto control simulation and return results.
    """
    model = KuramotoModel(config)
    results = model.run_simulation()
    
    # Add synchronization metrics
    sync_metrics = model.compute_synchronization_metrics(results)
    results['sync_metrics'] = sync_metrics
    
    return results


if __name__ == "__main__":
    # Test Kuramoto model
    from .config import create_kuramoto_config
    
    config = create_kuramoto_config(N=10, seed=42)
    results = run_kuramoto_control(config)
    
    print(f"Kuramoto simulation completed:")
    print(f"Final order parameter: {results['r'][-1]:.3f}")
    print(f"Mean order parameter: {results['sync_metrics']['mean_order_parameter']:.3f}")
    print(f"Total CPU time: {results['total_time']:.3f}s")
    print(f"Mean CPU per step: {np.mean(results['cpu_times']):.6f}s") 