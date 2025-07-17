"""Unit tests for stock_service.py"""

import sys
import os
from unittest.mock import patch, MagicMock

# Ensure proper import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from stock_service import (
    get_location_by_name_from_api,
    get_product_by_id_from_api,
    add_stock,
    get_stock,
    create_stock_request,
    get_all_stock_requests,
    fulfill_stock_request,
    get_location_by_id_from_api,
    get_stock_by_ids,
    deduct_stock_quantity
)
from models import Stock, StockRequest


@pytest.fixture
def fake_location():
    return MagicMock(id=1, name="Magasin 1")


@pytest.fixture
def fake_stock():
    return Stock(product_id=1, location_id=1, quantity=10)


@patch("stock_service.requests.get")
def test_get_location_by_name_from_api_success(mock_get):
    """Test successful API call to retrieve a location by name"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "name": "Magasin"}
    result = get_location_by_name_from_api("Magasin")
    assert result["name"] == "Magasin"


@patch("stock_service.requests.get")
def test_get_product_by_id_from_api_success(mock_get):
    """Test successful API call to retrieve product by ID"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "name": "Laptop"}
    result = get_product_by_id_from_api(1)
    assert result["name"] == "Laptop"


@patch("stock_service.SessionLocal")
@patch("stock_service.get_location_by_id_from_api")
def test_add_stock_to_logistic_center(mock_get_location, mock_session_local):
    """Test adding stock directly to logistic center"""
    mock_get_location.return_value = {"id": 1, "name": "Centre logistique"}

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_session_local.return_value = mock_session

    result = add_stock(1, 1, 5)
    assert result is True
    mock_session.commit.assert_called_once()


@patch("stock_service.SessionLocal")
@patch("stock_service.get_location_by_id_from_api")
@patch("stock_service.get_location_by_name_from_api")
def test_add_stock_transfer_from_logistic(mock_log_name, mock_get_id, mock_session_local):
    """Test stock transfer from logistic center to another location"""
    mock_get_id.return_value = {"id": 2, "name": "Magasin 1"}
    mock_log_name.return_value = {"id": 1, "name": "Centre logistique"}

    mock_session = MagicMock()
    # Simulate logistic stock has enough quantity
    mock_session.query.return_value.filter_by.return_value.first.side_effect = [
        MagicMock(quantity=10),  # logistic_stock
        None                    # target_stock
    ]
    mock_session_local.return_value = mock_session

    result = add_stock(1, 2, 5)
    assert result is True


@patch("stock_service.SessionLocal")
def test_get_stock(mock_session_local, fake_location, fake_stock):
    """Test retrieving stock levels for a location"""
    mock_session = MagicMock()
    mock_session.query.return_value.options.return_value.filter_by.return_value.all.return_value = [fake_stock]
    mock_session_local.return_value = mock_session

    result = get_stock(fake_location)
    assert result == [fake_stock]


@patch("stock_service.SessionLocal")
def test_create_stock_request_success(mock_session_local):
    """Test creating a stock request"""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    result = create_stock_request(1, 1, 5)
    assert result is True


@patch("stock_service.SessionLocal")
def test_get_all_stock_requests(mock_session_local):
    """Test fetching all stock requests"""
    mock_session = MagicMock()
    mock_session.query.return_value.options.return_value.all.return_value = ["req1"]
    mock_session_local.return_value = mock_session

    result = get_all_stock_requests()
    assert result == ["req1"]


@patch("stock_service.SessionLocal")
@patch("stock_service.get_product_by_id_from_api")
@patch("stock_service.get_location_by_name_from_api")
def test_fulfill_stock_request_success(mock_get_loc_name, mock_get_prod, mock_session_local):
    """Test successful stock fulfillment from a stock request"""
    mock_get_loc_name.side_effect = [
        {"id": 99, "name": "Centre logistique"},
        {"id": 1, "name": "Magasin 1"}
    ]
    mock_get_prod.return_value = {"name": "Item"}

    mock_request = MagicMock(product_id=1, location_id=2, quantity=3)
    mock_session = MagicMock()
    mock_session.query.return_value.get.return_value = mock_request
    mock_session.query.return_value.filter_by.return_value.first.side_effect = [
        MagicMock(quantity=10),  # source_stock
        None                     # dest_stock
    ]
    mock_session_local.return_value = mock_session

    success, message = fulfill_stock_request(1)
    assert success is True
    assert "envoyées" in message


@patch("stock_service.SessionLocal")
def test_get_location_by_id_from_api_success(mock_session_local):
    """Test successful location lookup by ID via API"""
    with patch("stock_service.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 1, "name": "Magasin"}
        result = get_location_by_id_from_api(1)
        assert result["name"] == "Magasin"


@patch("stock_service.SessionLocal")
def test_get_stock_by_ids(mock_session_local, fake_stock):
    """Test retrieving a specific stock by product and location"""
    mock_session = MagicMock()
    mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = fake_stock
    mock_session_local.return_value = mock_session

    result = get_stock_by_ids(1, 1)
    assert result == fake_stock


@patch("stock_service.SessionLocal")
def test_deduct_stock_quantity_success(mock_session_local):
    """Test deducting quantity from existing stock"""
    mock_stock = MagicMock(quantity=10)
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_stock
    mock_session_local.return_value = mock_session

    success, message = deduct_stock_quantity(1, 1, 3)
    assert success is True
    assert "3 unités déduites" in message
    assert mock_stock.quantity == 7


@patch("stock_service.SessionLocal")
def test_deduct_stock_quantity_insufficient(mock_session_local):
    """Test failure when trying to deduct more than available stock"""
    mock_stock = MagicMock(quantity=2)
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_stock
    mock_session_local.return_value = mock_session

    success, message = deduct_stock_quantity(1, 1, 5)
    assert success is False
    assert "Stock insuffisant" in message


@patch("stock_service.SessionLocal")
def test_deduct_stock_quantity_not_found(mock_session_local):
    """Test failure when stock is not found for deduction"""
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_session_local.return_value = mock_session

    success, message = deduct_stock_quantity(1, 1, 5)
    assert success is False
    assert "Stock introuvable" in message
