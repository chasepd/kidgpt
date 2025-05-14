import pytest
from app.core.config import get_db_config


def test_get_db_config_all_set(monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", "localhost")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_USER", "user")
    monkeypatch.setenv("MYSQL_PASSWORD", "pass")
    monkeypatch.setenv("MYSQL_DATABASE", "db")
    cfg = get_db_config()
    assert cfg == {
        "host": "localhost",
        "port": "3306",
        "user": "user",
        "password": "pass",
        "database": "db"
    }

def test_get_db_config_some_missing(monkeypatch):
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_USER", "user")
    monkeypatch.setenv("MYSQL_PASSWORD", "pass")
    monkeypatch.setenv("MYSQL_DATABASE", "db")
    cfg = get_db_config()
    assert cfg["host"] is None
    assert cfg["port"] == "3306"
    assert cfg["user"] == "user"
    assert cfg["password"] == "pass"
    assert cfg["database"] == "db"

def test_get_db_config_all_missing(monkeypatch):
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    monkeypatch.delenv("MYSQL_PORT", raising=False)
    monkeypatch.delenv("MYSQL_USER", raising=False)
    monkeypatch.delenv("MYSQL_PASSWORD", raising=False)
    monkeypatch.delenv("MYSQL_DATABASE", raising=False)
    cfg = get_db_config()
    assert all(v is None for v in cfg.values()) 