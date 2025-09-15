# tests/test_comparator.py

import pytest
from backend.core.comparator import compare_with_latest_report_of_type, _perform_comparison
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@patch("backend.core.comparator._perform_comparison")
def test_compare_latest_report_by_type_with_no_previous(mock_perform, mock_db):
    # Setup mock to return None (no previous report)
    mock_db.query().filter().order_by().first.return_value = None
    
    # Call the function
    result = compare_with_latest_report_of_type(mock_db, "radiologia", "Test report text")
    
    # Verify the function returned the expected result
    assert result["status"] == "nessun confronto disponibile"
    assert "Non esiste un referto precedente" in result["explanation"]
    
    # Verify _perform_comparison was not called
    mock_perform.assert_not_called()

@patch("backend.db.crud.get_most_recent_report_text_by_type")
@patch("backend.core.comparator._perform_comparison")
def test_compare_latest_report_by_type_with_previous(mock_perform, mock_get_report, mock_db):
    # Setup mocks
    mock_get_report.return_value = "Previous report text"
    mock_perform.return_value = {"status": "migliorata", "explanation": "Test explanation"}
    
    # Call the function
    result = compare_with_latest_report_of_type(mock_db, "radiologia", "New report text")
    
    # Verify correct functions were called
    mock_get_report.assert_called_once_with(mock_db, "radiologia")
    mock_perform.assert_called_once_with("Previous report text", "New report text")
    
    # Verify the function returned the expected result
    assert result["status"] == "migliorata"
    assert result["explanation"] == "Test explanation"
