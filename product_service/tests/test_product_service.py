"""Unit tests for product_repository"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from product_repository import (
    add_product,
    get_products,
    search_product_by,
    update_product,
    get_product_by_id
)
from models import Product

@pytest.fixture
def fake_product():
    return Product(id=1, name="Test Product", price=10.0, description="Sample description", category="Electronics")

@patch("product_repository.SessionLocal")
def test_add_product(mock_session_local):
    """Test adding a product"""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    add_product("Test", 9.99, "Test Description")

    mock_session.add.assert_called()
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()

@patch("product_repository.SessionLocal")
def test_get_products(mock_session_local, fake_product):
    """Test paginated product retrieval with sorting and optional category"""
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value
    mock_query.count.return_value = 1
    mock_query.offset.return_value.limit.return_value.all.return_value = [fake_product]
    mock_session_local.return_value = mock_session

    products, total = get_products(page=1, size=10, sort_field="id", sort_order="asc")

    assert total == 1
    assert len(products) == 1
    mock_session.close.assert_called_once()

@patch("product_repository.SessionLocal")
def test_search_product_by_id_found(mock_session_local, fake_product):
    """Test searching product by ID with result"""
    mock_session = MagicMock()
    mock_session.get.return_value = fake_product
    mock_session_local.return_value = mock_session

    result = search_product_by("id", "1")
    assert result == [fake_product]

@patch("product_repository.SessionLocal")
def test_search_product_by_id_not_found(mock_session_local):
    """Test searching product by ID without result"""
    mock_session = MagicMock()
    mock_session.get.return_value = None
    mock_session_local.return_value = mock_session

    result = search_product_by("id", "999")
    assert result == []

@patch("product_repository.SessionLocal")
def test_search_product_by_name(mock_session_local, fake_product):
    """Test searching product by name"""
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.all.return_value = [fake_product]
    mock_session_local.return_value = mock_session

    result = search_product_by("name", "Test")
    assert result == [fake_product]

@patch("product_repository.SessionLocal")
def test_search_product_by_invalid_type(mock_session_local):
    """Test invalid search type"""
    mock_session_local.return_value = MagicMock()
    with pytest.raises(ValueError):
        search_product_by("brand", "Samsung")

@patch("product_repository.SessionLocal")
def test_update_product_success(mock_session_local, fake_product):
    """Test updating a product successfully"""
    mock_session = MagicMock()
    mock_session.get.return_value = fake_product
    mock_session_local.return_value = mock_session

    success, message = update_product(1, "Updated", 20.0, "Updated Desc")

    assert success is True
    assert message == "Produit mis à jour avec succès"
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()

@patch("product_repository.SessionLocal")
def test_update_product_not_found(mock_session_local):
    """Test updating a non-existing product"""
    mock_session = MagicMock()
    mock_session.get.return_value = None
    mock_session_local.return_value = mock_session

    success, message = update_product(999, "X", 0, "Y")
    assert success is False
    assert message == "Produit introuvable"
    mock_session.close.assert_called_once()

@patch("product_repository.SessionLocal")
def test_get_product_by_id(mock_session_local, fake_product):
    """Test get product by ID"""
    mock_session = MagicMock()
    mock_session.query.return_value.get.return_value = fake_product
    mock_session_local.return_value = mock_session

    result = get_product_by_id(1)
    assert result == fake_product
    mock_session.close.assert_called_once()
