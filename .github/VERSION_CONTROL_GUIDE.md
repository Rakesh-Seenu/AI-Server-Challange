# Version Control & Code Preservation Guide

This document explains how your code is automatically preserved and how to recover old versions.

## 🎯 Overview

Your repository now has **automatic version control** that ensures you never lose old code. Every time you push to the main branch, the system:

1. ✅ Creates a **backup branch** with a timestamp
2. ✅ Generates a **version tag** (e.g., v1.0.0, v1.0.1)
3. ✅ Creates a **GitHub Release** with downloadable archives
4. ✅ Generates a **changelog** documenting what changed
5. ✅ Preserves **full git history**

## 🚀 How It Works

### Automatic Versioning (On Every Push)

When you push code to the `main` or `master` branch:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

The GitHub Actions workflow automatically:
- Increments the version number (patch version by default: v1.0.0 → v1.0.1)
- Creates a backup branch named `backup/v1.0.0-20260205-233000`
- Creates a version tag `v1.0.1`
- Generates a changelog showing all changes
- Creates a GitHub Release with a downloadable zip archive
- Updates the VERSION.md file

### Manual Version Bumps

You can manually trigger a version bump with a specific type:

1. Go to **Actions** tab in GitHub
2. Select **Version Control & Code Preservation** workflow
3. Click **Run workflow**
4. Choose version bump type:
   - **major**: v1.0.0 → v2.0.0 (breaking changes)
   - **minor**: v1.0.0 → v1.1.0 (new features)
   - **patch**: v1.0.0 → v1.0.1 (bug fixes)

### Manual Code Snapshots

Create a snapshot before making risky changes:

1. Go to **Actions** tab in GitHub
2. Select **Manual Code Snapshot** workflow
3. Click **Run workflow**
4. Enter:
   - **Snapshot name**: e.g., "before-major-refactor"
   - **Description**: Why you're creating this snapshot

This creates:
- A snapshot branch: `snapshot/before-major-refactor-20260205-233000`
- A snapshot tag: `snapshot-before-major-refactor-20260205-233000`
- A GitHub Release with downloadable archive

## 📥 How to Recover Old Code

### Method 1: Using Git Tags (Recommended)

View all available versions:
```bash
git fetch --tags
git tag -l
```

Checkout a specific version:
```bash
# View the code at version v1.0.0
git checkout v1.0.0

# Return to latest code
git checkout main
```

Create a new branch from an old version:
```bash
# Create a new branch from v1.0.0
git checkout -b recovery-branch v1.0.0
git push origin recovery-branch
```

### Method 2: Using Backup Branches

List all backup branches:
```bash
git fetch origin
git branch -r | grep backup
```

Checkout a backup branch:
```bash
git checkout backup/v1.0.0-20260205-233000
```

### Method 3: Using GitHub Releases

1. Go to your repository on GitHub
2. Click on **Releases** (right sidebar)
3. Find the version you want
4. Download the `.zip` archive
5. Extract and use the code

### Method 4: Using Git History

View commit history:
```bash
git log --oneline
```

Checkout a specific commit:
```bash
git checkout <commit-hash>
```

View changes in a specific commit:
```bash
git show <commit-hash>
```

### Method 5: Using Snapshots

List all snapshots:
```bash
git fetch origin
git tag -l | grep snapshot
```

Checkout a snapshot:
```bash
git checkout snapshot-before-major-refactor-20260205-233000
```

## 🔍 Finding What You Need

### View All Versions
```bash
# See all version tags
git tag -l "v*" --sort=-version:refname

# See all backup branches
git branch -r | grep backup

# See all snapshots
git tag -l "snapshot-*"
```

### Compare Versions
```bash
# See what changed between two versions
git diff v1.0.0 v1.1.0

# See files that changed
git diff --name-status v1.0.0 v1.1.0

# See changes in a specific file
git diff v1.0.0 v1.1.0 -- main.py
```

### View Changelogs

Changelogs are automatically generated in `.github/changelogs/`:
- `CHANGELOG-v1.0.0.md`
- `CHANGELOG-v1.1.0.md`
- etc.

## 📊 Version Tracking

Check `VERSION.md` in the root directory to see:
- Current version
- All previous versions with release dates
- Quick reference for version history

## 🛡️ Safety Features

Your code is protected in **5 different ways**:

1. **Git Tags**: Permanent markers for each version
2. **Backup Branches**: Timestamped branches before each version
3. **GitHub Releases**: Downloadable archives of each version
4. **Snapshot Branches**: Manual snapshots before risky changes
5. **Git History**: Complete commit history

## 💡 Best Practices

### Before Major Changes
Create a manual snapshot:
```bash
# Go to GitHub Actions → Manual Code Snapshot
# Name it descriptively: "before-database-migration"
```

### Regular Commits
Commit frequently with clear messages:
```bash
git commit -m "Add email validation to prefill endpoint"
```

### Use Semantic Versioning
- **Major** (v2.0.0): Breaking changes, major rewrites
- **Minor** (v1.1.0): New features, backwards compatible
- **Patch** (v1.0.1): Bug fixes, small improvements

## 🆘 Emergency Recovery

If something goes wrong:

1. **Don't panic!** Your code is safe.

2. **Find the last working version:**
   ```bash
   git tag -l --sort=-version:refname
   ```

3. **Restore it:**
   ```bash
   # Option A: Create a recovery branch
   git checkout -b emergency-recovery v1.0.0
   git push origin emergency-recovery
   
   # Option B: Reset main to old version (careful!)
   git checkout main
   git reset --hard v1.0.0
   git push origin main --force
   ```

4. **Or download from GitHub Releases** and start fresh.

## 📝 Examples

### Example 1: Recover Yesterday's Code
```bash
# Find yesterday's version
git log --since="yesterday" --oneline

# Checkout that commit
git checkout <commit-hash>

# Or use the backup branch
git checkout backup/v1.0.0-20260204-150000
```

### Example 2: Compare Current Code with Last Week
```bash
# Find last week's tag
git tag -l --sort=-version:refname

# Compare
git diff v0.9.0 HEAD
```

### Example 3: Restore a Deleted File
```bash
# Find when it was deleted
git log --all --full-history -- path/to/file.py

# Restore it from a specific version
git checkout v1.0.0 -- path/to/file.py
git commit -m "Restore deleted file from v1.0.0"
```

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| View all versions | `git tag -l` |
| Checkout version | `git checkout v1.0.0` |
| View changes | `git diff v1.0.0 v1.1.0` |
| List backups | `git branch -r \| grep backup` |
| Create snapshot | Use GitHub Actions → Manual Snapshot |
| View history | `git log --oneline` |
| Return to latest | `git checkout main` |

## ⚙️ Configuration

The workflows are located in:
- `.github/workflows/version-control.yml` - Automatic versioning
- `.github/workflows/manual-snapshot.yml` - Manual snapshots

You can customize:
- Version bump strategy
- Backup branch naming
- Changelog format
- Archive contents

## 📞 Need Help?

If you need to recover code and aren't sure how:

1. Check `VERSION.md` for available versions
2. Look at `.github/changelogs/` for what changed
3. Use `git log` to see commit history
4. Download from GitHub Releases if needed

**Remember**: With this setup, you can ALWAYS recover your old code! 🎉
