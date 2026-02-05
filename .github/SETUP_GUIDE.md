# Quick Setup Guide for Version Control

## 🚀 Getting Started

Your repository now has automatic version control! Here's how to set it up:

### Step 1: Commit the New Files

```bash
# Add all the new version control files
git add .github/
git add VERSION.md
git add README.md

# Commit them
git commit -m "Add automatic version control system"

# Push to GitHub
git push origin main
```

### Step 2: First Version Tag

After pushing, the GitHub Actions workflow will automatically:
- Create version `v0.1.0` (or increment from existing tags)
- Create a backup branch
- Generate a changelog
- Create a GitHub Release

### Step 3: Verify It's Working

1. Go to your GitHub repository
2. Click on **Actions** tab
3. You should see "Version Control & Code Preservation" workflow running
4. Once complete, check:
   - **Releases** tab - You'll see your first release
   - **Tags** - You'll see version tags
   - **Branches** - You'll see backup branches

## 📋 What Happens Automatically

Every time you push to `main`:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

The system automatically:
1. ✅ Detects the push
2. ✅ Increments version (v0.1.0 → v0.1.1)
3. ✅ Creates backup branch: `backup/v0.1.0-20260205-233000`
4. ✅ Creates version tag: `v0.1.1`
5. ✅ Generates changelog
6. ✅ Creates GitHub Release with downloadable archive
7. ✅ Updates `VERSION.md`

## 🎯 Common Tasks

### Create a Manual Snapshot Before Risky Changes

1. Go to GitHub → **Actions** tab
2. Select **Manual Code Snapshot**
3. Click **Run workflow**
4. Fill in:
   - **Snapshot name**: `before-database-migration`
   - **Description**: `Snapshot before migrating to PostgreSQL`
5. Click **Run workflow**

### Recover Old Code

```bash
# See all versions
git fetch --tags
git tag -l

# Checkout a specific version
git checkout v0.1.0

# Return to latest
git checkout main

# Create a recovery branch from old version
git checkout -b recovery-from-v0.1.0 v0.1.0
git push origin recovery-from-v0.1.0
```

### Manually Bump Version Type

By default, each push increments the patch version (v1.0.0 → v1.0.1).

To do a **minor** or **major** version bump:

1. Go to GitHub → **Actions** tab
2. Select **Version Control & Code Preservation**
3. Click **Run workflow**
4. Select version type:
   - **patch**: v1.0.0 → v1.0.1 (bug fixes)
   - **minor**: v1.0.0 → v1.1.0 (new features)
   - **major**: v1.0.0 → v2.0.0 (breaking changes)
5. Click **Run workflow**

## 📖 Documentation

- **Full Guide**: See [VERSION_CONTROL_GUIDE.md](.github/VERSION_CONTROL_GUIDE.md)
- **Version History**: See [VERSION.md](VERSION.md)
- **Changelogs**: Check `.github/changelogs/` directory

## ✅ Checklist

- [ ] Commit and push the new files
- [ ] Verify workflow runs successfully
- [ ] Check that first release is created
- [ ] Try creating a manual snapshot
- [ ] Practice recovering old code

## 🆘 Troubleshooting

### Workflow Not Running?

Make sure:
1. You pushed to `main` or `master` branch
2. GitHub Actions is enabled in your repository settings
3. The workflow files are in `.github/workflows/` directory

### Can't See Releases?

1. Go to repository **Settings**
2. Scroll to **Features**
3. Make sure **Releases** is enabled

### Need Help?

See the full guide: [VERSION_CONTROL_GUIDE.md](.github/VERSION_CONTROL_GUIDE.md)

## 🎉 You're All Set!

Your code is now automatically preserved. You'll never lose old code again!

**Next Steps:**
1. Commit and push these files
2. Watch the workflow run
3. Check your first release
4. Continue coding with confidence! 🚀
