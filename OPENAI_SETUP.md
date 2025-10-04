# OpenAI Integration Setup

## What Changed

The app now uses **OpenAI GPT-3.5-turbo** to intelligently analyze candidates instead of simple keyword matching!

## Benefits

- **Intelligent matching**: AI understands context, not just keywords
- **Personalized explanations**: AI explains WHY candidates match
- **Better results**: AI considers skills, experience, and education holistically
- **Spanish responses**: All explanations are in Spanish for your Chilean clients

## Setup Instructions

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### 2. Add the Key to Your Environment

Open your `.env` file (create it if it doesn't exist in the project root):

```bash
# Add this line
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Restart the App

```bash
python -m streamlit run poc_demo.py
```

## How It Works

### With OpenAI (Recommended)
1. User asks: "Quien tiene experiencia en Python y data science?"
2. AI analyzes all candidates' skills, experience, descriptions
3. AI returns: 
   - Specific candidates that match
   - Detailed explanation of WHY they match
   - Professional response in Spanish

### Without OpenAI (Fallback)
- Uses basic keyword matching
- Returns all candidates with matching keywords
- Generic "Found X candidates" message

## Example AI Response

**User**: "Quien tiene magíster en finanzas?"

**AI**: 
```
🤖 Análisis AI:

He identificado 2 candidatos con magíster en finanzas:

1. Carlos Mendoza - Tiene un Magíster en Finanzas de la Universidad de Chile 
   y trabaja como Analista Financiero Senior en Banco Santander. Su experiencia 
   incluye modelamiento financiero y evaluación de riesgos.

2. Ana Herrera - Aunque no tiene específicamente un magíster en finanzas, es 
   Contador Auditor con especialización en consultoría financiera y normativa IFRS.

Encontré 2 candidatos relevantes:
```

## Cost

- OpenAI charges per token used
- Average cost per search: ~$0.002-0.01 USD
- For PoC/Demo: Very affordable
- For production: Consider caching or rate limiting

## Troubleshooting

**"Falling back to keyword search"**
- Check your OpenAI API key in `.env`
- Ensure the key is valid and has credits
- Check terminal for error messages

**API Key Issues**
- Make sure there are no spaces in the key
- Key should start with `sk-`
- Check OpenAI dashboard for API status

## Deployment Note

When deploying to Streamlit Cloud, add the `OPENAI_API_KEY` to your app's secrets:
1. Go to your app settings on Streamlit Cloud
2. Go to Secrets
3. Add: `OPENAI_API_KEY = "sk-your-key-here"`

