import pytest

from drivesense.routing.scoring import RouteSegment, score_route


def test_low_connectivity_route_requires_offline_prefetch() -> None:
    result = score_route([RouteSegment("dead-zone", 10, 15, 100, 20, 2)], offline_threshold=0.5)
    assert result.predicted_offline_probability == 0.8
    assert result.offline_prefetch_required is True


def test_route_requires_segments() -> None:
    with pytest.raises(ValueError, match="requires at least one"):
        score_route([])
