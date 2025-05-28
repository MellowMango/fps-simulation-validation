"""
Unit tests for FPS dynamics - Layer 1 validation.
Tests each formula is copied verbatim, not "close enough".
"""

import numpy as np
import pytest
from hypothesis import given, strategies as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fps.dynamics import FPSDynamics, sigma, compute_spiral_feedback
from fps.config import create_default_config


class TestSigma:
    """Test sigmoid activation function σ(x) = 1/(1+e^(-k(x-x₀)))"""
    
    def test_sigma_bounds(self):
        """σ(x) must be in (0,1] for all finite real x (allowing floating-point precision)"""
        x = np.array([-100, -10, -1, 0, 1, 10, 100])  # Avoid extreme values
        result = sigma(x, k=2.0, x0=0.5)
        assert np.all(result > 0), "σ(x) must be > 0"
        assert np.all(result <= 1), "σ(x) must be ≤ 1"
    
    def test_sigma_midpoint(self):
        """σ(x₀) = 0.5 exactly"""
        x0 = 0.5
        result = sigma(x0, k=2.0, x0=x0)
        assert abs(result - 0.5) < 1e-10, f"σ({x0}) should be 0.5, got {result}"
    
    def test_sigma_monotonic(self):
        """σ(x) is strictly increasing"""
        x = np.linspace(-5, 5, 100)
        result = sigma(x, k=2.0, x0=0.0)
        assert np.all(np.diff(result) > 0), "σ(x) must be monotonically increasing"
    
    @given(st.floats(-50, 50), st.floats(0.1, 10), st.floats(-10, 10))
    def test_sigma_property_bounds(self, x, k, x0):
        """Property test: σ(x) ∈ (0,1] for all valid inputs (allowing floating-point precision)"""
        result = sigma(x, k=k, x0=x0)
        assert 0 < result <= 1, f"σ({x}) = {result} not in (0,1]"


class TestSpiralFeedback:
    """Test spiral feedback G(x) = tanh(λx)"""
    
    def test_spiral_feedback_sign(self):
        """Property: sign(G(x)) = sign(x)"""
        x_pos = np.array([0.1, 1.0, 10.0])
        x_neg = np.array([-0.1, -1.0, -10.0])
        
        G_pos = compute_spiral_feedback(x_pos, lambda_val=1.0)
        G_neg = compute_spiral_feedback(x_neg, lambda_val=1.0)
        
        assert np.all(G_pos > 0), "G(x) > 0 when x > 0"
        assert np.all(G_neg < 0), "G(x) < 0 when x < 0"
    
    def test_spiral_feedback_zero(self):
        """G(0) = 0"""
        result = compute_spiral_feedback(0.0, lambda_val=1.0)
        assert abs(result) < 1e-10, f"G(0) should be 0, got {result}"
    
    def test_spiral_feedback_bounds(self):
        """G(x) ∈ [-1, 1] for all finite x (allowing floating-point precision)"""
        x = np.array([-100, -10, -1, 0, 1, 10, 100])  # Avoid infinity
        result = compute_spiral_feedback(x, lambda_val=1.0)
        assert np.all(result >= -1), "G(x) must be ≥ -1"
        assert np.all(result <= 1), "G(x) must be ≤ 1"


class TestComputeS:
    """Test global signal computation S(t)"""
    
    def test_compute_S_scalar(self):
        """Test S computation with known inputs"""
        config = create_default_config(N=3, T=1.0, seed=42)
        model = FPSDynamics(config)
        
        # Simple test case
        A = np.array([1.0, 1.0, 1.0])
        phi = np.array([0.0, np.pi/2, np.pi])
        
        S = model._compute_S(A, phi)
        
        # Known result: 1*cos(0) + 1*cos(π/2) + 1*cos(π) = 1 + 0 + (-1) = 0
        expected = 1.0 + 0.0 + (-1.0)
        assert abs(S - expected) < 1e-10, f"Expected {expected}, got {S}"
    
    def test_frequency_modulation_zero_when_S_zero(self):
        """Property: Δf = 0 when S = 0"""
        config = create_default_config(N=5, T=1.0, seed=42)
        model = FPSDynamics(config)
        
        # Create scenario where S = 0
        S_zero = 0.0
        delta_f = model._compute_frequency_modulation(S_zero)
        
        assert abs(delta_f) < 1e-10, f"Δf should be 0 when S=0, got {delta_f}"


class TestSpiralRatio:
    """Test spiral ratio r(t) = φ + ε sin(2πωt + θ)"""
    
    def test_spiral_ratio_golden_mean(self):
        """r(t) oscillates around φ = 1.618"""
        config = create_default_config(N=5, T=10.0, seed=42)
        model = FPSDynamics(config)
        
        # Run short simulation
        results = model.run_simulation("constant", use_extended=False)
        r_values = results['r']
        
        # Mean should be close to golden ratio
        mean_r = np.mean(r_values)
        phi = 1.618
        
        assert abs(mean_r - phi) < 0.1, f"Mean r(t) = {mean_r} should be ≈ φ = {phi}"
    
    def test_spiral_ratio_bounds(self):
        """r(t) should stay within reasonable bounds around φ"""
        config = create_default_config(N=5, T=5.0, seed=42)
        model = FPSDynamics(config)
        
        results = model.run_simulation("constant", use_extended=False)
        r_values = results['r']
        
        phi = 1.618
        epsilon = config['spiral']['epsilon']  # Amplitude
        
        # Should stay within φ ± ε bounds (approximately)
        assert np.all(r_values > phi - 2*epsilon), f"r(t) below bounds"
        assert np.all(r_values < phi + 2*epsilon), f"r(t) above bounds"


class TestDeterminism:
    """Test reproducibility with fixed seeds"""
    
    def test_same_seed_same_results(self):
        """Same seed should produce identical results"""
        config = create_default_config(N=5, T=2.0, seed=123)
        
        # Run 1
        model1 = FPSDynamics(config)
        results1 = model1.run_simulation("constant", use_extended=False)
        
        # Run 2 with same config
        model2 = FPSDynamics(config)
        results2 = model2.run_simulation("constant", use_extended=False)
        
        # Should be identical
        np.testing.assert_array_equal(results1['S'], results2['S'], 
                                    "Same seed should produce identical S(t)")
        np.testing.assert_array_equal(results1['C'], results2['C'],
                                    "Same seed should produce identical C(t)")
        np.testing.assert_array_equal(results1['r'], results2['r'],
                                    "Same seed should produce identical r(t)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 