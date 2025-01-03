"""
Anthropic Claude Integration for Django.

Usage:
    # settings.py
    ANTHROPIC_API_KEY = 'sk-ant-...'
    ANTHROPIC_DEFAULT_MODEL = 'claude-sonnet-4-20250514'

    # Chat completion
    from django_extensions.anthropic_integration import chat_completion

    response = chat_completion(
        messages=[{'role': 'user', 'content': 'Hello!'}],
        system='You are a helpful assistant.'
    )
    print(response)

    # Simple text completion
    from django_extensions.anthropic_integration import text_completion

    response = text_completion('Explain quantum computing in simple terms.')
"""

from django.conf import settings


def get_anthropic_client():
    """Get configured Anthropic client."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic is required. Install it with: pip install anthropic")

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY must be set")

    return anthropic.Anthropic(api_key=api_key)


class AnthropicClient:
    """
    Anthropic Claude API client wrapper.

    Usage:
        client = AnthropicClient()
        response = client.chat('Hello!')

        # With streaming
        for chunk in client.chat_stream('Tell me a story'):
            print(chunk, end='')
    """

    def __init__(self, api_key=None, default_model=None):
        self._client = None
        self._api_key = api_key
        self.default_model = default_model or getattr(
            settings, 'ANTHROPIC_DEFAULT_MODEL', 'claude-sonnet-4-20250514'
        )
        self.default_max_tokens = getattr(settings, 'ANTHROPIC_MAX_TOKENS', 4096)

    @property
    def client(self):
        if self._client is None:
            if self._api_key:
                try:
                    import anthropic
                except ImportError:
                    raise ImportError("anthropic is required. Install it with: pip install anthropic")
                self._client = anthropic.Anthropic(api_key=self._api_key)
            else:
                self._client = get_anthropic_client()
        return self._client

    def chat(self, message=None, system=None, model=None, max_tokens=None,
             temperature=None, messages=None, **kwargs):
        """
        Send a message to Claude.

        Args:
            message: User message (if not using messages param)
            system: System prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            messages: Full message list (overrides message param)
            **kwargs: Additional API parameters

        Returns:
            str: Claude's response
        """
        if messages is None:
            messages = []
            if message:
                messages.append({'role': 'user', 'content': message})

        params = {
            'model': model or self.default_model,
            'max_tokens': max_tokens or self.default_max_tokens,
            'messages': messages,
        }

        if system:
            params['system'] = system

        if temperature is not None:
            params['temperature'] = temperature

        params.update(kwargs)

        response = self.client.messages.create(**params)
        return response.content[0].text

    def chat_with_history(self, message, history=None, system=None, **kwargs):
        """
        Chat with conversation history.

        Args:
            message: New user message
            history: List of previous messages
            system: System prompt
            **kwargs: Additional chat parameters

        Returns:
            tuple: (response, updated_history)
        """
        messages = []
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': message})

        response = self.chat(messages=messages, system=system, **kwargs)

        # Update history
        new_history = history.copy() if history else []
        new_history.append({'role': 'user', 'content': message})
        new_history.append({'role': 'assistant', 'content': response})

        return response, new_history

    def chat_stream(self, message, system=None, model=None, max_tokens=None,
                    messages=None, **kwargs):
        """
        Stream a response from Claude.

        Args:
            message: User message
            system: System prompt
            model: Model to use
            max_tokens: Maximum tokens
            messages: Full message list
            **kwargs: Additional parameters

        Yields:
            str: Chunks of the response
        """
        if messages is None:
            messages = [{'role': 'user', 'content': message}]

        params = {
            'model': model or self.default_model,
            'max_tokens': max_tokens or self.default_max_tokens,
            'messages': messages,
        }

        if system:
            params['system'] = system

        params.update(kwargs)

        with self.client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                yield text

    def vision(self, prompt, image_url=None, image_base64=None, image_media_type='image/jpeg',
               system=None, **kwargs):
        """
        Send an image for analysis.

        Args:
            prompt: Question about the image
            image_url: URL of the image
            image_base64: Base64 encoded image data
            image_media_type: MIME type of image
            system: System prompt
            **kwargs: Additional parameters

        Returns:
            str: Claude's response about the image
        """
        if image_url:
            image_content = {
                'type': 'image',
                'source': {
                    'type': 'url',
                    'url': image_url,
                }
            }
        elif image_base64:
            image_content = {
                'type': 'image',
                'source': {
                    'type': 'base64',
                    'media_type': image_media_type,
                    'data': image_base64,
                }
            }
        else:
            raise ValueError("Either image_url or image_base64 must be provided")

        messages = [{
            'role': 'user',
            'content': [
                image_content,
                {'type': 'text', 'text': prompt}
            ]
        }]

        return self.chat(messages=messages, system=system, **kwargs)

    def tool_use(self, message, tools, system=None, model=None, **kwargs):
        """
        Use tools/functions with Claude.

        Args:
            message: User message
            tools: List of tool definitions
            system: System prompt
            model: Model to use
            **kwargs: Additional parameters

        Returns:
            dict: Response with potential tool use
        """
        params = {
            'model': model or self.default_model,
            'max_tokens': kwargs.pop('max_tokens', self.default_max_tokens),
            'messages': [{'role': 'user', 'content': message}],
            'tools': tools,
        }

        if system:
            params['system'] = system

        params.update(kwargs)

        response = self.client.messages.create(**params)

        result = {
            'stop_reason': response.stop_reason,
            'content': []
        }

        for block in response.content:
            if block.type == 'text':
                result['content'].append({
                    'type': 'text',
                    'text': block.text
                })
            elif block.type == 'tool_use':
                result['content'].append({
                    'type': 'tool_use',
                    'id': block.id,
                    'name': block.name,
                    'input': block.input
                })

        return result

    def count_tokens(self, text, model=None):
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for
            model: Model to use for counting

        Returns:
            int: Token count
        """
        return self.client.count_tokens(
            text,
            model=model or self.default_model
        )


# Convenience functions

def chat_completion(messages, system=None, model=None, **kwargs):
    """Send a chat completion request to Claude."""
    client = AnthropicClient()
    return client.chat(messages=messages, system=system, model=model, **kwargs)


def text_completion(prompt, system=None, **kwargs):
    """Simple text completion with Claude."""
    client = AnthropicClient()
    return client.chat(prompt, system=system, **kwargs)


def stream_completion(prompt, system=None, **kwargs):
    """Stream a completion from Claude."""
    client = AnthropicClient()
    return client.chat_stream(prompt, system=system, **kwargs)


def analyze_image(prompt, image_url=None, image_base64=None, **kwargs):
    """Analyze an image with Claude."""
    client = AnthropicClient()
    return client.vision(prompt, image_url=image_url, image_base64=image_base64, **kwargs)
