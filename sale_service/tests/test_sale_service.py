"""Test suite for sale_repository module"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Product, Stock, Sale, Location
from sale_service import sale_repository

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
    monkeypatch.setattr("service_layer.sale_repository.SessionLocal", TestingSessionLocal)

@pytest.fixture(scope="function", autouse=True)
def clean_data():
    """Method to clean the data"""
    session = TestingSessionLocal()
    session.query(Sale).delete()
    session.query(Stock).delete()
    session.query(Product).delete()
    session.query(Location).delete()
    session.commit()
    yield
    session.close()

@pytest.fixture
def setup_inventory():
    """Method to set up inventory"""
    session = TestingSessionLocal()
    location = Location(name="Store X")
    product = Product(name="Widget", price=20.0, description="Test item")
    session.add_all([location, product])
    session.commit()

    stock = Stock(location_id=location.id, product_id=product.id, quantity=50)
    session.add(stock)
    session.commit()
    session.refresh(location)
    session.refresh(product)
    session.close()
    return {"location": location, "product": product}

def test_add_sale_success(setup_inventory):
    """Method to test add sale"""
    loc = setup_inventory["location"]
    prod = setup_inventory["product"]
    sale_repository.add_sale(prod.id, loc, 5)

    session = TestingSessionLocal()
    sales = session.query(Sale).all()
    stock = session.query(Stock).filter_by(location_id=loc.id, product_id=prod.id).first()
    session.close()

    assert len(sales) == 1
    assert stock.quantity == 45

def test_add_sale_insufficient_stock(setup_inventory):
    """Method to test add sale but insufficient stock"""
    loc = setup_inventory["location"]
    prod = setup_inventory["product"]
    sale_repository.add_sale(prod.id, loc, 100)

    session = TestingSessionLocal()
    sales = session.query(Sale).all()
    stock = session.query(Stock).filter_by(location_id=loc.id, product_id=prod.id).first()
    session.close()

    assert len(sales) == 0
    assert stock.quantity == 50

def test_get_sales_by_location(setup_inventory):
    """Method to test get sales by location"""
    loc = setup_inventory["location"]
    prod = setup_inventory["product"]
    sale_repository.add_sale(prod.id, loc, 10)

    sales, total = sale_repository.get_sales_by_location(loc)
    assert total == 1
    assert len(sales) == 1
    assert sales[0].product.name == "Widget"
    assert sales[0].location.name == "Store X"

def test_get_all_sales(setup_inventory):
    """Method to test get all sales"""
    loc = setup_inventory["location"]
    prod = setup_inventory["product"]
    sale_repository.add_sale(prod.id, loc, 3)

    all_sales = sale_repository.get_all_sales()
    assert len(all_sales) == 1
    assert all_sales[0].product_id == prod.id

def test_cancel_sale(setup_inventory):
    """Method to test cancel sale"""
    loc = setup_inventory["location"]
    prod = setup_inventory["product"]
    sale_repository.add_sale(prod.id, loc, 7)

    session = TestingSessionLocal()
    sale = session.query(Sale).first()
    sale_id = sale.id
    session.close()

    sale_repository.cancel_sale(sale_id)

    session = TestingSessionLocal()
    remaining_sales = session.query(Sale).filter_by(id=sale_id).all()
    stock = session.query(Stock).filter_by(location_id=loc.id, product_id=prod.id).first()
    session.close()

    assert len(remaining_sales) == 0
    assert stock.quantity == 50
