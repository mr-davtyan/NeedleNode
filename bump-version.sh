#!/bin/bash
# bump-version.sh

# Exit on absolute error
set -e

# Default to "patch" if no argument is provided
BUMP_TYPE=${1:-patch}

# Ensure VERSION file exists
if [ ! -f VERSION ]; then
    echo "1.0.0" > VERSION
fi

CURRENT_VERSION=$(cat VERSION | xargs)
echo "Current Version: $CURRENT_VERSION"

# Split by '.'
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
if [ ${#VERSION_PARTS[@]} -ne 3 ]; then
    echo "Error: Invalid version format in VERSION file ('$CURRENT_VERSION'). Expected x.y.z"
    exit 1
fi

MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

case "$BUMP_TYPE" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "Usage: ./bump-version.sh [major|minor|patch]"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "$NEW_VERSION" > VERSION
echo "New Version: $NEW_VERSION"

# Detect current branch dynamically
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Stage and Commit
git add VERSION
git commit -m "Bump version to $NEW_VERSION"

# Add tag
git tag -a "v$NEW_VERSION" -m "Version $NEW_VERSION"

echo "Pushing changes to origin/$CURRENT_BRANCH and tags..."
git push origin "$CURRENT_BRANCH" --tags

echo "Successfully bumped version to $NEW_VERSION and triggered build flawlessly."
