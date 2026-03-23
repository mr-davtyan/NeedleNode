#!/bin/bash
set -e

# Ensure we are in the project root
cd "$(dirname "$0")"

# 1. Read current version
if [ ! -f "VERSION" ]; then
    echo "Error: VERSION file not found."
    exit 1
fi

CURRENT_VERSION=$(cat VERSION)
echo "Current Version: $CURRENT_VERSION"

# 2. Increment patch version
# Split by dot
IFS='.' read -r -a parts <<< "$CURRENT_VERSION"

MAJOR="${parts[0]}"
MINOR="${parts[1]}"
PATCH="${parts[2]}"

# Check if we have valid parts
if [ -z "$MAJOR" ] || [ -z "$MINOR" ] || [ -z "$PATCH" ]; then
    echo "Error: Invalid version format in VERSION file. Expected X.Y.Z"
    exit 1
fi

NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"

echo "New Version: $NEW_VERSION"

# 3. Write new version
echo "$NEW_VERSION" > VERSION

# 4. Git operations
echo "Committing version bump..."
git add VERSION
git commit -m "Release $NEW_VERSION"

echo "Pushing changes..."
git push origin main  # Assumes 'main' is the branch

echo "Release $NEW_VERSION completed and pushed."
