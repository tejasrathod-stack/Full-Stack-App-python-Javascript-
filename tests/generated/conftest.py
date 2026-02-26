"""
pytest configuration for AI-generated tests.
Framework-specific setup with minimal dependencies.
"""

import os
import sys
import pytest
import warnings

# Suppress deprecation warnings during testing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Set testing environment
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("LOG_LEVEL", "ERROR")

# Add target project to Python path
TARGET_ROOT = os.environ.get("TARGET_ROOT", "/home/runner/work/Full-Stack-App-python-Javascript-/Full-Stack-App-python-Javascript-/pipeline/target_repo/backend")
if TARGET_ROOT and TARGET_ROOT not in sys.path:
    sys.path.insert(0, TARGET_ROOT)

# Also add current directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============== FLASK + SQLALCHEMY CONFIGURATION ==============

_flask_app = None
_db = None
try:
    for module_name in ['app', 'application', 'main', 'server', 'api']:
        try:
            mod = __import__(module_name)
            if hasattr(mod, 'app'):
                _flask_app = mod.app
            elif hasattr(mod, 'create_app'):
                _flask_app = mod.create_app()
            elif hasattr(mod, 'application'):
                _flask_app = mod.application
            if hasattr(mod, 'db'):
                _db = mod.db
            if _flask_app:
                break
        except ImportError:
            continue
except Exception:
    pass


@pytest.fixture
def app():
    """Flask application with fresh test database per test."""
    if _flask_app is None:
        pytest.skip("No Flask app found")

    _flask_app.config['TESTING'] = True
    _flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    _flask_app.config['WTF_CSRF_ENABLED'] = False

    ctx = _flask_app.app_context()
    ctx.push()

    if _db is not None:
        _db.create_all()

    yield _flask_app

    if _db is not None:
        _db.session.remove()
        _db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app):
    """Flask test client with DB support."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session for direct DB assertions."""
    if _db is None:
        pytest.skip("No SQLAlchemy db found")
    yield _db.session
    _db.session.rollback()


@pytest.fixture
def sample_data():
    """Sample test data for Flask-DB apps."""
    return {
        "title": "Test Item",
        "description": "Test Description",
        "name": "Test Name",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }


@pytest.fixture
def auth_headers():
    """Authorization headers for API testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
