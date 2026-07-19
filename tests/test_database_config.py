import backend.app as backend_app


def test_get_database_uri_defaults_to_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_URI", raising=False)
    monkeypatch.delenv("USE_SQLITE", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)

    uri = backend_app.get_database_uri()

    assert uri.startswith("sqlite:///")


def test_get_database_uri_uses_mysql_when_custom_settings_are_provided(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_URI", raising=False)
    monkeypatch.delenv("USE_SQLITE", raising=False)
    monkeypatch.setenv("DB_HOST", "db.internal")
    monkeypatch.setenv("DB_USER", "app")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DB_NAME", "finance")
    monkeypatch.setenv("DB_PORT", "3306")

    uri = backend_app.get_database_uri()

    assert uri.startswith("mysql+pymysql://")


def test_get_database_uri_ignores_default_local_password(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_URI", raising=False)
    monkeypatch.delenv("USE_SQLITE", raising=False)
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_USER", "root")
    monkeypatch.setenv("DB_PASSWORD", "Root")
    monkeypatch.setenv("DB_NAME", "finance")
    monkeypatch.setenv("DB_PORT", "3306")

    uri = backend_app.get_database_uri()

    assert uri.startswith("sqlite:///")
