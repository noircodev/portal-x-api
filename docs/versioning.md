Here is a comprehensive **documentation on your version bump workflow**, explaining how to use semantic versioning with GitHub Actions and how your system handles automated versioning, staging integration, and deployments based on version tags like `bump/major`, `bump/minor`, and `bump/patch`.

---

# 📘 Documentation: Semantic Versioning & Version Bump Workflow

## Overview

This document outlines the **automated version bump process** for the Portal X Event Project using GitHub Actions and semantic versioning principles. Version bumps are **triggered via Git tags** with the format:

- `bump/major`
- `bump/minor`
- `bump/patch`

Once triggered, a GitHub Actions workflow automatically:

1. Merges changes into the `staging` branch.
2. Updates the version number in `pyproject.toml`.
3. Tags the new version as `vX.Y.Z`.
4. Pushes the tag and code to the `staging` branch.
5. Triggers the **auto-deployment workflow** for staging.

---

## 📌 Triggering a Version Bump

To initiate a version bump, push a tag to the repository in the following format:

```bash
git tag bump/patch
git push origin bump/patch
```

| Tag Format   | Version Change Type | Description                              |
| ------------ | ------------------- | ---------------------------------------- |
| `bump/patch` | Patch               | Backward-compatible bug fix              |
| `bump/minor` | Minor               | Backward-compatible feature addition     |
| `bump/major` | Major               | Breaking changes or incompatible updates |

---

## 🛠 How It Works

### 1. `Version Bump` GitHub Workflow

**Trigger**: Tag push to `bump/*`

#### Key Steps:

| Step                        | Description                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| **Extract bump type**       | Determines the bump type (`major`, `minor`, `patch`) from the tag                        |
| **Setup `staging` branch**  | Ensures the `staging` branch exists and is checked out                                   |
| **Merge changes**           | Merges the latest commit into `staging`, using `theirs` strategy for conflict resolution |
| **Run version bump script** | Calls `scripts/bump_version.py <type>` to update `pyproject.toml` version                |
| **Commit and tag**          | Commits updated version and tags it as `vX.Y.Z`                                          |
| **Push to GitHub**          | Pushes both `staging` and the version tag                                                |
| **Clean up**                | Deletes the trigger tag `bump/*` from the remote                                         |
| **Summarize**               | Outputs version bump summary to GitHub Actions UI                                        |

---

### 2. `Auto Deploy` GitHub Workflow

**Trigger**:

- Push to `staging` (after version bump)
- Merge PR from `staging` → `main` (for production deployment)

#### Staging Deploy Flow:

Triggered immediately after a successful version bump:

- Fetches code on the server
- Activates Python virtual environment
- Installs dependencies (base + optional based on environment)
- Applies database migrations
- Runs custom post-deploy scripts
- Collects static files
- Restarts services (e.g., Gunicorn)
- Records deployment metadata (via `create_app_version`)

---

## 🔍 Versioning Script: `scripts/bump_version.py`

This script performs the actual semantic version bump.

```bash
python scripts/bump_version.py patch
```

### Internals:

- Reads current version from `pyproject.toml`
- Increments the version segment (`X`, `Y`, or `Z`) based on bump type
- Writes the updated version back to `pyproject.toml`

---

## 📝 Commit Conventions (Optional but Recommended)

Adopt the **Conventional Commits** format to align changelogs with version types:

```bash
git commit -m "feat: add export functionality"
git commit -m "fix: correct typo in login API"
git commit -m "refactor!: change auth system (BREAKING CHANGE)"
```

This helps future automation (e.g., changelog generation, semantic-release).

---

## 🚀 Sample Workflow for Team

1. Merge your feature/fix into the default branch (e.g., `main`).

2. Decide on the appropriate version bump:

   - Bug fix? → `patch`
   - New feature? → `minor`
   - Breaking change? → `major`

3. Run:

   ```bash
   git tag bump/minor
   git push origin bump/minor
   ```

4. GitHub Actions:

   - Executes version bump logic
   - Merges and updates `staging`
   - Triggers deployment to staging
   - Outputs summary

---

## 🔐 Permissions

Ensure these secrets are configured in your repository settings:

| Secret Name         | Description                              |
| ------------------- | ---------------------------------------- |
| `GH_PAT`            | Personal access token with `repo` access |
| `STAGING_SERVER`    | SSH string for staging server            |
| `PRODUCTION_SERVER` | SSH string for production server         |
| `SSH_PRIVATE_KEY`   | SSH key with access to deployment server |

---

## ✅ Advantages of This Setup

- **Automated semantic versioning** tied to Git tags
- **Conflict-resilient staging integration**
- **Environment-specific deployments** with rollback protection
- **Clean, informative GitHub summaries**
- **Version tracking & tagging enforcement**

---

## 📎 Sample Summary Output

```
# 🚀 Version Bump Complete

- **New Version**: v1.4.0
- **Bump Type**: minor
- **Target Branch**: staging
- **Tag Created**: v1.4.0

## Summary
The version has been successfully bumped and deployed to staging branch.
All conflicts were resolved by preserving workflow files and accepting other changes.

## Usage
Version was automatically bumped from trigger tag: `bump/minor`
```

---

## 📚 Future Recommendations

- Add **changelog generator** (e.g., `auto-changelog`, `release-please`)
- Enforce commit message format using `commitlint` + `husky`
- Add **GitHub Release Notes** on version tag push

---
