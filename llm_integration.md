# LLM Integration Approach

## Overview
The LLM integration system provides a flexible and extensible interface for connecting the personal agent with various Large Language Models. It supports multiple providers, handles authentication, manages rate limits, and provides consistent interfaces regardless of the underlying provider.

## Architecture

### LLM Client Layer
The main interface that the agent uses to interact with LLMs.

### Provider Adapters
Provider-specific implementations that translate generic requests to provider-specific APIs.

### Configuration Layer
Manages API keys, model preferences, and provider settings.

## Core Components

### LLM Client (`src/personal_agent/llm/client.py`)

#### Main Interface
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Message:
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class LLMResponse:
    content: str
    finish_reason: str
    usage: Dict[str, int]  # tokens used
    model: str

class LLMClient(ABC):
    @abstractmethod
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def stream_response(self, messages: List[Message], **kwargs):
        """Stream a response from the LLM."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
```

#### Implementation
```python
from typing import List, Optional
from .providers.base import LLMProvider
from ..config.settings import Config

class LLMClient:
    def __init__(self, config: Config):
        self.config = config
        self.provider = self._initialize_provider()
        self.rate_limiter = RateLimiter()
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize the appropriate provider based on configuration."""
        provider_name = self.config.llm.provider
        if provider_name == "openai":
            from .providers.openai import OpenAIProvider
            return OpenAIProvider(self.config.llm)
        elif provider_name == "anthropic":
            from .providers.anthropic import AnthropicProvider
            return AnthropicProvider(self.config.llm)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Generate a response from the LLM."""
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Add system message if not present
        if not any(m.role == "system" for m in messages):
            messages.insert(0, Message(
                role="system",
                content=self.config.llm.system_prompt or "You are a helpful assistant."
            ))
        
        # Generate response
        return self.provider.generate_response(messages, **kwargs)
    
    def stream_response(self, messages: List[Message], **kwargs):
        """Stream a response from the LLM."""
        self.rate_limiter.wait_if_needed()
        return self.provider.stream_response(messages, **kwargs)
```

## Provider Implementations

### Base Provider (`src/personal_agent/llm/providers/base.py`)

```python
from abc import ABC, abstractmethod
from typing import List
from ..client import Message, LLMResponse

class LLMProvider(ABC):
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def stream_response(self, messages: List[Message], **kwargs):
        """Stream a response from the LLM."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
```

### OpenAI Provider (`src/personal_agent/llm/providers/openai.py`)

```python
import openai
from typing import List
from .base import LLMProvider
from ..client import Message, LLMResponse

class OpenAIProvider(LLMProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = openai.OpenAI(api_key=config.api_key)
    
    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """Convert internal messages to OpenAI format."""
        return [{"role": m.role, "content": m.content} for m in messages]
    
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Generate a response from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model or "gpt-3.5-turbo",
                messages=self._convert_messages(messages),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                finish_reason=response.choices[0].finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=response.model
            )
        except Exception as e:
            raise LLMException(f"OpenAI API error: {str(e)}")
    
    def stream_response(self, messages: List[Message], **kwargs):
        """Stream a response from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model or "gpt-3.5-turbo",
                messages=self._convert_messages(messages),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
                **kwargs
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise LLMException(f"OpenAI API error: {str(e)}")
```

### Anthropic Provider (`src/personal_agent/llm/providers/anthropic.py`)

```python
import anthropic
from typing import List
from .base import LLMProvider
from ..client import Message, LLMResponse

class AnthropicProvider(LLMProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = anthropic.Anthropic(api_key=config.api_key)
    
    def _convert_messages(self, messages: List[Message]) -> tuple:
        """Convert internal messages to Anthropic format."""
        system_message = None
        conversation = []
        
        for message in messages:
            if message.role == "system":
                system_message = message.content
            else:
                conversation.append({"role": message.role, "content": message.content})
        
        return system_message, conversation
    
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Generate a response from Anthropic."""
        try:
            system_message, conversation = self._convert_messages(messages)
            
            response = self.client.messages.create(
                model=self.config.model or "claude-3-haiku-20240307",
                system=system_message,
                messages=conversation,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.content[0].text,
                finish_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                model=response.model
            )
        except Exception as e:
            raise LLMException(f"Anthropic API error: {str(e)}")
```

## Configuration Integration

### LLM Configuration (`src/personal_agent/config/settings.py`)

```python
@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = "You are a helpful assistant."
    rate_limit_requests: int = 60  # requests per minute
    rate_limit_period: int = 60  # seconds
```

## Rate Limiting

### Rate Limiter (`src/personal_agent/llm/rate_limiter.py`)

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests: int = 60, period: int = 60):
        self.max_requests = max_requests
        self.period = period
        self.requests = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old requests outside the period
        while self.requests and self.requests[0] <= now - self.period:
            self.requests.popleft()
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.period - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Record this request
        self.requests.append(now)
```

## Error Handling

### LLM Exceptions (`src/personal_agent/llm/exceptions.py`)

```python
class LLMException(Exception):
    """Base exception for LLM-related errors."""
    pass

class AuthenticationError(LLMException):
    """Raised when API authentication fails."""
    pass

class RateLimitError(LLMException):
    """Raised when rate limit is exceeded."""
    pass

class ModelError(LLMException):
    """Raised when there's an issue with the model."""
    pass
```

## Caching

### Response Caching (`src/personal_agent/llm/cache.py`)

```python
import hashlib
import json
from typing import List
from .client import Message

class LLmCache:
    def __init__(self, cache_backend=None):
        self.cache = cache_backend or {}
    
    def _generate_key(self, messages: List[Message], **kwargs) -> str:
        """Generate a cache key for the request."""
        key_data = {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "kwargs": kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, messages: List[Message], **kwargs):
        """Get cached response if available."""
        key = self._generate_key(messages, **kwargs)
        return self.cache.get(key)
    
    def set(self, messages: List[Message], response, **kwargs):
        """Cache a response."""
        key = self._generate_key(messages, **kwargs)
        self.cache[key] = response
```

## Streaming Support

### Streaming Implementation
- Support for streaming responses for real-time interaction
- Proper handling of partial responses
- Graceful handling of stream interruptions

## Multi-modal Support (Future)

### Image Processing
- Support for image inputs
- Vision model integration
- Image description and analysis

### Audio Processing
- Speech-to-text integration
- Text-to-speech capabilities
- Voice interaction support

## Model Management

### Model Selection
- Automatic model selection based on task
- Cost/performance optimization
- Fallback model support

### Model Switching
- Seamless switching between models
- State preservation during switches
- Performance comparison tools

## Monitoring and Analytics

### Usage Tracking
- Token usage monitoring
- Cost tracking per provider
- Performance metrics

### Performance Monitoring
- Response time tracking
- Error rate monitoring
- Model performance comparison

## Security Considerations

### API Key Management
- Secure storage of API keys
- Environment-based key loading
- Key rotation support

### Data Privacy
- Optional request/response logging
- Data anonymization
- Compliance with privacy regulations

## Extensibility

### Adding New Providers
1. Create a new provider class inheriting from LLMProvider
2. Implement the required methods
3. Add the provider to the factory in LLMClient
4. Update configuration documentation

### Custom Features
- Provider-specific parameters
- Custom preprocessing/postprocessing
- Specialized response handling