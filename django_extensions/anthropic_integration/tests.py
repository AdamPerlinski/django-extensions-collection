"""Tests for Anthropic Claude Integration."""

import pytest
from unittest.mock import MagicMock, patch

from .client import (
    AnthropicClient,
    chat_completion,
    text_completion,
    stream_completion,
)


class TestAnthropicClient:
    """Test cases for AnthropicClient."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.ANTHROPIC_API_KEY = 'sk-ant-test-key'
        settings.ANTHROPIC_DEFAULT_MODEL = 'claude-sonnet-4-20250514'
        settings.ANTHROPIC_MAX_TOKENS = 4096
        return settings

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create mock Anthropic client."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_settings, mock_anthropic_client):
        """Create AnthropicClient with mocked client."""
        with patch('django_extensions.anthropic_integration.client.get_anthropic_client', return_value=mock_anthropic_client):
            c = AnthropicClient()
            c._client = mock_anthropic_client
            return c

    def test_chat_simple(self, client, mock_anthropic_client):
        """Test simple chat."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = 'Hello! How can I help you?'
        mock_response.content = [mock_content]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = client.chat('Hello!')

        assert result == 'Hello! How can I help you?'
        mock_anthropic_client.messages.create.assert_called_once()

    def test_chat_with_system(self, client, mock_anthropic_client):
        """Test chat with system prompt."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = 'Response'
        mock_response.content = [mock_content]
        mock_anthropic_client.messages.create.return_value = mock_response

        client.chat('Hello!', system='You are a helpful assistant.')

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        assert call_kwargs['system'] == 'You are a helpful assistant.'

    def test_chat_with_temperature(self, client, mock_anthropic_client):
        """Test chat with temperature."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = 'Response'
        mock_response.content = [mock_content]
        mock_anthropic_client.messages.create.return_value = mock_response

        client.chat('Hello!', temperature=0.5)

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        assert call_kwargs['temperature'] == 0.5

    def test_chat_with_history(self, client, mock_anthropic_client):
        """Test chat with conversation history."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = 'I remember you are Bob!'
        mock_response.content = [mock_content]
        mock_anthropic_client.messages.create.return_value = mock_response

        history = [
            {'role': 'user', 'content': 'My name is Bob'},
            {'role': 'assistant', 'content': 'Nice to meet you, Bob!'}
        ]

        response, new_history = client.chat_with_history(
            'What is my name?',
            history=history
        )
