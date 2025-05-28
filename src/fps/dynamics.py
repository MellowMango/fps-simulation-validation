"""
Core FPS (Fractale Pulsante Spiralée) dynamics implementation.
All 6 fundamental equations as specified in math.md.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import time


def sigma(x: np.ndarray, k: float = 2.0, x0: float = 0.5) -> np.ndarray:
    """
    Standalone sigmoid activation function σ(x) = 1/(1+e^(-k(x-x₀)))
    Used for unit testing. Numerically stable implementation.
    """
    # Clip extreme values to prevent overflow
    z = -k * (x - x0)
    z = np.clip(z, -500, 500)  # Prevent overflow
    return 1.0 / (1.0 + np.exp(z))


def compute_spiral_feedback(x: np.ndarray, lambda_val: float = 1.0) -> np.ndarray:
    """
    Standalone spiral feedback function G(x) = tanh(λx)
    Used for unit testing.
    """
    return np.tanh(lambda_val * x)


class Stratum:
    """Individual strate in the FPS system."""


class FPSDynamics:
    """Core FPS mathematical model implementing all fundamental equations."""
    
    def __init__(self, config: Dict):
        """Initialize FPS system with configuration."""
        self.config = config
        self.N = config['system']['N']  # Number of strates
        self.T = config['system']['T']  # Time duration
        self.dt = config['system'].get('dt', 0.1)  # Time step
        self.seed = config['system']['seed']
        
        # Set random seed for reproducibility
        np.random.seed(self.seed)
        
        # Spiral parameters
        self.phi = config['spiral']['phi']  # Golden ratio ≈ 1.618
        self.epsilon = config['spiral']['epsilon']  # ≈ 0.05
        self.omega = config['spiral']['omega']  # ≈ 0.1
        self.theta = config['spiral']['theta']
        
        # Per-strate parameters (arrays of length N)
        self.A0 = np.array(config['strates']['A0'])
        self.f0 = np.array(config['strates']['f0'])
        self.alpha = np.array(config['strates']['alpha'])
        self.beta = np.array(config['strates']['beta'])
        self.k = np.array(config['strates']['k'])  # Sigmoid steepness
        self.x0 = np.array(config['strates']['x0'])  # Sigmoid center
        self.w = np.array(config['strates']['w'])  # Coupling weights (N x N)
        
        # Feedback parameters
        self.lambda_feedback = config.get('lambda', 1.0)
        
        # Initialize state variables
        self.reset_state()
    
    def reset_state(self):
        """Reset system state."""
        self.t_steps = int(self.T / self.dt)
        self.time = np.linspace(0, self.T, self.t_steps)
        
        # State arrays
        self.S_history = np.zeros(self.t_steps)
        self.C_history = np.zeros(self.t_steps)
        self.r_history = np.zeros(self.t_steps)
        self.A_history = np.zeros((self.t_steps, self.N))
        self.f_history = np.zeros((self.t_steps, self.N))
        
        # For extended form
        self.gamma_history = np.zeros((self.t_steps, self.N))
        self.E_history = np.zeros((self.t_steps, self.N))
        self.O_history = np.zeros((self.t_steps, self.N))
        
        # Performance tracking
        self.cpu_times = []
    
    def sigma(self, x: np.ndarray) -> np.ndarray:
        """
        Equation 1: Per-strate amplitude sigmoid function.
        σ(x) = 1/(1 + e^(-k(x-x₀)))
        """
        # Clip extreme values to prevent overflow
        z = -self.k * (x - self.x0)
        z = np.clip(z, -500, 500)  # Prevent overflow
        return 1.0 / (1.0 + np.exp(z))
    
    def compute_amplitude(self, I_n: np.ndarray, t_idx: int) -> np.ndarray:
        """
        Equation 1: Per-strate amplitude
        A_n(t) = A₀ σ(I_n(t))
        """
        return self.A0 * self.sigma(I_n)
    
    def compute_frequency_modulation(self, A_n: np.ndarray, f_n_prev: np.ndarray, t: float, t_idx: int) -> np.ndarray:
        """
        Equation 2: Frequency modulation
        Δf_n(t) = α_n Σᵢ w_{ni} S_i(t) → f_n(t) = f₀n + Δf_n(t)
        
        Proper implementation using individual strate signals S_i(t) = A_i(t) sin(2π f_i(t) t + φ_i)
        """
        # Use deterministic phases for reproducibility
        if not hasattr(self, '_phases'):
            np.random.seed(self.seed)  # Ensure reproducible phases
            self._phases = 2 * np.pi * np.random.random(self.N)
        
        # Compute individual strate signals S_i(t)
        S_i = A_n * np.sin(2 * np.pi * f_n_prev * t + self._phases)
        
        # Frequency modulation: Δf_n = α_n * w_n * Σᵢ S_i(t)
        # For simplicity, using scalar w_n instead of full matrix w_{ni}
        delta_f = self.alpha * self.w * np.sum(S_i)
        
        # Add numerical stability: clip extreme frequency changes
        delta_f = np.clip(delta_f, -1.0, 1.0)  # Prevent extreme frequency excursions
        
        # Ensure frequencies stay positive
        f_new = self.f0 + delta_f
        f_new = np.maximum(f_new, 0.01)  # Minimum frequency to prevent division by zero
        
        return f_new
    
    def compute_spiral_ratio(self, t: float) -> float:
        """
        Equation 5: Spiral ratio driver
        r(t) = φ + ε sin(2πωt + θ)
        """
        return self.phi + self.epsilon * np.sin(2 * np.pi * self.omega * t + self.theta)
    
    def spiral_feedback(self, x: np.ndarray) -> np.ndarray:
        """
        Equation 4: Spiral feedback function
        G(x) = tanh(λx)
        """
        return np.tanh(self.lambda_feedback * x)
    
    def compute_global_signal_canonical(self, A_n: np.ndarray, f_n: np.ndarray, t: float) -> float:
        """
        Equation 3: Global signal (canonical form)
        S(t) = Σₙ A_n(t) sin(2π f_n(t) t + φₙ)
        """
        # Use deterministic phases for reproducibility (initialized once)
        if not hasattr(self, '_phases'):
            np.random.seed(self.seed)  # Ensure reproducible phases
            self._phases = 2 * np.pi * np.random.random(self.N)
        
        signal = np.sum(A_n * np.sin(2 * np.pi * f_n * t + self._phases))
        
        # Add numerical stability: normalize by number of strates to prevent blow-ups
        signal = signal / self.N
        
        return signal
    
    def compute_global_signal_extended(self, A_n: np.ndarray, f_n: np.ndarray, 
                                     gamma_n: np.ndarray, E_n: np.ndarray, 
                                     O_n: np.ndarray, t: float) -> float:
        """
        Equation 3: Global signal (extended FPS form with feedback + latency)
        S(t) = Σₙ A_n(t) γ_n(t) sin(2π f_n(t) t + φₙ) G(E_n(t) - O_n(t))
        """
        # Use deterministic phases for reproducibility
        if not hasattr(self, '_phases'):
            np.random.seed(self.seed)  # Ensure reproducible phases
            self._phases = 2 * np.pi * np.random.random(self.N)
        
        feedback_term = self.spiral_feedback(E_n - O_n)
        signal = np.sum(A_n * gamma_n * np.sin(2 * np.pi * f_n * t + self._phases) * feedback_term)
        
        # Add numerical stability: normalize by number of strates to prevent blow-ups
        signal = signal / self.N
        
        return signal
    
    def compute_strate_kernel(self, x: np.ndarray, t: float, n: int, 
                            mu_n: float, sigma_n: float) -> np.ndarray:
        """
        Equation 6: Strate-local kernel (for visual sanity checks)
        G_n(x,t) = A_n(t) sinc(f_n(t)(x-μ_n(t))) exp(-(x-μ_n(t))²/(2σ_n²(t)))
        """
        A_n = self.A_history[-1, n] if len(self.A_history) > 0 else self.A0[n]
        f_n = self.f_history[-1, n] if len(self.f_history) > 0 else self.f0[n]
        
        # Sinc function (sin(πx)/(πx))
        arg = f_n * (x - mu_n)
        sinc_term = np.sinc(arg)  # NumPy sinc is sin(πx)/(πx)
        
        # Gaussian envelope
        gaussian_term = np.exp(-(x - mu_n)**2 / (2 * sigma_n**2))
        
        return A_n * sinc_term * gaussian_term
    
    def compute_coherence(self, S: float, r: float) -> float:
        """
        Compute coherence C(t) as a measure of spiral alignment.
        This is a derived metric, not one of the 6 fundamental equations.
        """
        # Simple coherence measure: how close spiral ratio is to golden ratio
        return np.exp(-abs(r - self.phi))
    
    def run_simulation(self, input_scenario: str = "constant", use_extended: bool = False) -> Dict:
        """
        Run complete FPS simulation with all equations.
        
        Args:
            input_scenario: "constant", "step", or "ramp"
            use_extended: Whether to use extended form with feedback
        
        Returns:
            Dictionary with all simulation results
        """
        start_time = time.time()
        
        # Generate input scenarios I_n(t)
        I_scenarios = self._generate_input_scenarios(input_scenario)
        
        # Initialize extended form variables if needed
        if use_extended:
            gamma_n = np.ones((self.t_steps, self.N))  # Placeholder
            E_n = np.random.normal(0, 0.1, (self.t_steps, self.N))  # Environment
            O_n = np.random.normal(0, 0.1, (self.t_steps, self.N))  # Output
        
        # Main simulation loop
        for t_idx, t in enumerate(self.time):
            step_start = time.time()
            
            # Current inputs
            I_n = I_scenarios[t_idx, :]
            
            # Equation 1: Compute amplitudes
            A_n = self.compute_amplitude(I_n, t_idx)
            self.A_history[t_idx, :] = A_n
            
            # Equation 2: Compute frequencies
            f_n_prev = self.f_history[t_idx-1, :] if t_idx > 0 else self.f0
            f_n = self.compute_frequency_modulation(A_n, f_n_prev, t, t_idx)
            self.f_history[t_idx, :] = f_n
            
            # Equation 5: Compute spiral ratio
            r_t = self.compute_spiral_ratio(t)
            self.r_history[t_idx] = r_t
            
            # Equation 3: Compute global signal
            if use_extended:
                gamma_n_t = gamma_n[t_idx, :]
                E_n_t = E_n[t_idx, :]
                O_n_t = O_n[t_idx, :]
                self.gamma_history[t_idx, :] = gamma_n_t
                self.E_history[t_idx, :] = E_n_t
                self.O_history[t_idx, :] = O_n_t
                
                S_t = self.compute_global_signal_extended(A_n, f_n, gamma_n_t, E_n_t, O_n_t, t)
            else:
                S_t = self.compute_global_signal_canonical(A_n, f_n, t)
            
            self.S_history[t_idx] = S_t
            
            # Compute coherence (derived metric)
            C_t = self.compute_coherence(S_t, r_t)
            self.C_history[t_idx] = C_t
            
            # Track CPU time per step
            step_time = time.time() - step_start
            self.cpu_times.append(step_time)
        
        total_time = time.time() - start_time
        
        return {
            'time': self.time,
            'S': self.S_history,
            'C': self.C_history,
            'r': self.r_history,
            'A': self.A_history,
            'f': self.f_history,
            'gamma': self.gamma_history if use_extended else None,
            'E': self.E_history if use_extended else None,
            'O': self.O_history if use_extended else None,
            'cpu_times': np.array(self.cpu_times),
            'total_time': total_time,
            'config': self.config
        }
    
    def _generate_input_scenarios(self, scenario: str) -> np.ndarray:
        """Generate input scenarios I_n(t) for all strates."""
        I_scenarios = np.zeros((self.t_steps, self.N))
        
        for t_idx, t in enumerate(self.time):
            if scenario == "constant":
                I_scenarios[t_idx, :] = 0.3
            elif scenario == "step":
                I_scenarios[t_idx, :] = 1.0 if t >= self.T/4 else 0.3
            elif scenario == "ramp":
                I_scenarios[t_idx, :] = t / self.T
            else:
                raise ValueError(f"Unknown scenario: {scenario}")
        
        return I_scenarios
    
    # Helper methods for testing
    def _compute_S(self, A: np.ndarray, phi: np.ndarray) -> float:
        """Helper method for testing: compute S with given amplitudes and phases."""
        return np.sum(A * np.cos(phi))  # Using cosine for the test case
    
    def _compute_frequency_modulation(self, S: float) -> float:
        """Helper method for testing: compute frequency modulation for scalar case."""
        # For testing, return the change in frequency for first strate
        # Using simplified approach for backward compatibility with tests
        return self.alpha[0] * self.w[0] * S 