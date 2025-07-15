"""Test suite for stock_repository module"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Product, Stock, StockRequest, Location
from stock_service import stock_repository

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup the in-memory test database"""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def override_session(monkeypatch):
    """Override the production session with test session"""
    monkeypatch.setattr("service_layer.stock_repository.SessionLocal", TestingSessionLocal)

@pytest.fixture(scope="function", autouse=True)
def clean_data():
    """Clean all tables before each test"""
    session = TestingSessionLocal()
    session.query(StockRequest).delete()
    session.query(Stock).delete()
    session.query(Product).delete()
    session.query(Location).delete()
    session.commit()
    yield
    session.close()

@pytest.fixture
def setup_inventory():
    """Insert initial locations, product, and stock"""
    session = TestingSessionLocal()
    centre = Location(name="Centre logistique")
    store = Location(name="Magasin A")
    product = Product(name="TestItem", price=10.0, description="test")
    session.add_all([centre, store, product])
    session.commit()

    stock = Stock(location_id=centre.id, product_id=product.id, quantity=100)
    session.add(stock)
    session.commit()

    data = {
        "centre_id": centre.id,
        "store_id": store.id,
        "product_id": product.id
    }
    session.close()
    return data

def test_add_stock_to_centre_logistique(setup_inventory):
    """Test adding stock to Centre Logistique"""
    session = TestingSessionLocal()
    centre = session.get(Location, setup_inventory["centre_id"])
    product = session.get(Product, setup_inventory["product_id"])
    result = stock_repository.add_stock(product.id, centre, 50)
    stock = session.query(Stock).filter_by(location_id=centre.id, product_id=product.id).first()
    session.close()
    assert result is True
    assert stock.quantity == 150

def test_add_stock_to_store_from_centre(setup_inventory):
    """Test transferring stock from Centre to store"""
    session = TestingSessionLocal()
    centre = session.get(Location, setup_inventory["centre_id"])
    store = session.get(Location, setup_inventory["store_id"])
    product = session.get(Product, setup_inventory["product_id"])
    result = stock_repository.add_stock(product.id, store, 30)
    centre_stock = session.query(Stock).filter_by(location_id=centre.id, product_id=product.id).first()
    store_stock = session.query(Stock).filter_by(location_id=store.id, product_id=product.id).first()
    session.close()
    assert result is True
    assert centre_stock.quantity == 70
    assert store_stock.quantity == 30

def test_add_stock_insufficient_in_centre(setup_inventory):
    """Test stock transfer with insufficient quantity in Centre"""
    session = TestingSessionLocal()
    store = session.get(Location, setup_inventory["store_id"])
    product = session.get(Product, setup_inventory["product_id"])
    result = stock_repository.add_stock(product.id, store, 200)
    session.close()
    assert result is False

def test_get_stock(setup_inventory):
    """Test stock retrieval for a location"""
    session = TestingSessionLocal()
    centre = session.get(Location, setup_inventory["centre_id"])
    product = session.get(Product, setup_inventory["product_id"])
    stocks = stock_repository.get_stock(centre)
    session.close()
    assert len(stocks) == 1
    assert stocks[0].product.name == product.name

def test_create_stock_request(setup_inventory):
    """Test creating a stock request"""
    session = TestingSessionLocal()
    store = session.get(Location, setup_inventory["store_id"])
    product = session.get(Product, setup_inventory["product_id"])
    result = stock_repository.create_stock_request(store.id, product.id, 20)
    requests = session.query(StockRequest).all()
    session.close()
    assert result is True
    assert len(requests) == 1

def test_get_all_stock_requests(setup_inventory):
    """Test retrieval of all stock requests"""
    session = TestingSessionLocal()
    store = session.get(Location, setup_inventory["store_id"])
    product = session.get(Product, setup_inventory["product_id"])
    stock_repository.create_stock_request(store.id, product.id, 10)
    session.close()
    requests = stock_repository.get_all_stock_requests()
    assert len(requests) == 1
    assert requests[0].location.name == "Magasin A"

def test_fulfill_stock_request_success(setup_inventory):
    """Test fulfilling a valid stock request"""
    session = TestingSessionLocal()
    store = session.get(Location, setup_inventory["store_id"])
    centre = session.get(Location, setup_inventory["centre_id"])
    product = session.get(Product, setup_inventory["product_id"])

    stock_repository.create_stock_request(store.id, product.id, 20)
    request_id = session.query(StockRequest.id).first()[0]
    session.close()

    result, msg = stock_repository.fulfill_stock_request(request_id)

    session = TestingSessionLocal()
    centre_stock = session.query(Stock).filter_by(location_id=centre.id, product_id=product.id).scalar()
    store_stock = session.query(Stock).filter_by(location_id=store.id, product_id=product.id).scalar()
    session.close()

    assert result is True
    assert "envoyées à" in msg
    assert centre_stock.quantity == 80
    assert store_stock.quantity == 20

def test_fulfill_stock_request_insufficient_stock(setup_inventory):
    """Test fulfilling a stock request with insufficient stock"""
    session = TestingSessionLocal()
    store = session.get(Location, setup_inventory["store_id"])
    product = session.get(Product, setup_inventory["product_id"])

    stock_repository.create_stock_request(store.id, product.id, 999)
    request_id = session.query(StockRequest.id).first()[0]
    session.close()

    result, msg = stock_repository.fulfill_stock_request(request_id)

    assert result is False
    assert "insuffisant" in msg
