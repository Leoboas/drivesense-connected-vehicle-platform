from drivesense.telemetry.generator import GeneratorConfig, generate_events


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
