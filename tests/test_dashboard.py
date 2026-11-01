from app.dashboard import relation_for


def test_relation_for_accepts_only_local_supported_dashboard_formats() -> None:
    assert relation_for("data/samples/dashboard-demo.jsonl") == (
        "read_json_auto('data/samples/dashboard-demo.jsonl')"
    )
    assert relation_for("data/silver/*.parquet") == (
        "read_parquet('data/silver/*.parquet', hive_partitioning=true)"
    )


def test_relation_for_escapes_a_path_and_rejects_unsupported_inputs() -> None:
    assert relation_for("data/driver's-demo.jsonl") == (
        "read_json_auto('data/driver''s-demo.jsonl')"
    )
    try:
        relation_for("data/samples/dashboard.csv")
    except ValueError as error:
        assert ".jsonl" in str(error)
    else:
        raise AssertionError("Unsupported dashboard input must be rejected.")
