"""Unit tests for location"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from location_repository import get_all_locations, get_location_by_name, get_location_by_id
from models import Location

@pytest.fixture
def fake_location():
    """Create fake location"""
    return Location(id=1, name="Magasin")

@patch("location_repository.SessionLocal")
def test_get_all_locations(mock_session_local, fake_location):
    """Test get locations"""
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value
    mock_query.order_by.return_value.all.return_value = [fake_location]
    mock_session_local.return_value = mock_session

    result = get_all_locations()

    assert result == [fake_location]
    mock_session.query.assert_called_once_with(Location)
    mock_session.close.assert_called_once()

@patch("location_repository.SessionLocal")
def test_get_location_by_name_found(mock_session_local, fake_location):
    """Test get location by name"""
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = fake_location
    mock_session_local.return_value = mock_session

    result = get_location_by_name("magasin")

    assert result == fake_location
    mock_query.filter.assert_called_once()
    mock_session.close.assert_called_once()

@patch("location_repository.SessionLocal")
def test_get_location_by_name_not_found(mock_session_local):
    """Test get location by name not found"""
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session_local.return_value = mock_session

    result = get_location_by_name("unknown")

    assert result is None
    mock_session.close.assert_called_once()

@patch("location_repository.SessionLocal")
def test_get_location_by_id(mock_session_local, fake_location):
    """Test get location by id"""
    mock_session = MagicMock()
    mock_session.query.return_value.get.return_value = fake_location
    mock_session_local.return_value = mock_session

    result = get_location_by_id(1)

    assert result == fake_location
    mock_session.query.assert_called_once_with(Location)
    mock_session.query.return_value.get.assert_called_once_with(1)
    mock_session.close.assert_called_once()
