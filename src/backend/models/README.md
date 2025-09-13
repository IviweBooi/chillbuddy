# ChillBuddy Models Directory

This directory contains AI models and related configuration files for the ChillBuddy mental health chatbot.

## Directory Structure

```
models/
├── README.md                    # This file
├── model_config.json           # Model configuration and settings
├── GODEL-v1_1-base-seq2seq/    # GODEL model files (if downloaded locally)
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── vocab.txt
├── fallback_responses.json     # Fallback responses when AI model fails
├── conversation_templates.json # Pre-defined conversation templates
└── safety_filters.json         # Safety filtering rules and patterns
```

## Model Information

### Primary Model: GODEL-v1.1-base-seq2seq
- **Purpose**: Conversational AI for mental health support
- **Source**: Microsoft GODEL (Grounded Open Dialogue Language Model)
- **Size**: ~1.3GB
- **Usage**: Generate empathetic and contextually appropriate responses

### Model Loading Options

1. **Online Loading** (Recommended for development):
   - Load model directly from Hugging Face Hub
   - Requires internet connection
   - Automatic updates

2. **Local Loading** (Recommended for production):
   - Download model files to this directory
   - Faster loading times
   - Works offline
   - Better for deployment

## Configuration Files

### model_config.json
Contains model-specific settings:
- Model name and version
- Loading parameters
- Generation settings (temperature, max_length, etc.)
- Safety filtering options

### fallback_responses.json
Pre-written responses for when the AI model:
- Fails to load
- Generates inappropriate content
- Takes too long to respond
- Encounters errors

### conversation_templates.json
Structured conversation patterns for:
- Greeting messages
- Crisis intervention
- Mood check-ins
- Coping strategy suggestions
- Session endings

### safety_filters.json
Safety rules and filters:
- Inappropriate content detection
- Crisis keyword patterns
- Response validation rules
- Content moderation settings

## Setup Instructions

### For Development (Online Loading)
1. No additional setup required
2. Model will be downloaded automatically on first use
3. Ensure stable internet connection

### For Production (Local Loading)
1. Download GODEL model files:
   ```bash
   # Using Hugging Face CLI
   huggingface-cli download microsoft/GODEL-v1_1-base-seq2seq --local-dir ./GODEL-v1_1-base-seq2seq
   ```

2. Or download manually:
   - Visit: https://huggingface.co/microsoft/GODEL-v1_1-base-seq2seq
   - Download all files to `./GODEL-v1_1-base-seq2seq/` directory

3. Update `model_config.json` to use local path

## Model Usage Guidelines

### Mental Health Considerations
- Always validate AI responses for appropriateness
- Implement safety filters for crisis situations
- Provide fallback responses for sensitive topics
- Monitor model outputs for quality and safety

### Performance Optimization
- Use GPU acceleration when available
- Implement response caching for common queries
- Set appropriate generation parameters
- Monitor memory usage and response times

### Safety and Ethics
- Never rely solely on AI for crisis intervention
- Always provide human contact options
- Respect user privacy and data protection
- Regularly audit model outputs for bias

## Alternative Models

If GODEL is not suitable, consider these alternatives:

1. **DialoGPT**: Microsoft's conversational AI
2. **BlenderBot**: Facebook's open-domain chatbot
3. **T5**: Google's text-to-text transformer
4. **GPT-2**: OpenAI's language model (smaller versions)

## Troubleshooting

### Common Issues
1. **Model loading fails**: Check internet connection or local file paths
2. **Out of memory**: Reduce batch size or use smaller model
3. **Slow responses**: Consider model quantization or GPU acceleration
4. **Inappropriate responses**: Review and update safety filters

### Support
For model-related issues:
1. Check Hugging Face documentation
2. Review model-specific GitHub repositories
3. Consult mental health AI best practices
4. Test thoroughly before deployment

## License and Attribution

- GODEL model: MIT License (Microsoft)
- Ensure compliance with model licenses
- Attribute models appropriately in documentation
- Respect usage guidelines and restrictions