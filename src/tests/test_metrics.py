from fps.metrics import coherence
from fps.strata import Stratum


def test_coherence_single():
    s = Stratum(1.0, 1.0, 0.0, 1.0, 0.1, 0.05, 0.01)
    assert coherence([s]) == 1.0
