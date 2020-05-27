import importlib
from pryno.main import build_bot, build_app

# export PYTHONPATH=pryno

def test_bot():
    assert build_bot() == True

def test_app():
    assert build_app() == True