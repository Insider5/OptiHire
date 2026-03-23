#!/bin/bash

# OptiHire Installation Script (File-based Storage Version)
# Uses all-MiniLM model and JSON file storage

echo "🚀 OptiHire Installation Script (File-based Version)"
echo "===================================================="
echo "Features: all-MiniLM semantic matching + File storage"
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Activate existing virtual environment or create new one
echo ""
if [ -d "venv" ]; then
    echo "📦 Activating existing virtual environment..."
    source venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created"
fi

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies (no database required)..."
pip install -r requirements.txt

# Download spaCy model
echo ""
echo "🤖 Downloading spaCy language model for NER..."
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your Gemini API key (optional)."
else
    echo ""
    echo "ℹ️  .env file already exists"
fi

# Create required directories
echo ""
echo "📁 Creating application directories..."
mkdir -p uploads data
touch uploads/.gitkeep
touch data/.gitkeep

# Initialize storage
echo ""
echo "🗄️  Initializing file storage..."
flask --app run init-storage

# Ask if user wants to create sample data
echo ""
read -p "Would you like to create sample data for testing? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    flask --app run create-sample-data
    echo ""
    echo "✅ Sample data created!"
    echo "   Recruiter: recruiter@example.com / password123"
    echo "   Candidate: candidate@example.com / password123"
fi

echo ""
echo "✨ Installation complete!"
echo ""
echo "📋 System Configuration:"
echo "   ✅ all-MiniLM-L6-v2 for semantic matching"
echo "   ✅ File-based storage (no database)"
echo "   ✅ spaCy NER for resume parsing"
echo "   ✅ Gemini AI for interview questions (optional)"
echo ""
echo "📋 Next steps:"
echo "   1. (Optional) Edit .env file with Gemini API key"
echo "   2. Activate virtual environment: source venv/bin/activate"
echo "   3. Run the application: python run.py"
echo "   4. Open browser to: http://localhost:5000"
echo ""
echo "Happy hiring! 🎉"
