import event_store


def test_event_store_saves_event(tmp_path, monkeypatch):
    database_path = tmp_path / "events.db"

    monkeypatch.setattr(
        event_store,
        "DB_PATH",
        str(database_path),
    )

    event_store.init_db()

    inserted = event_store.save_event(
        delivery_id="delivery-001",
        event_name="issues",
        action="opened",
        payload={"action": "opened"},
    )

    events = event_store.get_events()

    assert inserted is True
    assert len(events) == 1
    assert events[0]["delivery_id"] == "delivery-001"
    assert events[0]["event_name"] == "issues"


def test_event_store_ignores_duplicate_delivery(tmp_path, monkeypatch):
    database_path = tmp_path / "events.db"

    monkeypatch.setattr(
        event_store,
        "DB_PATH",
        str(database_path),
    )

    event_store.init_db()

    first_insert = event_store.save_event(
        delivery_id="delivery-duplicate",
        event_name="issues",
        action="opened",
        payload={"action": "opened"},
    )

    second_insert = event_store.save_event(
        delivery_id="delivery-duplicate",
        event_name="issues",
        action="opened",
        payload={"action": "opened"},
    )

    events = event_store.get_events()

    assert first_insert is True
    assert second_insert is False
    assert len(events) == 1
