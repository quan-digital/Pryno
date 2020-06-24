import importlib
from main import build_bot, build_app

# export PYTHONPATH=pryno


def test_bot():
    assert build_bot()


def test_app():
    assert build_app()
