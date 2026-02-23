import pytest
from pydantic import ValidationError
from app.schemas import ResponseSubmitRequest, QuestionCreate, QuestionUpdate

def test_response_submit_validation():
    # Valid
    req = ResponseSubmitRequest(form_id="test_form", answers={"q1": "Answer", "q2": 10})
    assert req.form_id == "test_form"
    assert req.answers["q1"] == "Answer"

    # Empty answers should fail
    with pytest.raises(ValidationError):
        ResponseSubmitRequest(form_id="test_form", answers={})

    # Null value should pass for partial completion as per logic
    req = ResponseSubmitRequest(form_id="test_form", answers={"q1": None})
    assert req.answers["q1"] is None
    
    # Empty string keys should fail
    with pytest.raises(ValidationError):
        ResponseSubmitRequest(form_id="test_form", answers={"  ": "Answer"})

def test_question_create_validation():
    # Valid Text Question
    req = QuestionCreate(form_id="f1", text="Name?", type="text", order=0)
    assert req.type == "text"
    
    # Valid Select Question
    req = QuestionCreate(form_id="f1", text="Role?", type="select", order=1, options=["Admin", "User"])
    assert len(req.options) == 2
    
    # Select question without options should fail
    with pytest.raises(ValidationError):
        QuestionCreate(form_id="f1", text="Role?", type="select", order=1)
        
    # Text question WITH options should fail
    with pytest.raises(ValidationError):
        QuestionCreate(form_id="f1", text="Name?", type="text", order=0, options=["Option 1"])

def test_question_update_validation():
    # Update type to select without options should fail if both provided
    with pytest.raises(ValidationError):
        QuestionUpdate(type="select", options=[])
        
    # Update type to text with options should fail
    with pytest.raises(ValidationError):
        QuestionUpdate(type="text", options=["Option 1"])
