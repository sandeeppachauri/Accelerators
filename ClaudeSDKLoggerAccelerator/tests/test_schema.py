from sdk_logger_accelerator.schema import SCHEMA_VERSION, Scope, TraceRecord


def test_to_dict_embeds_schema_version_and_scope_value():
    record = TraceRecord(
        scope=Scope.INFO,
        session_id="s1",
        turn_index=0,
        timestamp="2026-01-01T00:00:00+00:00",
    )
    data = record.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["scope"] == "INFO"


def test_default_metadata_is_independent_dict():
    a = TraceRecord(scope=Scope.DEBUG, session_id="s1", turn_index=0, timestamp="t")
    b = TraceRecord(scope=Scope.DEBUG, session_id="s2", turn_index=0, timestamp="t")
    a.metadata["k"] = "v"
    assert b.metadata == {}
