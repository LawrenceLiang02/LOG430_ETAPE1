import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Location
from service_layer.location_repository import get_all_locations, get_location_by_name

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function", autouse=True)
def seed_data():
    session = TestingSessionLocal()
    session.query(Location).delete()
    session.commit()

    session.add_all([
        Location(name="Store A"),
        Location(name="store b"),
        Location(name="Warehouse Z"),
    ])
    session.commit()
    yield
    session.close()

@pytest.fixture(autouse=True)
def override_session(monkeypatch):
    monkeypatch.setattr("service_layer.location_repository.SessionLocal", TestingSessionLocal)

def test_get_all_locations():
    locations = get_all_locations()
    assert len(locations) == 3
    assert [loc.name for loc in locations] == ["Store A", "Warehouse Z", "store b"]

def test_get_location_by_name_case_insensitive():
    loc = get_location_by_name("STORE A")
    assert loc is not None
    assert loc.name == "Store A"

def test_get_location_by_name_not_found():
    loc = get_location_by_name("NotExist")
    assert loc is None
