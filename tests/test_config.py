import os

import pytest

from config import load_settings


def test_default_model(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.delenv("BG_MODEL", raising=False)
    settings = load_settings()
    assert settings.model == "birefnet-general"


def test_invalid_model(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("BG_MODEL", "does-not-exist")
    with pytest.raises(RuntimeError):
        load_settings()
