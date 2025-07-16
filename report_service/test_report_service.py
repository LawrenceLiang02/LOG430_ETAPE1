"""Test suite for report_service module functions"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Product, Sale, Stock, Location
from service_layer import report_service

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
    monkeypatch.setattr("service_layer.report_service.SessionLocal", TestingSessionLocal)


@pytest.fixture(scope="function", autouse=True)
def seed_data():
    """Method to set data"""
    session = TestingSessionLocal()
    session.query(Sale).delete()
    session.query(Stock).delete()
    session.query(Product).delete()
    session.query(Location).delete()
    session.commit()

    loc1 = Location(name="Store 1")
    loc2 = Location(name="Store 2")

    prod1 = Product(name="Apple", price=1.5, description="Fruit")
    prod2 = Product(name="Banana", price=0.8, description="Fruit")

    session.add_all([loc1, loc2, prod1, prod2])
    session.commit()

    sale1 = Sale(location_id=loc1.id, product_id=prod1.id, quantity=10)
    sale2 = Sale(location_id=loc2.id, product_id=prod2.id, quantity=5)
    session.add_all([sale1, sale2])

    stock1 = Stock(location_id=loc1.id, product_id=prod1.id, quantity=3)
    stock2 = Stock(location_id=loc2.id, product_id=prod2.id, quantity=120)
    session.add_all([stock1, stock2])

    session.commit()
    yield
    session.close()


def test_generate_sales_report_csv(monkeypatch):
    """Test CSV report generation and file output"""
    monkeypatch.setattr("service_layer.report_service.os.makedirs", lambda *args, **kwargs: None)

    filename = report_service.generate_sales_report_csv()
    assert filename.endswith(".csv")
    assert os.path.exists(filename)

    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
        assert "Rapport consolidé des ventes" in content
        assert "Ventes par magasin" in content
        assert "Top 5 produits les plus vendus" in content
        assert "Stock restant par magasin" in content


def test_get_store_performance_metrics():
    """Test store metrics including rupture and overstock"""
    revenue_by_store, total_sales, top_product, rupture, surstock = report_service.get_store_performance_metrics()

    assert len(revenue_by_store) == 2
    assert total_sales == 2
    assert top_product.name in {"Apple", "Banana"}
    assert len(rupture) == 1
    assert len(surstock) == 1
    assert rupture[0].quantity < 10
    assert surstock[0].quantity > 100
