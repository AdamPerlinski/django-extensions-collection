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

    def test_embed_single(self, client, mock_openai_client):
        """Test single text embedding."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_openai_client.embeddings.create.return_value = mock_response

        result = client.embed('Hello world')

        assert result == [0.1, 0.2, 0.3]

    def test_embed_multiple(self, client, mock_openai_client):
        """Test multiple text embeddings."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(), MagicMock()]
        mock_response.data[0].embedding = [0.1, 0.2]
        mock_response.data[1].embedding = [0.3, 0.4]
        mock_openai_client.embeddings.create.return_value = mock_response

        result = client.embed(['Hello', 'World'])

        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]

    def test_generate_image(self, client, mock_openai_client):
        """Test image generation."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].url = 'https://example.com/image.png'
        mock_openai_client.images.generate.return_value = mock_response

        result = client.generate_image('A cat sitting on a couch')

        assert result == ['https://example.com/image.png']
        call_kwargs = mock_openai_client.images.generate.call_args[1]
        assert call_kwargs['prompt'] == 'A cat sitting on a couch'

    def test_transcribe(self, client, mock_openai_client):
        """Test audio transcription."""
        mock_openai_client.audio.transcriptions.create.return_value = 'Hello world'

        with patch('builtins.open', MagicMock()):
            result = client.transcribe('/path/to/audio.mp3')

        assert result == 'Hello world'

    def test_moderate(self, client, mock_openai_client):
        """Test content moderation."""
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_result.flagged = False
        mock_result.categories = {'hate': False, 'violence': False}
        mock_result.category_scores = {'hate': 0.01, 'violence': 0.02}
        mock_response.results = [mock_result]
        mock_openai_client.moderations.create.return_value = mock_response

        result = client.moderate('Hello world')

        assert result['flagged'] is False

    def test_function_call(self, client, mock_openai_client):
        """Test function calling."""
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = 'get_weather'
        mock_tool_call.function.arguments = '{"location": "NYC"}'
        mock_choice.message.tool_calls = [mock_tool_call]
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        functions = [
            {
                'name': 'get_weather',
                'description': 'Get weather for a location',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'}
                    }
                }
            }
        ]

        result = client.function_call("What's the weather in NYC?", functions)

        assert result['function_call'] is True
        assert result['calls'][0]['name'] == 'get_weather'


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.OPENAI_API_KEY = 'sk-test-key'
        return settings

    def test_chat_completion_function(self, mock_settings):
        """Test chat_completion function."""
        with patch('django_extensions.openai_integration.client.get_openai_client') as mock_get:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = 'Response'
            mock_client.chat.completions.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = chat_completion([
                {'role': 'user', 'content': 'Hello'}
            ])

            assert result == 'Response'

    def test_text_completion_function(self, mock_settings):
        """Test text_completion function."""
        with patch('django_extensions.openai_integration.client.get_openai_client') as mock_get:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = 'Response'
            mock_client.chat.completions.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = text_completion('Hello!', system_prompt='Be helpful')

            assert result == 'Response'

    def test_create_embedding_function(self, mock_settings):
        """Test create_embedding function."""
        with patch('django_extensions.openai_integration.client.get_openai_client') as mock_get:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3]
            mock_client.embeddings.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = create_embedding('Hello')

            assert result == [0.1, 0.2, 0.3]

    def test_generate_image_function(self, mock_settings):
        """Test generate_image function."""
        with patch('django_extensions.openai_integration.client.get_openai_client') as mock_get:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].url = 'https://example.com/img.png'
            mock_client.images.generate.return_value = mock_response
            mock_get.return_value = mock_client

            result = generate_image('A cat')

            assert result == ['https://example.com/img.png']
