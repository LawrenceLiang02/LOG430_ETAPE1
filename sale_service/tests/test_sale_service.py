"""Unit tests for sale_service"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sale_service import (
    add_sale,
    get_sales_by_location,
    get_all_sales,
    cancel_sale,
    get_product_from_api,
    get_stock_from_api,
    deduct_stock,
    get_location_by_name_from_api
)
from models import Sale


@pytest.fixture
def mock_sale():
    """Test sale service"""
    return Sale(id=1, product_id=1, location_id=1, quantity=2)


@pytest.fixture
def mock_location():
    """Test sale service"""
    return MagicMock(id=1, name="Magasin 1")


@patch("sale_service.requests.get")
def test_get_product_from_api_success(mock_get):
    """Test sale service"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "name": "Phone", "price": 200}
    result = get_product_from_api(1)
    assert result["name"] == "Phone"

@patch("sale_service.requests.get")
def test_get_product_from_api_failure(mock_get):
    """Test sale service"""
    mock_get.side_effect = Exception("Timeout")
    result = get_product_from_api(1)
    assert result is None

@patch("sale_service.requests.get")
def test_get_stock_from_api_success(mock_get):
    """Test sale service"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"quantity": 10}
    result = get_stock_from_api(1, 1)
    assert result["quantity"] == 10

@patch("sale_service.requests.get")
def test_get_stock_from_api_failure(mock_get):
    """Test sale service"""
    mock_get.side_effect = Exception("Fail")
    result = get_stock_from_api(1, 1)
    assert result is None

@patch("sale_service.requests.post")
def test_deduct_stock_success(mock_post):
    """Test sale service"""
    mock_post.return_value.status_code = 200
    assert deduct_stock(1, 1, 2) is True

@patch("sale_service.requests.post")
def test_deduct_stock_failure(mock_post):
    """Test sale service"""
    mock_post.side_effect = Exception("Fail")
    assert deduct_stock(1, 1, 2) is False


@patch("sale_service.SessionLocal")
@patch("sale_service.deduct_stock")
@patch("sale_service.get_stock_from_api")
@patch("sale_service.get_product_from_api")
def test_add_sale_success(mock_get_product, mock_get_stock, mock_deduct, mock_session_local, mock_location):
    """Test sale service"""
    mock_get_product.return_value = {"id": 1, "name": "Phone", "price": 300}
    mock_get_stock.return_value = {"quantity": 5}
    mock_deduct.return_value = True

    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    result = add_sale(1, {"id": 1, "name": "Magasin 1"}, 2)
    assert result is True
    mock_session.commit.assert_called_once()

@patch("sale_service.SessionLocal")
@patch("sale_service.get_product_from_api")
def test_add_sale_product_not_found(mock_get_product, mock_session_local):
    """Test sale service"""
    mock_get_product.return_value = None
    mock_session_local.return_value = MagicMock()
    result = add_sale(1, {"id": 1, "name": "Magasin 1"}, 2)
    assert result is False

@patch("sale_service.SessionLocal")
@patch("sale_service.get_product_from_api")
@patch("sale_service.get_stock_from_api")
def test_add_sale_insufficient_stock(mock_get_stock, mock_get_product, mock_session_local):
    """Test sale service"""
    mock_get_product.return_value = {"id": 1, "name": "Phone", "price": 100}
    mock_get_stock.return_value = {"quantity": 1}
    mock_session_local.return_value = MagicMock()
    result = add_sale(1, {"id": 1, "name": "Magasin 1"}, 3)
    assert result is False


@patch("sale_service.SessionLocal")
def test_get_all_sales(mock_session_local, mock_sale):
    """Test sale service"""
    mock_session = MagicMock()
    mock_session.query.return_value.options.return_value.all.return_value = [mock_sale]
    mock_session_local.return_value = mock_session

    result = get_all_sales()
    assert result == [mock_sale]


@patch("sale_service.SessionLocal")
def test_get_sales_by_location(mock_session_local, mock_sale, mock_location):
    """Test sale service"""
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value.options.return_value.filter_by.return_value
    mock_query.count.return_value = 1
    mock_query.offset.return_value.limit.return_value.all.return_value = [mock_sale]
    mock_session_local.return_value = mock_session

    results, total = get_sales_by_location(mock_location)
    assert len(results) == 1
    assert total == 1


@patch("sale_service.SessionLocal")
@patch("sale_service.requests.post")
def test_cancel_sale_success(mock_post, mock_session_local):
    """Test sale service"""
    sale = MagicMock()
    sale.id = 1
    sale.quantity = 2
    sale.product.id = 1
    sale.product.name = "Item"
    sale.location.name = "Magasin 1"

    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status = lambda: None

    mock_session = MagicMock()
    mock_session.get.return_value = sale
    mock_session_local.return_value = mock_session

    result = cancel_sale(1)
    assert result is True
    mock_session.delete.assert_called_once_with(sale)


@patch("sale_service.SessionLocal")
@patch("sale_service.requests.post")
def test_cancel_sale_stock_fail(mock_post, mock_session_local):
    """Test sale service"""
    sale = MagicMock()
    sale.id = 1
    sale.quantity = 2
    sale.product.id = 1
    sale.product.name = "Item"
    sale.location.name = "Magasin 1"

    mock_post.side_effect = Exception("API error")

    mock_session = MagicMock()
    mock_session.get.return_value = sale
    mock_session_local.return_value = mock_session

    result = cancel_sale(1)
    assert result is False


@patch("sale_service.requests.get")
def test_get_location_by_name_from_api_success(mock_get):
    """Test sale service"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "name": "M1"}
    result = get_location_by_name_from_api("M1")
    assert result["name"] == "M1"

@patch("sale_service.requests.get")
def test_get_location_by_name_from_api_failure(mock_get):
    """Test sale service"""
    mock_get.side_effect = Exception("Error")
    result = get_location_by_name_from_api("fail")
    assert result is None
