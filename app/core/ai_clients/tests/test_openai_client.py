import pytest
from unittest.mock import patch, MagicMock
from app.core.ai_clients.openai_client import OpenAIClient
from app.core.ai_clients import openai_client

# Patch ApiKey.get_openai_key to always return a dummy key unless explicitly patched in a test
@pytest.fixture(autouse=True)
def patch_apikey(monkeypatch):
    monkeypatch.setattr(openai_client.ApiKey, "get_openai_key", staticmethod(lambda: "dummy-key"))

# --- __init__ ---
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_init_api_key_present(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = 'key'
    client = OpenAIClient()
    assert client.api_key_missing is False
    mock_openai.assert_called_once_with(api_key='key')

@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_init_api_key_missing(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = None
    client = OpenAIClient()
    assert client.api_key_missing is True
    assert client.client is None

# --- get_banned_words ---
@patch('app.core.ai_clients.openai_client.BannedWord')
def test_get_banned_words(mock_bw):
    mock_bw.get_all.return_value = [MagicMock(word='bad'), MagicMock(word='evil')]
    client = OpenAIClient()
    result = client.get_banned_words()
    assert result == ['bad', 'evil']

# --- contains_banned ---
def test_contains_banned_true():
    client = OpenAIClient()
    assert client.contains_banned('This is bad', ['bad']) is True

def test_contains_banned_false():
    client = OpenAIClient()
    assert client.contains_banned('This is good', ['bad']) is False

# --- moderate_content ---
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_moderate_content_api_key_missing(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = None
    client = OpenAIClient()
    result = client.moderate_content('text')
    assert result is False

@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_moderate_content_flagged(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.results = [MagicMock(flagged=True)]
    mock_client.moderations.create.return_value = mock_resp
    mock_openai.return_value = mock_client
    client = OpenAIClient()
    client.client = mock_client
    client.api_key_missing = False
    result = client.moderate_content('text')
    assert result is True

@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_moderate_content_not_flagged(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.results = [MagicMock(flagged=False)]
    mock_client.moderations.create.return_value = mock_resp
    mock_openai.return_value = mock_client
    client = OpenAIClient()
    client.client = mock_client
    client.api_key_missing = False
    result = client.moderate_content('text')
    assert result is False

# --- get_persona_prompt ---
@patch('app.core.ai_clients.openai_client.Settings')
def test_get_persona_prompt_found(mock_settings):
    mock_settings.return_value.get_personas.return_value = [{'id': 1, 'system_prompt': 'hi'}]
    client = OpenAIClient()
    result = client.get_persona_prompt(1, 2)
    assert result == 'hi'

@patch('app.core.ai_clients.openai_client.Settings')
def test_get_persona_prompt_not_found(mock_settings):
    mock_settings.return_value.get_personas.return_value = [{'id': 2, 'system_prompt': 'hi'}]
    client = OpenAIClient()
    result = client.get_persona_prompt(1, 2)
    assert result == 'You are a helpful assistant.'

# --- get_chat_response ---
@patch('app.core.ai_clients.openai_client.Settings')
@patch('app.core.ai_clients.openai_client.Message')
@patch('app.core.ai_clients.openai_client.BannedWord')
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_get_chat_response_api_key_missing(mock_openai, mock_apikey, mock_bw, mock_msg, mock_settings):
    mock_apikey.get_openai_key.return_value = None
    client = OpenAIClient()
    result = client.get_chat_response('hi', 1, 1)
    assert 'OpenAI API key is not set' in result

@patch('app.core.ai_clients.openai_client.Settings')
@patch('app.core.ai_clients.openai_client.Message')
@patch('app.core.ai_clients.openai_client.BannedWord')
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_get_chat_response_contains_banned(mock_openai, mock_apikey, mock_bw, mock_msg, mock_settings):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_bw.get_all.return_value = [MagicMock(word='bad')]
    client = OpenAIClient()
    client.api_key_missing = False
    client.client = MagicMock()
    client.get_banned_words = lambda: ['bad']
    client.contains_banned = lambda text, banned: True
    result = client.get_chat_response('bad', 1, 1)
    assert 'can\'t help' in result

@patch('app.core.ai_clients.openai_client.Settings')
@patch('app.core.ai_clients.openai_client.Message')
@patch('app.core.ai_clients.openai_client.BannedWord')
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_get_chat_response_normal(mock_openai, mock_apikey, mock_bw, mock_msg, mock_settings):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_bw.get_all.return_value = [MagicMock(word='bad')]
    mock_settings.return_value.get_child_instructions.return_value = ''
    mock_settings.return_value.get_personas.return_value = [{'id': 1, 'system_prompt': 'hi'}]
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content='hello'))]
    mock_client.chat.completions.create.return_value = mock_resp
    mock_openai.return_value = mock_client
    mock_msg.get_by_conversation_id.return_value = []
    client = OpenAIClient()
    client.api_key_missing = False
    client.client = mock_client
    client.get_banned_words = lambda: []
    client.contains_banned = lambda text, banned: False
    result = client.get_chat_response('hi', 1, 1)
    assert result == 'hello'

@patch('app.core.ai_clients.openai_client.Settings')
@patch('app.core.ai_clients.openai_client.Message')
@patch('app.core.ai_clients.openai_client.BannedWord')
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_get_chat_response_output_banned(mock_openai, mock_apikey, mock_bw, mock_msg, mock_settings):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_bw.get_all.return_value = [MagicMock(word='bad')]
    mock_settings.return_value.get_child_instructions.return_value = ''
    mock_settings.return_value.get_personas.return_value = [{'id': 1, 'system_prompt': 'hi'}]
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content='bad'))]
    mock_client.chat.completions.create.return_value = mock_resp
    mock_openai.return_value = mock_client
    mock_msg.get_by_conversation_id.return_value = []
    client = OpenAIClient()
    client.api_key_missing = False
    client.client = mock_client
    client.get_banned_words = lambda: ['bad']
    client.contains_banned = lambda text, banned: text == 'bad'
    result = client.get_chat_response('hi', 1, 1)
    assert 'can\'t help' in result

