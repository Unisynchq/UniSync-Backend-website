import os
from unittest.mock import patch, MagicMock, AsyncMock

# Set dummy environment variables
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_key"
os.environ["RESEND_API_KEY"] = "re_dummy_key"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["GOOGLE_API_KEY"] = "sk-dummy-google-key"

import pytest
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks

with patch("supabase.create_client"), patch("app.database.supabase"):
    with patch("google.generativeai.configure"):
        from app.main import app

client = TestClient(app)

@patch("app.api.routes.forms.rate_limit_service.check_rate_limit")
@patch("app.services.forms.supabase")
@patch("app.services.ai.ai_service.model")
@patch("app.api.routes.forms.form_service")
def test_form_submission_triggers_ai(mock_form_service, mock_model, mock_supabase, mock_limit):
    # Mock rate limit
    mock_limit.return_value = (True, 10, MagicMock())
    
    # Mock public form lookup
    mock_form_service.get_public_form_by_slug.return_value = {
        "id": "form_123",
        "title": "Feedback Form",
        "questions": [{"id": "q1", "text": "How was it?"}]
    }
    
    # Mock submission result
    mock_form_service.submit_response.return_value = {
        "success": True,
        "message": "Response submitted successfully",
        "response_id": "resp_123"
    }

    # Execute submission
    payload = {
        "form_id": "form_123",
        "answers": {"q1": "It was great!"}
    }
    
    response = client.post("/api/f/feedback/submit", json=payload)
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Verify submit_response was called with background_tasks
    args, kwargs = mock_form_service.submit_response.call_args
    assert args[0] == "form_123"
    assert isinstance(args[2], BackgroundTasks)

@patch("app.services.ai.supabase")
@pytest.mark.asyncio
async def test_ai_analysis_logic(mock_supabase):
    from app.services.ai import ai_service
    
    # Patch the model on the existing ai_service instance
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"sentiment": "positive", "summary": "Great feedback", "key_insights": ["Fast", "Simple"], "flagged": false}'
    mock_model.generate_content.return_value = mock_response
    
    with patch.object(ai_service, 'model', mock_model):
        # Execute analysis
        await ai_service.analyze_submission(
            "resp_123", 
            "Test Form", 
            [{"id": "q1", "text": "Q1"}], 
            {"q1": "A1"}
        )
        
        # Verify Gemini was called
        mock_model.generate_content.assert_called_once()
        
        # Verify DB storage
        mock_supabase.table.assert_called_with("ai_analysis")
        mock_supabase.table().insert.assert_called_once()
        args, kwargs = mock_supabase.table().insert.call_args
        assert args[0]["response_id"] == "resp_123"
        assert args[0]["status"] == "completed"
        assert args[0]["raw_analysis"]["sentiment"] == "positive"
