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

