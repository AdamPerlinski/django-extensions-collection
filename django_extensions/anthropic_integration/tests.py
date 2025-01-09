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

        assert response == 'I remember you are Bob!'
        assert len(new_history) == 4
        assert new_history[-1]['role'] == 'assistant'

    def test_chat_stream(self, client, mock_anthropic_client):
        """Test streaming chat."""
        mock_stream = MagicMock()
        mock_stream.text_stream = ['Hello', ' ', 'World']
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_anthropic_client.messages.stream.return_value = mock_stream

        chunks = list(client.chat_stream('Hi!'))

        assert chunks == ['Hello', ' ', 'World']

    def test_vision_with_url(self, client, mock_anthropic_client):
        """Test vision with image URL."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = 'I see a cat.'
        mock_response.content = [mock_content]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = client.vision(
            'What is in this image?',
            image_url='https://example.com/cat.jpg'
        )

        assert result == 'I see a cat.'
        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        assert call_kwargs['messages'][0]['content'][0]['type'] == 'image'

    def test_vision_with_base64(self, client, mock_anthropic_client):
        """Test vision with base64 image."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = 'I see a dog.'
        mock_response.content = [mock_content]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = client.vision(
            'What is this?',
            image_base64='base64data',
            image_media_type='image/png'
        )

        assert result == 'I see a dog.'

    def test_vision_requires_image(self, client):
        """Test vision requires image."""
        with pytest.raises(ValueError):
            client.vision('What is this?')

    def test_tool_use(self, client, mock_anthropic_client):
        """Test tool use."""
        mock_response = MagicMock()
        mock_response.stop_reason = 'tool_use'

        mock_tool_block = MagicMock()
        mock_tool_block.type = 'tool_use'
        mock_tool_block.id = 'tool_123'
        mock_tool_block.name = 'get_weather'
        mock_tool_block.input = {'location': 'NYC'}
        mock_response.content = [mock_tool_block]

        mock_anthropic_client.messages.create.return_value = mock_response

        tools = [{
            'name': 'get_weather',
            'description': 'Get weather for a location',
            'input_schema': {
                'type': 'object',
                'properties': {
                    'location': {'type': 'string'}
                }
            }
        }]

        result = client.tool_use("What's the weather in NYC?", tools)

        assert result['stop_reason'] == 'tool_use'
        assert result['content'][0]['name'] == 'get_weather'
        assert result['content'][0]['input'] == {'location': 'NYC'}


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.ANTHROPIC_API_KEY = 'sk-ant-test-key'
        return settings

    def test_chat_completion_function(self, mock_settings):
        """Test chat_completion function."""
        with patch('django_extensions.anthropic_integration.client.get_anthropic_client') as mock_get:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_content = MagicMock()
            mock_content.text = 'Response'
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = chat_completion([
                {'role': 'user', 'content': 'Hello'}
            ])

            assert result == 'Response'

    def test_text_completion_function(self, mock_settings):
        """Test text_completion function."""
        with patch('django_extensions.anthropic_integration.client.get_anthropic_client') as mock_get:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_content = MagicMock()
            mock_content.text = 'Response'
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = text_completion('Hello!', system='Be helpful')

            assert result == 'Response'

    def test_stream_completion_function(self, mock_settings):
        """Test stream_completion function."""
        with patch('django_extensions.anthropic_integration.client.get_anthropic_client') as mock_get:
            mock_client = MagicMock()
            mock_stream = MagicMock()
            mock_stream.text_stream = ['Hello', ' World']
            mock_stream.__enter__ = MagicMock(return_value=mock_stream)
            mock_stream.__exit__ = MagicMock(return_value=False)
            mock_client.messages.stream.return_value = mock_stream
            mock_get.return_value = mock_client

            chunks = list(stream_completion('Hi!'))

            assert chunks == ['Hello', ' World']
