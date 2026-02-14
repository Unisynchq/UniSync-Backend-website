import os
from unittest.mock import patch, MagicMock

# Set dummy environment variables
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_key"
os.environ["RESEND_API_KEY"] = "re_dummy_key"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

import pytest
from fastapi.testclient import TestClient

with patch("supabase.create_client"), patch("app.database.supabase"):
    from app.main import app

client = TestClient(app)

# Mock user dependency
mock_user = {
    "id": "user_123",
    "email": "test@example.com",
    "created_at": "2024-01-01"
}

@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer valid_token"}

@patch("app.api.deps.auth_service")
@patch("app.api.routes.forms_auth.form_service")
def test_create_form(mock_form_service, mock_auth_service, auth_header):
    # Mock auth
    mock_auth_service.get_user.return_value = MagicMock(id="user_123", email="test@example.com", created_at="2024-01-01")
    
    # Mock form service
    mock_form_service.create_form.return_value = {
        "id": "form_123",
        "owner_id": "user_123",
        "slug": "test-form",
        "title": "Test Form",
        "description": "Desc",
        "is_published": False,
        "created_at": "2024-01-01",
        "questions": []
    }
    
    payload = {"title": "Test Form", "description": "Desc"}
    response = client.post("/api/forms/", json=payload, headers=auth_header)
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Form"
    assert response.json()["owner_id"] == "user_123"

@patch("app.api.deps.auth_service")
@patch("app.api.routes.forms_auth.form_service")
def test_list_forms(mock_form_service, mock_auth_service, auth_header):
    mock_auth_service.get_user.return_value = MagicMock(id="user_123", email="test@example.com", created_at="2024-01-01")
    mock_form_service.list_user_forms.return_value = [
        {"id": "f1", "owner_id": "user_123", "title": "Form 1", "slug": "s1", "is_published": True, "created_at": "2024-01-01"}
    ]
    
    response = client.get("/api/forms/", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 1

@patch("app.api.deps.auth_service")
@patch("app.api.routes.forms_auth.form_service")
def test_get_dashboard_stats(mock_form_service, mock_auth_service, auth_header):
    mock_auth_service.get_user.return_value = MagicMock(id="user_123", email="test@example.com", created_at="2024-01-01")
    mock_form_service.get_dashboard_stats.return_value = {
        "total_forms": 5,
        "total_responses": 10,
        "published_forms_count": 2,
        "recent_responses_count": 3
    }
    
    response = client.get("/api/forms/stats", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["total_forms"] == 5

@patch("app.api.deps.auth_service")
@patch("app.api.routes.questions.form_service")
def test_add_question(mock_form_service, mock_auth_service, auth_header):
    mock_auth_service.get_user.return_value = MagicMock(id="user_123", email="test@example.com", created_at="2024-01-01")
    mock_form_service.add_question.return_value = {
        "id": "q1",
        "form_id": "f1",
        "text": "What is your name?",
        "type": "text",
        "order": 1,
        "options": None,
        "created_at": "..."
    }
    
    payload = {
        "form_id": "f1",
        "text": "What is your name?",
        "type": "text",
        "order": 1
    }
    response = client.post("/api/questions/", json=payload, headers=auth_header)
    assert response.status_code == 201
    assert response.json()["text"] == "What is your name?"

@patch("app.api.deps.auth_service")
@patch("app.api.routes.questions.form_service")
def test_delete_question_access_denied(mock_form_service, mock_auth_service, auth_header):
    mock_auth_service.get_user.return_value = MagicMock(id="user_123", email="test@example.com", created_at="2024-01-01")
    mock_form_service.delete_question.side_effect = Exception("Access denied")
    
    response = client.delete("/api/questions/q1", headers=auth_header)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
