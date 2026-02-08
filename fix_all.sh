#!/bin/bash
echo "Fixing all issues..."

# Kill processes on ports 3000 and 8000
kill -9 $(lsof -t -i:3000) 2>/dev/null || true
kill -9 $(lsof -t -i:8000) 2>/dev/null || true

# Clear node modules
cd frontend
rm -rf node_modules .next
npm install

# Clear Python cache
cd ../backend
rm -rf __pycache__ services/__pycache__ utils/__pycache__
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

echo "✅ Fixed! Now run:"
echo "Terminal 1: cd backend && python main.py"
echo "Terminal 2: cd frontend && npm run dev"
