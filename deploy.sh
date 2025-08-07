#!/bin/bash

set -e

# Prompt for deployment type
read -rp "Enter deployment type (major, minor, patch): " DEPLOY_TYPE
if [[ ! "$DEPLOY_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "❌ Invalid deployment type. Must be 'major', 'minor', or 'patch'."
    exit 1
fi

# Prompt for commit message
read -rp "Enter commit message: " COMMIT_MSG
if [[ -z "$COMMIT_MSG" ]]; then
    echo "❌ Commit message cannot be empty."
    exit 1
fi

# Commit any staged changes
echo "📦 Committing changes..."
git add .
git commit -m "$COMMIT_MSG" || echo "⚠️ No changes to commit"

# Define tag
TAG="bump/$DEPLOY_TYPE"

# Delete local tag if it exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "🧹 Deleting existing local tag: $TAG"
    git tag -d "$TAG"
fi

# Create new tag
echo "🏷️ Creating new tag: $TAG"
git tag "$TAG"

# Push tag to remote
echo "🚀 Pushing tag to remote: $TAG"
if git push origin "$TAG"; then
    echo "✅ Tag '$TAG' pushed successfully!"
else
    echo "❌ Failed to push tag '$TAG'"
    exit 1
fi
