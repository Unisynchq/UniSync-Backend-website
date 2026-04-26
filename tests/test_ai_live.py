import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.ai import ai_service
from app.schemas import AILiveAnalyzeRequest

@pytest.mark.asyncio
@patch('app.services.ai.litellm.acompletion')
async def test_analyze_live_input_success(mock_acompletion):
    """Verify that live analysis correctly combines results from two models"""
    # Mock settings to have hf_token
    ai_service.hf_token = "test-hf-token"
    
    # Setup mock responses for both quality and detection
    # quality response
    mock_quality_response = MagicMock()
    mock_quality_response.choices = [
        MagicMock(message=MagicMock(content='{"indicator": "green", "suggestion": "Perfect answer!"}'))
    ]
    
    # detection response
    mock_detection_response = MagicMock()
    mock_detection_response.choices = [
        MagicMock(message=MagicMock(content='{"probability": 0.1, "is_ai_generated": false}'))
    ]
    
    # Configure acompletion to return different values on sequential calls
    mock_acompletion.side_effect = [mock_quality_response, mock_detection_response]
    
    request = AILiveAnalyzeRequest(
        form_id="form-123",
        question_id="q-456",
        question_text="Tell us about yourself.",
        answer_text="I am a passionate software engineer with 5 years of experience."
    )
    
    result = await ai_service.analyze_live_input(request)
    
    assert result.quality_score.indicator == "green"
    assert result.ai_detection.is_ai_generated is False
    assert result.ai_detection.probability == 0.1
    assert "authentic" in result.ai_detection.feedback

@pytest.mark.asyncio
@patch('app.services.ai.litellm.acompletion')
async def test_analyze_live_input_handles_ai_detection(mock_acompletion):
    """Verify that it correctly flags AI-generated text"""
    ai_service.hf_token = "test-hf-token"
    
    # quality response (Amber)
    mock_quality_response = MagicMock()
    mock_quality_response.choices = [
        MagicMock(message=MagicMock(content='{"indicator": "amber", "suggestion": "Try adding more detail."}'))
    ]
    
    # detection response (High AI probability)
    mock_detection_response = MagicMock()
    mock_detection_response.choices = [
        MagicMock(message=MagicMock(content='{"probability": 0.95, "is_ai_generated": true}'))
    ]
    
    mock_acompletion.side_effect = [mock_quality_response, mock_detection_response]
    
    request = AILiveAnalyzeRequest(
        form_id="form-123",
        question_id="q-456",
        question_text="What is your favorite food?",
        answer_text="As an AI, I do not have personal preferences, but many people enjoy pizza."
    )
    
    result = await ai_service.analyze_live_input(request)
    
    assert result.ai_detection.is_ai_generated is True
    assert result.ai_detection.probability == 0.95
    assert "automated" in result.ai_detection.feedback

@pytest.mark.asyncio
@patch('app.services.ai.litellm.acompletion')
async def test_analyze_live_input_handles_errors(mock_acompletion):
    """Verify that it falls back gracefully if models fail"""
    ai_service.hf_token = "test-hf-token"
    
    # Force acompletion to fail
    mock_acompletion.side_effect = Exception("HF API Error")
    
    request = AILiveAnalyzeRequest(
        form_id="form-123",
        question_id="q-456",
        question_text="Broken test.",
        answer_text="Whatever."
    )
    
    result = await ai_service.analyze_live_input(request)
    
    # Should fall back to defaults defined in _get_quality_score and _get_ai_detection
    assert result.quality_score.indicator == "amber"
    assert result.ai_detection.is_ai_generated is False
    assert "unavailable" in result.ai_detection.feedback
