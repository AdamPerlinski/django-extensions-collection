"""Tests for OpenAI Integration."""

import pytest
from unittest.mock import MagicMock, patch

from .client import (
    OpenAIClient,
    chat_completion,
    text_completion,
    create_embedding,
    generate_image,
)


class TestOpenAIClient:
    """Test cases for OpenAIClient."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.OPENAI_API_KEY = 'sk-test-key'
        settings.OPENAI_ORGANIZATION = 'org-test'
        settings.OPENAI_DEFAULT_MODEL = 'gpt-4'
        return settings

    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_settings, mock_openai_client):
        """Create OpenAIClient with mocked client."""
        with patch('django_extensions.openai_integration.client.get_openai_client', return_value=mock_openai_client):
            c = OpenAIClient()
            c._client = mock_openai_client
            return c

    def test_chat_simple(self, client, mock_openai_client):
        """Test simple chat completion."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Hello! How can I help?'
        mock_openai_client.chat.completions.create.return_value = mock_response

        result = client.chat('Hello!')

        assert result == 'Hello! How can I help?'
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_chat_with_system_prompt(self, client, mock_openai_client):
        """Test chat with system prompt."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Response'
        mock_openai_client.chat.completions.create.return_value = mock_response

        client.chat('Hello!', system_prompt='You are a helpful assistant.')

        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'You are a helpful assistant.'

    def test_chat_with_history(self, client, mock_openai_client):
        """Test chat with conversation history."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'I remember!'
        mock_openai_client.chat.completions.create.return_value = mock_response

        history = [
            {'role': 'user', 'content': 'My name is Bob'},
            {'role': 'assistant', 'content': 'Nice to meet you, Bob!'}
        ]

        response, new_history = client.chat_with_history(
            'What is my name?',
            history=history
        )

        assert response == 'I remember!'
        assert len(new_history) == 4
        assert new_history[-1]['role'] == 'assistant'

    def test_chat_stream(self, client, mock_openai_client):
        """Test streaming chat."""
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock()]
        chunk1.choices[0].delta.content = 'Hello'

        chunk2 = MagicMock()
        chunk2.choices = [MagicMock()]
        chunk2.choices[0].delta.content = ' World'

        mock_openai_client.chat.completions.create.return_value = [chunk1, chunk2]

        chunks = list(client.chat_stream('Hi!'))

        assert chunks == ['Hello', ' World']
        mock_openai_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        assert call_kwargs['stream'] is True
