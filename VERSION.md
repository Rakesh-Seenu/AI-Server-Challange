# Version History

## Current Version: v0.1.0

This file tracks all versions of the AI Server project. Each version is preserved in multiple ways:
- Git tags
- Backup branches
- GitHub Releases with downloadable archives
- Full git history

## How to Use This File

This file is automatically updated by the GitHub Actions workflow. You can:
- See what version you're currently on
- View the history of all releases
- Find when specific versions were released

## Version List

### v0.1.0 - Initial Release
- **Date**: TBD (will be set on first workflow run)
- **Description**: Initial version with version control system
- **Features**:
  - FastAPI server with chat completions endpoint
  - Email data extraction (prefill endpoint)
  - Rate limiting
  - OpenAI and OpenRouter integration
  - Automatic version control and code preservation

---

## Future Versions

All future versions will be automatically listed here when the GitHub Actions workflow runs.

To see detailed changes for each version, check the `.github/changelogs/` directory.

## Quick Commands

```bash
# View all versions
git tag -l

# Checkout a specific version
git checkout v0.1.0

# Return to latest
git checkout main

# See what changed between versions
git diff v0.1.0 v0.2.0
```

For more information, see [VERSION_CONTROL_GUIDE.md](.github/VERSION_CONTROL_GUIDE.md)
