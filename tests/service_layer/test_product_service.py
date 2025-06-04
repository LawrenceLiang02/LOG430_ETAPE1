"""Module to test product service"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Product
from service_layer import product_repository

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Method to set up database"""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def override_session(monkeypatch):
    """Method to override session"""
    monkeypatch.setattr("service_layer.product_repository.SessionLocal", TestingSessionLocal)

@pytest.fixture(scope="function", autouse=True)
def clean_products():
    """<ethod to clean products"""
    session = TestingSessionLocal()
    session.query(Product).delete()
    session.commit()
    yield
    session.close()

def test_add_product():
    """Method to test add product"""
    product_repository.add_product("Test", 10.0, "Sample")
    session = TestingSessionLocal()
    products = session.query(Product).all()
    session.close()
    assert len(products) == 1
    assert products[0].name == "Test"

def test_get_products():
    """Method to test get product"""
    product_repository.add_product("Prod1", 5.0, "Desc1")
    product_repository.add_product("Prod2", 15.0, "Desc2")
    products = product_repository.get_products()
    assert len(products) == 2
    names = [p.name for p in products]
    assert "Prod1" in names
    assert "Prod2" in names

def test_search_product_by_id():
    """Method to test search product by id"""
    product_repository.add_product("Unique", 20.0, "FindMe")
    products = product_repository.get_products()
    product_id = products[0].id
    result = product_repository.search_product_by("id", str(product_id))
    assert len(result) == 1
    assert result[0].name == "Unique"

def test_search_product_by_name():
    """Method to test search product by name"""
    product_repository.add_product("Alpha", 8.0, "X")
    result = product_repository.search_product_by("name", "alp")
    assert result
    assert result[0].name == "Alpha"

def test_search_product_by_invalid_type():
    """Method to test search product invalid"""
    with pytest.raises(ValueError):
        product_repository.search_product_by("category", "tools")

def test_update_product_success():
    """Method to test update product"""
    product_repository.add_product("Old", 1.0, "Old Desc")
    prod = product_repository.get_products()[0]
    success, msg = product_repository.update_product(prod.id, "New", 9.0, "New Desc")
    assert success is True
    assert msg == "Produit mis à jour avec succès"
    updated = product_repository.get_products()[0]
    assert updated.name == "New"
    assert updated.price == 9.0
    assert updated.description == "New Desc"

def test_update_product_not_found():
    """Method to test update invalid product"""
    success, msg = product_repository.update_product(999, "X", 0.0, "X")
    assert success is False
    assert msg == "Produit introuvable"
