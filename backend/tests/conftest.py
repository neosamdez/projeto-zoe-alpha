import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole
from app.core.security import get_password_hash, create_access_token

TEST_DB_URL = "sqlite:///./test_asi.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TENANT_ID = uuid.uuid4()
ADMIN_EMAIL = "testadmin@amenti.io"
TECH_EMAIL = "testtech@amenti.io"
PASSWORD = "test2026"


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_tables(db):
    for tbl in reversed(Base.metadata.sorted_tables):
        db.execute(tbl.delete())
    db.commit()
    yield


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_admin(db):
    admin = User(
        id=uuid.uuid4(),
        full_name="Test Admin",
        email=ADMIN_EMAIL,
        hashed_password=get_password_hash(PASSWORD),
        role=UserRole.ADMIN,
        tenant_id=TENANT_ID,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture()
def seed_technician(db):
    tech = User(
        id=uuid.uuid4(),
        full_name="Test Tech",
        email=TECH_EMAIL,
        hashed_password=get_password_hash(PASSWORD),
        role=UserRole.TECHNICIAN,
        tenant_id=TENANT_ID,
        is_active=True,
    )
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@pytest.fixture()
def admin_token(seed_admin):
    return create_access_token(
        data={"sub": seed_admin.email, "user_id": str(seed_admin.id), "tenant_id": str(TENANT_ID)}
    )


@pytest.fixture()
def tech_token(seed_technician):
    return create_access_token(
        data={"sub": seed_technician.email, "user_id": str(seed_technician.id), "tenant_id": str(TENANT_ID)}
    )


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def tech_headers(tech_token):
    return {"Authorization": f"Bearer {tech_token}"}
