from pathlib import Path

from drivesense.models import TelemetryEvent
from drivesense.offline.buffer import LocalEventBuffer


def test_buffer_is_idempotent_and_retries(tmp_path: Path) -> None:
    event = TelemetryEvent(
        "id-1", "v1", "t1", "2026-01-01T00:00:00+00:00", 0, 0, 0, 50, "OFFLINE", -100, 0, "OFFLINE"
    )
    buffer = LocalEventBuffer(tmp_path / "buffer.db")
    assert buffer.enqueue(event) is True
    assert buffer.enqueue(event) is False
    assert buffer.reconcile(lambda _: (_ for _ in ()).throw(ConnectionError())) == (0, 1)
    sent: list[str] = []
    assert buffer.reconcile(lambda item: sent.append(item.event_id)) == (1, 0)
    assert sent == ["id-1"]
    buffer.close()