@patch('app.core.ai_clients.openai_client.Settings')
@patch('app.core.ai_clients.openai_client.Message')
@patch('app.core.ai_clients.openai_client.BannedWord')
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_get_chat_response_exception(mock_openai, mock_apikey, mock_bw, mock_msg, mock_settings):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_bw.get_all.return_value = [MagicMock(word='bad')]
    mock_settings.return_value.get_child_instructions.return_value = ''
    mock_settings.return_value.get_personas.return_value = [{'id': 1, 'system_prompt': 'hi'}]
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception('fail')
    mock_openai.return_value = mock_client
    mock_msg.get_by_conversation_id.return_value = []
    client = OpenAIClient()
    client.api_key_missing = False
    client.client = mock_client
    client.get_banned_words = lambda: []
    client.contains_banned = lambda text, banned: False
    result = client.get_chat_response('hi', 1, 1)
    assert 'error' in result.lower()

# --- summarize_text ---
@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_summarize_text_api_key_missing(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = None
    client = OpenAIClient()
    result = client.summarize_text('text')
    assert result == '(No summary)'

@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_summarize_text_normal(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content='summary'))]
    mock_client.chat.completions.create.return_value = mock_resp
    mock_openai.return_value = mock_client
    client = OpenAIClient()
    client.client = mock_client
    client.api_key_missing = False
    result = client.summarize_text('text')
    assert result == 'summary'

@patch('app.core.ai_clients.openai_client.ApiKey')
@patch('app.core.ai_clients.openai_client.OpenAI')
def test_summarize_text_exception(mock_openai, mock_apikey):
    mock_apikey.get_openai_key.return_value = 'key'
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception('fail')
    mock_openai.return_value = mock_client
    client = OpenAIClient()
    client.client = mock_client
    client.api_key_missing = False
    result = client.summarize_text('text')
    assert result == '(No summary)' 