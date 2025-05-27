"""Tests"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Product, Sale

import service_layer.store_service as store_service

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def session():
    """Method to set up session"""
    engine = create_engine(TEST_DATABASE_URL)
    testing_session_local = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()

    # Patch SessionLocal in store_service
    store_service.SessionLocal = lambda: session

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)

def test_add_product(session):
    """Test to add product"""
    store_service.add_product("Banane", 1.99, 50)
    products = session.query(Product).all()

    assert len(products) == 1
    assert products[0].name == "Banane"

def test_add_sale_success(session):
    """Service layer test to add sale"""
    product = Product(name="Pomme", price=0.99, quantity=10)
    session.add(product)
    session.commit()

    store_service.add_sale(product.id, 3)

    updated_product = session.get(Product, product.id)
    sales = session.query(Sale).all()

    assert updated_product.quantity == 7
    assert len(sales) == 1
    assert sales[0].quantity == 3

def test_add_sale_insufficient_stock(session, capsys):
    """Test to add insufficiant stock should return error"""
    product = Product(name="Lait", price=2.5, quantity=2)
    session.add(product)
    session.commit()

    store_service.add_sale(product.id, 5)
    captured = capsys.readouterr()

    assert "Stock insuffisant" in captured.out
    assert session.query(Sale).count() == 0

def test_cancel_sale(session):
    """Test to cancel a sale and revert amounts"""
    product = Product(name="Pain", price=3.0, quantity=10)
    session.add(product)
    session.commit()

    sale = Sale(product=product, quantity=2)
    session.add(sale)
    product.quantity -= 2
    session.commit()

    store_service.cancel_sale(sale.id)

    updated_product = session.get(Product, product.id)
    assert updated_product.quantity == 10
    assert session.query(Sale).count() == 0
