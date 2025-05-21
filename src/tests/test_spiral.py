from fps.spiral import G_factory


def test_tanh_monotonic():
    G = G_factory("tanh")
    assert G(0.1) > G(-0.1)
