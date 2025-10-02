#!/bin/bash

# Check if OpenAI API key is set
if [ -z "$API_KEY_OPEN_AI" ] && [ ! -f .env ]; then
    echo "⚠️  Warning: API_KEY_OPEN_AI not found"
    echo "Please create a .env file with: echo 'API_KEY_OPEN_AI=your-key-here' > .env"
    echo "Or set it with: export API_KEY_OPEN_AI='your-key-here'"
    echo ""
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🚀 Starting FastAPI server..."
echo "📍 Interface: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
python3 main.py 