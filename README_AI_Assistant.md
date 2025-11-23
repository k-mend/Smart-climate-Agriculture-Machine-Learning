# 🤖 Agribricks AI Assistant

An AI-powered agricultural advisor that provides expert farming advice using Groq's Llama3-70B model and LangChain.

## 🌟 Features

- **Expert Agricultural Advice**: Context-aware farming guidance
- **Crop Management**: Planting, growing, and harvesting advice
- **Pest & Disease Control**: Natural and effective solutions
- **Soil Health**: Fertility management and improvement tips
- **Weather-Based Decisions**: Climate-smart farming practices
- **Multi-language Support**: Responses in different languages
- **Confidence Scoring**: Reliability indicators for advice

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_ai_only.txt
```

### 2. Get Groq API Key
- Visit [Groq Console](https://console.groq.com/)
- Sign up for a free account
- Generate an API key

### 3. Configure Environment
Create a `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the AI Assistant
```bash
# Standalone version (AI only)
python agribricks_standalone.py

# Or integrate with existing FastAPI app
uvicorn app.main:app --reload
```

### 5. Test the API
Visit: http://localhost:8000/docs

## 📖 API Usage

### Ask Agricultural Questions
```bash
curl -X POST "http://localhost:8000/api/agribricks-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I control aphids on tomatoes naturally?",
    "location": "Central Kenya", 
    "crop_type": "tomatoes"
  }'
```

### Example Response
```json
{
  "question": "How do I control aphids on tomatoes naturally?",
  "answer": "🎯 **Direct Answer**\nAphids can be controlled naturally using neem oil, beneficial insects, and companion planting...\n\n📋 **Action Steps**\n1. Spray neem oil solution (2-3ml per liter)\n2. Introduce ladybugs and lacewings\n3. Plant marigolds nearby...",
  "confidence_score": 0.92,
  "sources": ["Agricultural best practices", "IPM protocols"],
  "recommendations": [
    "Apply neem oil in early morning",
    "Monitor plants weekly",
    "Maintain proper spacing"
  ],
  "location_context": "Central Kenya",
  "crop_context": "tomatoes"
}
```

## 🌾 What the AI Can Help With

### Crop Management
- Best planting times and seasons
- Crop selection for your climate
- Harvesting timing and techniques
- Yield optimization strategies

### Pest & Disease Control
- Natural pest control methods
- Disease identification and treatment
- Integrated pest management
- Organic solutions

### Soil Health
- Soil fertility improvement
- Organic fertilizer recommendations
- pH management
- Composting techniques

### Weather & Climate
- Drought-resistant crops
- Climate adaptation strategies
- Seasonal farming calendar
- Water conservation

### Sustainable Practices
- Organic farming methods
- Crop rotation strategies
- Resource conservation
- Environmental protection

## 🔧 Configuration Options

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_key_here

# Optional
DEBUG=True
LOG_LEVEL=INFO
```

### Supported Languages
- English (en) - Default
- Swahili (sw)
- French (fr)
- Spanish (es)

## 📊 Health Monitoring

Check AI service status:
```bash
GET /api/agribricks-ai/health
```

## 🧪 Testing

Run the test script:
```bash
python test_agribricks_ai.py
```

## 📚 Example Questions

### Crop Management
- "What are the best crops for the rainy season in Kenya?"
- "When should I plant maize in my region?"
- "How do I increase my tomato yield?"

### Pest Control
- "How do I control fall armyworm naturally?"
- "What are signs of bacterial wilt in tomatoes?"
- "Best organic pesticides for vegetables?"

### Soil Health
- "How to improve clay soil for farming?"
- "What organic fertilizer is best for maize?"
- "How to make compost at home?"

## 🚀 Deployment

### Local Development
```bash
python agribricks_standalone.py
```

### Production (Docker)
```dockerfile
FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements_ai_only.txt
CMD ["python", "agribricks_standalone.py"]
```

### Cloud Deployment
Deploy to platforms like:
- Render
- Railway
- Heroku
- AWS Lambda

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📄 License

MIT License

## 🆘 Support

- **Issues**: Create GitHub issues
- **Questions**: Use the `/api/examples` endpoint
- **Documentation**: Visit `/docs` when running

## 🙏 Acknowledgments

- **Groq**: For providing fast LLM inference
- **LangChain**: For AI framework and tools
- **Agricultural Experts**: For domain knowledge validation

---

**Made with 🌱 for farmers worldwide**