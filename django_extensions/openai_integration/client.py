"""
OpenAI Integration for Django.

Usage:
    # settings.py
    OPENAI_API_KEY = 'sk-...'
    OPENAI_ORGANIZATION = 'org-...'  # optional
    OPENAI_DEFAULT_MODEL = 'gpt-4'  # optional

    # Chat completion
    from django_extensions.openai_integration import chat_completion

    response = chat_completion(
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello!'}
        ]
    )
    print(response)  # Assistant's reply

    # Generate embeddings
    from django_extensions.openai_integration import create_embedding

    embedding = create_embedding('Hello world')
"""

from django.conf import settings


def get_openai_client():
    """Get configured OpenAI client."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai is required. Install it with: pip install openai")

    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set")

    organization = getattr(settings, 'OPENAI_ORGANIZATION', None)

    return OpenAI(api_key=api_key, organization=organization)


class OpenAIClient:
    """
    OpenAI API client wrapper.

    Usage:
        client = OpenAIClient()
        response = client.chat('Hello!')
        embedding = client.embed('Some text')
    """

    def __init__(self, api_key=None, organization=None, default_model=None):
        self._client = None
        self._api_key = api_key
        self._organization = organization
        self.default_model = default_model or getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-4o')
        self.default_embedding_model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

    @property
    def client(self):
        if self._client is None:
            if self._api_key:
                try:
                    from openai import OpenAI
                except ImportError:
                    raise ImportError("openai is required. Install it with: pip install openai")
                self._client = OpenAI(api_key=self._api_key, organization=self._organization)
            else:
                self._client = get_openai_client()
        return self._client

    def chat(self, message=None, system_prompt=None, model=None, temperature=0.7,
             max_tokens=None, messages=None, **kwargs):
        """
        Send a chat completion request.

        Args:
            message: User message (if not using messages param)
            system_prompt: System prompt
            model: Model to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            messages: Full message history (overrides message/system_prompt)
            **kwargs: Additional API parameters

        Returns:
            str: Assistant's response
        """
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            if message:
                messages.append({'role': 'user', 'content': message})

        params = {
            'model': model or self.default_model,
            'messages': messages,
            'temperature': temperature,
        }

        if max_tokens:
            params['max_tokens'] = max_tokens

        params.update(kwargs)

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    def chat_with_history(self, message, history=None, system_prompt=None, **kwargs):
        """
        Chat with conversation history.

        Args:
            message: New user message
