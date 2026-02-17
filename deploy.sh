#!/bin/bash
# Quick deployment script for Streamlit Cloud

echo "🚀 Preparing deployment to Streamlit Cloud..."
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/Tejsai05/AI-Personal-Finance-Manager.git
fi

echo "📝 Adding files to git..."
git add .

echo "💬 Committing changes..."
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Update AI Personal Finance Manager for deployment"
fi
git commit -m "$commit_msg"

echo "⬆️  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Done! Your code is now on GitHub."
echo ""
echo "📍 Next steps:"
echo "1. Go to https://share.streamlit.io/"
echo "2. Sign in with GitHub"
echo "3. Click 'New app'"
echo "4. Select repository: Tejsai05/AI-Personal-Finance-Manager"
echo "5. Branch: main"
echo "6. Main file: app.py"
echo "7. Click 'Deploy!'"
echo ""
echo "🌐 Your app will be live at: https://[your-app-name].streamlit.app"
echo ""
