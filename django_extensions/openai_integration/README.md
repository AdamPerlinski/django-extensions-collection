# OpenAI Integration

OpenAI API integration for Django.

## Installation

```bash
pip install openai
```

```python
INSTALLED_APPS = [
    'django_extensions.openai_integration',
]
```

## Configuration

```python
# settings.py
OPENAI_API_KEY = 'sk-...'
OPENAI_DEFAULT_MODEL = 'gpt-4'
OPENAI_DEFAULT_TEMPERATURE = 0.7
OPENAI_DEFAULT_MAX_TOKENS = 1000
```

## Usage

### Chat Completion

```python
from django_extensions.openai_integration import chat_completion

response = chat_completion([
    {'role': 'user', 'content': 'What is Django?'}
])

print(response)  # "Django is a high-level Python web framework..."
```

### OpenAIClient Class

```python
from django_extensions.openai_integration import OpenAIClient

client = OpenAIClient()

# Simple chat
response = client.chat('Explain REST APIs')

# With system prompt
response = client.chat(
    'Summarize this article',
    system_prompt='You are a helpful assistant that summarizes text concisely.'
)

# With conversation history
response = client.chat(messages=[
    {'role': 'system', 'content': 'You are a coding assistant.'},
    {'role': 'user', 'content': 'Write a Python function to sort a list'},
    {'role': 'assistant', 'content': 'def sort_list(lst): return sorted(lst)'},
    {'role': 'user', 'content': 'Now make it sort in reverse order'}
])
```

### Text Embeddings

```python
from django_extensions.openai_integration import get_embedding

embedding = get_embedding('Hello, world!')
# Returns list of floats [0.123, -0.456, ...]
```

### Image Generation

```python
from django_extensions.openai_integration import generate_image

image_url = generate_image(
    prompt='A sunset over mountains, digital art',
    size='1024x1024'
)
```

### Moderation

```python
from django_extensions.openai_integration import moderate

result = moderate('Some text to check')
if result['flagged']:
    print('Content flagged:', result['categories'])
```

### Streaming

```python
from django_extensions.openai_integration import stream_chat

for chunk in stream_chat([{'role': 'user', 'content': 'Tell me a story'}]):
    print(chunk, end='', flush=True)
```

### Function Calling

```python
response = client.chat(
    'What is the weather in Paris?',
    functions=[{
        'name': 'get_weather',
        'parameters': {
            'type': 'object',
            'properties': {'location': {'type': 'string'}}
        }
    }]
)
```

## License

MIT
