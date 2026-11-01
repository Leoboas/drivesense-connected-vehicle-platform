from drivesense.telemetry.generator import (
    SAO_PAULO_FLORIANOPOLIS_ROAD,
    GeneratorConfig,
    generate_events,
    point_on_path,
)


def test_generator_injects_deterministic_duplicates() -> None:
    events = generate_events(
        GeneratorConfig(vehicles=1, trips=1, events=4, duplicate_probability=1, seed=1)
    )
    assert len(events) == 8
    assert len({event.event_id for event in events}) == 4


def test_generator_marks_offline_events() -> None:
    events = generate_events(
        GeneratorConfig(vehicles=1, trips=1, events=3, offline_probability=1, seed=1)
    )
    assert all(event.connection_state == "OFFLINE" for event in events)


def test_generator_covers_the_four_geography_scenarios() -> None:
    events = generate_events(GeneratorConfig(vehicles=4, trips=4, events=8, seed=1))
    assert {event.scenario for event in events} == {
        "SAO_PAULO_URBAN",
        "SAO_PAULO_FLORIANOPOLIS_CORRIDOR",
        "FLORIANOPOLIS_TRAILS",
        "SP_FLORIANOPOLIS_CONNECTIVITY_VARIATION",
    }
    assert {event.region_type for event in events} == {"URBAN", "HIGHWAY", "TRAIL"}


def test_sao_paulo_florianopolis_corridor_uses_declared_road_endpoints() -> None:
    assert point_on_path(SAO_PAULO_FLORIANOPOLIS_ROAD, 0) == SAO_PAULO_FLORIANOPOLIS_ROAD[0]
    assert point_on_path(SAO_PAULO_FLORIANOPOLIS_ROAD, 1) == SAO_PAULO_FLORIANOPOLIS_ROAD[-1]
