import os
from unittest.mock import patch, MagicMock

# Set dummy environment variables
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_key"
os.environ["RESEND_API_KEY"] = "re_dummy_key"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

import pytest
from fastapi.testclient import TestClient

# Mock Supabase before importing app
with patch("supabase.create_client"), patch("app.database.supabase"):
    from app.main import app
    from app.api.deps import get_current_user

client = TestClient(app)

# Mock user
mock_user = MagicMock()
mock_user.id = "user_123"
mock_user.email = "test@example.com"

# Override dependency
app.dependency_overrides[get_current_user] = lambda: mock_user

@patch("app.services.responses.supabase")
def test_list_form_responses(mock_supabase):
    # Mock database response
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": "resp_1",
            "form_id": "form_123",
            "answers": {"q1": "Answer 1"},
            "metadata": {},
            "created_at": "2026-02-23T10:00:00Z"
        }
    ]
    # Chain the mock calls correctly
    mock_supabase.table().select().eq().order().execute.return_value = mock_result
    
    response = client.get("/api/responses/form/form_123")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "resp_1"

@patch("app.services.responses.supabase")
def test_get_response_detail(mock_supabase):
    # Mock database response for response detail
    mock_resp_result = MagicMock()
    mock_resp_result.data = [{
        "id": "resp_1",
        "form_id": "form_123",
        "answers": {"q1": "Answer 1"},
        "metadata": {},
        "created_at": "2026-02-23T10:00:00Z"
    }]
    
    # Mock database response for analysis
    mock_anal_result = MagicMock()
    mock_anal_result.data = [{
        "id": "anal_1",
        "response_id": "resp_1",
        "status": "completed",
        "raw_analysis": {"sentiment": "positive"},
        "created_at": "2026-02-23T10:05:00Z"
    }]
    
    # Configure mock behavior for multiple calls
    # Note: Each call to .table() might return a new mock if not careful.
    # But here we are patching app.services.responses.supabase
    mock_supabase.table().select().eq().execute.side_effect = [mock_resp_result, mock_anal_result]
    
    response = client.get("/api/responses/detail/resp_1")
    
    assert response.status_code == 200
    assert response.json()["id"] == "resp_1"
    assert response.json()["ai_analysis"]["status"] == "completed"

@patch("app.services.responses.supabase")
def test_get_response_not_found(mock_supabase):
    # Mock empty database response
    mock_result = MagicMock()
    mock_result.data = []
    mock_supabase.table().select().eq().execute.return_value = mock_result
    
    response = client.get("/api/responses/detail/non_existent")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
