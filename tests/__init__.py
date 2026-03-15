import os

os.environ.setdefault("AUTH_SECRET", "test-auth-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
