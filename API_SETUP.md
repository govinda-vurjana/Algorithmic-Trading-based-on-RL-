# API Provider Setup Guide

## Overview
This project now supports both **OpenAI** and **Anthropic** API providers. You can easily switch between them using environment variables.

## Quick Setup

### 1. Create `.env` File
Copy the example file:
```bash
cp .env.example .env
```

### 2. Configure Your API Provider

Edit `.env` and set your preferred provider:

#### Option A: Use OpenAI (GPT-4o)
```bash
API_PROVIDER="openai"
OPENAI_API_KEY="sk-your-openai-key-here"
```

#### Option B: Use Anthropic (Claude 3.5 Sonnet)
```bash
API_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

## Supported Models

| Provider | Model | Description |
|----------|-------|-------------|
| OpenAI | `gpt-4o` | Latest GPT-4 Optimized model |
| Anthropic | `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet (latest) |

## How It Works

The `TradingPipeline` class automatically detects the `API_PROVIDER` environment variable and initializes the appropriate client:

```python
# Automatically selects the right API based on .env
pipeline = TradingPipeline()
```

When you run the pipeline, you'll see which provider is being used:
```
🤖 Using API Provider: OPENAI
📦 Model: gpt-4o
```

## Getting API Keys

### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy and paste into `.env`

### Anthropic
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env`

## Switching Between Providers

Simply change the `API_PROVIDER` value in your `.env` file:

```bash
# Switch to Anthropic
API_PROVIDER="anthropic"

# Switch back to OpenAI
API_PROVIDER="openai"
```

No code changes required! The pipeline will automatically use the correct API.

## Troubleshooting

### "No API key found"
- Make sure your `.env` file exists in the project root
- Check that the API key variable name matches the provider (OPENAI_API_KEY or ANTHROPIC_API_KEY)
- Ensure there are no extra spaces or quotes in the key

### "Rate limit exceeded"
- Both providers have rate limits
- Consider reducing the number of concurrent trials
- Wait a few minutes and try again
- Check your API usage dashboard

### "Invalid API key"
- Verify the key is copied correctly (no extra spaces)
- Check that the key hasn't expired
- Ensure you're using the correct key for the selected provider

## Cost Considerations

Both APIs charge per token usage. Approximate costs per run (10 trials):

- **OpenAI GPT-4o**: ~$0.10-0.30 per run
- **Anthropic Claude 3.5**: ~$0.15-0.35 per run

Costs vary based on:
- Number of trials
- Prompt length
- Response length
- Model temperature settings

## Best Practices

1. **Keep keys secure**: Never commit `.env` to version control
2. **Monitor usage**: Check your API dashboard regularly
3. **Set spending limits**: Configure billing alerts on provider dashboards
4. **Test with fewer trials**: Use 3-5 trials for testing before full runs
5. **Use appropriate model**: Choose based on your needs and budget
