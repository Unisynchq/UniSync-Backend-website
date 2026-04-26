import pytest
from unittest.mock import patch, MagicMock
from app.services.ai import ai_service
from app.schemas import AIAnalysisUpdate

def test_sanitize_prompts():
    """Verify malicious or massive inputs are truncated to prevent context flooding"""
    long_string = "A" * 6000
    sanitized = ai_service._sanitize_input(long_string)
    assert len(sanitized) == 5015  # 5000 + len("... [TRUNCATED]")
    assert sanitized.endswith("... [TRUNCATED]")
    
    # Normal input should be untouched
    short_string = "This app is great."
    assert ai_service._sanitize_input(short_string) == short_string

@patch('app.services.ai.supabase')
def test_create_pending_analysis(mock_supabase):
    """Verify that a pending record triggers correctly to the database"""
    # Mocking the Supabase chained call: supabase.table().insert().execute()
    mock_insert = MagicMock()
    mock_supabase.table.return_value.insert.return_value = mock_insert
    
    response_id = "test-123"
    result = ai_service.create_pending_analysis(response_id)
    
    assert result is True
    mock_supabase.table.assert_called_with("ai_analysis")
    mock_supabase.table().insert.assert_called_with({
        "response_id": response_id,
        "status": "pending"
    })
    mock_insert.execute.assert_called_once()

@patch('app.services.ai.genai.Client')
@patch('app.services.ai.supabase')
def test_analyze_submission_success(mock_supabase, mock_genai_client):
    """Verify complete analysis flow when LLM returns valid JSON"""
    # Bind the mock model to the service instance manually for this test
    # (assuming it initialized with one)
    mock_client_instance = MagicMock()
    ai_service.client = mock_client_instance
    
    # Mock LLM response mapping to our enforced schema
    mock_response = MagicMock()
    mock_response.text = '{"category":"Feedback","sentiment":"Positive","summary":"Good job.","actionable":false}'
    mock_client_instance.models.generate_content.return_value = mock_response
    
    # Mock Database Update
    mock_update = MagicMock()
    mock_supabase.table.return_value.update.return_value.eq.return_value = mock_update
    
    # Perform the action
    ai_service.analyze_submission(
        response_id="response-xyz",
        form_title="Beta Feedback",
        questions=[{"id": "q1", "text": "What do you like?"}],
        answers={"q1": "Everything."}
    )
    
    # Verify the background update called Supabase with 'completed'
    mock_supabase.table.assert_called_with("ai_analysis")
    update_arg = mock_supabase.table().update.call_args[0][0]
    assert update_arg["status"] == "completed"
    assert update_arg["raw_analysis"]["sentiment"] == "Positive"
    assert "error_log" not in update_arg # Should be excluded via exclude_none=True

@patch('app.services.ai.genai.Client')
@patch('app.services.ai.supabase')
def test_analyze_submission_handles_llm_failure(mock_supabase, mock_genai_client):
    """Verify that if the LLM crashes or fails, the database row is safely marked as failed"""
    mock_client_instance = MagicMock()
    ai_service.client = mock_client_instance
    
    # Force the LLM to raise an Exception
    mock_client_instance.models.generate_content.side_effect = Exception("API Quota Exceeded")
    
    mock_update = MagicMock()
    mock_supabase.table.return_value.update.return_value.eq.return_value = mock_update
    
    ai_service.analyze_submission(
        response_id="fail-test-id",
        form_title="Feedback",
        questions=[],
        answers={}
    )
    
    # Verify it updated the schema to failed
    update_arg = mock_supabase.table().update.call_args[0][0]
    assert update_arg["status"] == "failed"
    assert "API Quota Exceeded" in update_arg["error_log"]
