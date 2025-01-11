# Anthropic Integration

Anthropic Claude API integration for Django.

## Installation

```bash
pip install anthropic
```

```python
INSTALLED_APPS = [
    'django_extensions.anthropic_integration',
]
```

## Configuration

```python
# settings.py
ANTHROPIC_API_KEY = 'sk-ant-...'
ANTHROPIC_DEFAULT_MODEL = 'claude-3-sonnet-20240229'
ANTHROPIC_DEFAULT_MAX_TOKENS = 1024
```

## Usage

### Text Completion

```python
from django_extensions.anthropic_integration import text_completion

response = text_completion('Explain quantum computing in simple terms')
print(response)
```

### AnthropicClient Class

```python
from django_extensions.anthropic_integration import AnthropicClient

client = AnthropicClient()

# Simple chat
response = client.chat('What is machine learning?')

# With system prompt
response = client.chat(
    'Summarize this text',
    system_prompt='You are a concise summarizer. Keep responses under 100 words.'
)

# With conversation history
response = client.chat(messages=[
    {'role': 'user', 'content': 'Hello!'},
    {'role': 'assistant', 'content': 'Hello! How can I help?'},
    {'role': 'user', 'content': 'Tell me about Python'}
])
```

### Model Selection

```python
# Claude 3 Opus (most capable)
response = client.chat('Complex question', model='claude-3-opus-20240229')

# Claude 3 Sonnet (balanced)
response = client.chat('Question', model='claude-3-sonnet-20240229')

# Claude 3 Haiku (fastest)
response = client.chat('Quick question', model='claude-3-haiku-20240307')
```

### Streaming

```python
from django_extensions.anthropic_integration import stream_completion

for chunk in stream_completion('Tell me a story'):
    print(chunk, end='', flush=True)
```

### Token Counting

```python
from django_extensions.anthropic_integration import count_tokens

tokens = count_tokens('Hello, world!')
print(f'Token count: {tokens}')
```

### With Images

```python
import base64

with open('image.png', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.chat(
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'image', 'source': {'type': 'base64', 'data': image_data}},
            {'type': 'text', 'text': 'What is in this image?'}
        ]
    }]
)
```

## License

MIT
