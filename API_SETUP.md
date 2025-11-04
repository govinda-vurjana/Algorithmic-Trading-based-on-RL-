# Anthropic API Setup Guide

## Overview
This project uses **Anthropic's Claude** API for generating trading strategies.

## Quick Setup

### 1. Create `.env` File
Copy the example file:
```bash
cp .env.example .env
```

### 2. Configure Your API Key

Edit `.env` and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

## Model Used

| Model | Description |
|-------|-------------|
| `claude-sonnet-4-20250514` | Claude Sonnet 4 - Latest model optimized for code generation |

## How It Works

The `TradingPipeline` class initializes the Anthropic client:

```python
pipeline = TradingPipeline()
```

When you run the pipeline, you'll see:
```
🤖 Using Anthropic Claude
📦 Model: claude-sonnet-4-20250514
```

## Getting Your API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env`

## Troubleshooting

### "No API key found"
- Make sure your `.env` file exists in the project root
- Check that the API key variable is named `ANTHROPIC_API_KEY`
- Ensure there are no extra spaces or quotes in the key

### "Rate limit exceeded"
- Anthropic has rate limits on API usage
- Consider reducing the number of concurrent trials
- Wait a few minutes and try again
- Check your API usage dashboard at console.anthropic.com

### "Invalid API key"
- Verify the key is copied correctly (no extra spaces)
- Check that the key hasn't expired
- Ensure the key starts with `sk-ant-`

## Cost Considerations

Anthropic charges per token usage. Approximate costs per run (10 trials):

- **Claude Sonnet 4**: ~$0.15-0.35 per run

Costs vary based on:
- Number of trials
- Prompt length
- Response length
- Model temperature settings

## Best Practices

1. **Keep keys secure**: Never commit `.env` to version control
2. **Monitor usage**: Check your API dashboard regularly at console.anthropic.com
3. **Set spending limits**: Configure billing alerts on the Anthropic dashboard
4. **Test with fewer trials**: Use 3-5 trials for testing before full runs
