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
            history: List of previous messages
            system_prompt: System prompt
            **kwargs: Additional chat parameters

        Returns:
            tuple: (response, updated_history)
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': message})

        response = self.chat(messages=messages, **kwargs)

        # Update history
        new_history = history.copy() if history else []
        new_history.append({'role': 'user', 'content': message})
        new_history.append({'role': 'assistant', 'content': response})

        return response, new_history

    def chat_stream(self, message, system_prompt=None, model=None, **kwargs):
        """
        Stream a chat completion.

        Args:
            message: User message
            system_prompt: System prompt
            model: Model to use
            **kwargs: Additional parameters

        Yields:
            str: Chunks of the response
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': message})

        stream = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            stream=True,
            **kwargs
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def embed(self, text, model=None):
        """
        Create embeddings for text.

        Args:
            text: Text or list of texts to embed
            model: Embedding model to use

        Returns:
            list: Embedding vector(s)
        """
        if isinstance(text, str):
            text = [text]

        response = self.client.embeddings.create(
            model=model or self.default_embedding_model,
            input=text
        )

        if len(text) == 1:
            return response.data[0].embedding
        return [d.embedding for d in response.data]

    def generate_image(self, prompt, size='1024x1024', quality='standard',
                       n=1, model='dall-e-3', style='vivid'):
        """
        Generate an image.

        Args:
            prompt: Image description
            size: Image size ('1024x1024', '1792x1024', '1024x1792')
            quality: 'standard' or 'hd'
            n: Number of images
            model: Model to use
            style: 'vivid' or 'natural'

        Returns:
            list: List of image URLs or base64 data
        """
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
            style=style
        )

        return [img.url for img in response.data]

    def transcribe(self, audio_file, model='whisper-1', language=None,
                   response_format='text', **kwargs):
        """
        Transcribe audio to text.

        Args:
            audio_file: Audio file path or file object
            model: Whisper model
            language: Language code (optional)
            response_format: 'text', 'json', 'srt', 'vtt'
            **kwargs: Additional parameters

        Returns:
            str: Transcription
        """
        if isinstance(audio_file, str):
            audio_file = open(audio_file, 'rb')

        params = {
            'model': model,
            'file': audio_file,
            'response_format': response_format,
        }

        if language:
            params['language'] = language

        params.update(kwargs)

        return self.client.audio.transcriptions.create(**params)

    def moderate(self, text):
        """
        Check text for content policy violations.

        Args:
            text: Text to moderate

        Returns:
            dict: Moderation results
        """
        response = self.client.moderations.create(input=text)
        result = response.results[0]

        return {
            'flagged': result.flagged,
            'categories': dict(result.categories) if hasattr(result.categories, '__iter__') else result.categories,
            'scores': dict(result.category_scores) if hasattr(result.category_scores, '__iter__') else result.category_scores,
        }

    def function_call(self, message, functions, model=None, **kwargs):
        """
        Call with function definitions.

        Args:
            message: User message
            functions: List of function definitions
            model: Model to use
            **kwargs: Additional parameters

        Returns:
            dict: Function call info or message
        """
        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=[{'role': 'user', 'content': message}],
            tools=[{'type': 'function', 'function': f} for f in functions],
            **kwargs
        )

        choice = response.choices[0]
        if choice.message.tool_calls:
            return {
                'function_call': True,
                'calls': [
                    {
                        'name': tc.function.name,
                        'arguments': tc.function.arguments,
                    }
                    for tc in choice.message.tool_calls
                ]
            }
        return {'function_call': False, 'message': choice.message.content}


# Convenience functions

def chat_completion(messages, model=None, **kwargs):
    """Send a chat completion request."""
    client = OpenAIClient()
    return client.chat(messages=messages, model=model, **kwargs)


def text_completion(prompt, system_prompt=None, **kwargs):
    """Simple text completion."""
    client = OpenAIClient()
    return client.chat(prompt, system_prompt=system_prompt, **kwargs)


def create_embedding(text, model=None):
    """Create embeddings for text."""
    client = OpenAIClient()
    return client.embed(text, model=model)


def generate_image(prompt, **kwargs):
    """Generate an image from a prompt."""
    client = OpenAIClient()
    return client.generate_image(prompt, **kwargs)


def transcribe_audio(audio_file, **kwargs):
    """Transcribe audio to text."""
    client = OpenAIClient()
    return client.transcribe(audio_file, **kwargs)


def moderate_content(text):
    """Check text for policy violations."""
    client = OpenAIClient()
    return client.moderate(text)
