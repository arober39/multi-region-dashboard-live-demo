# AI Performance Assistant

The Multi-Region Dashboard includes an AI-powered chat assistant that helps you understand your database performance metrics and provides optimization recommendations.

## Features

- **Context-Aware**: The assistant has access to your recent check data (latency, health metrics, etc.)
- **Performance Insights**: Ask about latency trends, regional comparisons, and optimization tips
- **Natural Language**: Chat naturally about your database performance
- **Real-time**: Powered by Ollama running locally on your machine

## Prerequisites

1. **Ollama** must be installed and running locally
2. The `llama3.2:latest` model must be available

### Installing Ollama

```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# Pull the llama3.2 model
ollama pull llama3.2:latest
```

## Usage

The chat interface is located in the main dashboard, just above the "Recent Check History" section.

### Example Questions

**Understanding Metrics:**
- "What is database latency?"
- "Explain cache hit ratio"
- "What does connection pooling mean?"

**Performance Analysis:**
- "Which region has the best performance?"
- "Why is my latency high?"
- "How can I improve my cache hit ratio?"

**Comparisons:**
- "Compare latency between US East and EU West"
- "Which region should I use for my application?"
- "What's causing the performance difference between regions?"

**Optimization:**
- "How can I reduce latency?"
- "What are best practices for connection pooling?"
- "Should I add more indexes?"

## How It Works

1. **User asks a question** in the chat interface
2. **System gathers context** from your recent check data (last 10 checks)
3. **Ollama processes the request** using llama3.2 with the context
4. **Assistant responds** with insights and recommendations

## Configuration

The chat integration is configured in `app/chat.py`:

```python
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:latest"
```

### Using a Different Model

If you prefer to use a different Ollama model:

1. Pull the model:
   ```bash
   ollama pull llama3.1:latest
   ```

2. Update `DEFAULT_MODEL` in `app/chat.py`:
   ```python
   DEFAULT_MODEL = "llama3.1:latest"
   ```

## API Endpoint

The chat functionality is exposed via:

```
POST /api/chat
Content-Type: application/json

{
  "message": "Your question here"
}
```

Response:
```json
{
  "response": "AI-generated response with context from your database metrics"
}
```

## Troubleshooting

### "Chat service error"
- Ensure Ollama is running: `ps aux | grep ollama`
- Check if the service is accessible: `curl http://localhost:11434/api/tags`
- Verify the model is installed: `ollama list`

### Slow Responses
- llama3.2 is optimized for speed, but responses may take 5-15 seconds
- Consider using a smaller model like `llama3.2:1b` for faster responses
- Ensure your machine has sufficient RAM (8GB+ recommended)

### Model Not Found
```bash
# Pull the required model
ollama pull llama3.2:latest

# Verify installation
ollama list
```

## Privacy

- **All processing is local**: No data is sent to external services
- **Context is session-based**: The assistant only sees recent check data from your current session
- **No data storage**: Chat history is not persisted to disk

## Performance

- **Average response time**: 5-15 seconds
- **Context limit**: Last 10 check results
- **Model size**: llama3.2 is ~2GB (good balance of speed and quality)
