# Setup Guide

This guide will walk you through setting up the GitHub workflows in your repository.

## 🚀 Quick Setup (5 minutes)

### 1. Copy Workflows

```bash
# Clone this repository or download the .github directory
git clone https://github.com/your-username/github-workflows-you-need.git
cp -r github-workflows-you-need/.github your-repo/.github
```

### 2. Set Up Secrets

Go to your repository → Settings → Secrets and variables → Actions, and add:

#### Required for all workflows:
- `GITHUB_TOKEN` (automatically provided)

#### Required for AWS workflows:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional, defaults to us-east-1)

### 3. Customize Configuration

Create custom configuration files in your repository root:

```bash
# PR Reviewers
cp .github/workflows/config/default_reviewers.yml .github/auto_reviewers.yml

# Sensitive Files
cp .github/workflows/config/default_sensitive_files.yml .github/sensitive_files.yml

# Versioning
cp .github/workflows/config/default_versioning.yml .github/versioning.yml
```

### 4. Test the Workflows

Create a test PR to verify everything works:
```bash
git checkout -b test-workflows
echo "test" > test.txt
git add test.txt
git commit -m "test: add test file"
git push origin test-workflows
```

## 🔧 Detailed Setup

### Step 1: Repository Preparation

1. **Ensure your repository has the correct structure**:
   ```
   your-repo/
   ├── .github/
   │   └── workflows/
   ├── package.json (if using Node.js)
   └── README.md
   ```

2. **Check branch protection rules** (recommended):
   - Go to Settings → Branches
   - Add rule for `main` or `master`
   - Enable "Require status checks to pass before merging"
   - Enable "Require branches to be up to date before merging"

### Step 2: Workflow Installation

1. **Copy the workflows**:
   ```bash
   # Option 1: Manual copy
   mkdir -p .github/workflows
   cp github-workflows-you-need/.github/workflows/*.yml .github/workflows/
   cp -r github-workflows-you-need/.github/workflows/reusable .github/workflows/
   cp -r github-workflows-you-need/.github/workflows/config .github/workflows/
   cp -r github-workflows-you-need/.github/scripts .github/

   # Option 2: Git submodule (for updates)
   git submodule add https://github.com/your-username/github-workflows-you-need.git
   cp -r github-workflows-you-need/.github .github
   ```

2. **Verify the structure**:
   ```bash
   tree .github/
   ```

### Step 3: Configuration

#### A. PR Reviewers Configuration

Create `.github/auto_reviewers.yml`:

```yaml
# Default reviewers for all PRs
default_reviewers:
  - "your-username"
  - "team-lead"

# Path-based reviewers
path_reviewers:
  "frontend/.*":
    - "frontend-lead"
    - "ui-ux-expert"
  "backend/.*|api/.*":
    - "backend-lead"
    - "senior-backend"
  "infrastructure/.*|terraform/.*":
    - "devops-lead"
    - "infrastructure-admin"
```

#### B. Sensitive Files Configuration

Create `.github/sensitive_files.yml`:

```yaml
# Files to detect as sensitive
sensitive_patterns:
  - "\\.env$"
  - ".*\\.key$"
  - ".*\\.pem$"
  - "secrets\\.json"
  - "config\\.json"

# Files to exclude from detection
excluded_patterns:
  - "\\.env\\.example$"
  - "docs/.*"
  - "test/.*"
  - "examples/.*"
```

#### C. Versioning Configuration

Create `.github/versioning.yml`:

```yaml
# Version bump rules
version_bump_rules:
  major:
    - "BREAKING CHANGE"
    - "!:"  # Breaking change indicator
  minor:
    - "feat:"
    - "feature:"
  patch:
    - "fix:"
    - "docs:"
    - "style:"
    - "refactor:"

# Release configuration
release:
  create_github_release: true
  generate_changelog: true
  draft_release: false
  prerelease: false
```

### Step 4: Secrets Configuration

#### For Basic Usage (PR Reviewers, Sensitive Files, Tests, Versioning):

No additional secrets required beyond `GITHUB_TOKEN`.

#### For AWS Workflows:

1. **Create AWS IAM User**:
   ```bash
   # For S3 Migration
   aws iam create-user --user-name github-actions-s3
   aws iam attach-user-policy --user-name github-actions-s3 --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
   
   # For IAM User Creation
   aws iam create-user --user-name github-actions-iam
   aws iam attach-user-policy --user-name github-actions-iam --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
   ```

2. **Generate Access Keys**:
   ```bash
   aws iam create-access-key --user-name github-actions-s3
   aws iam create-access-key --user-name github-actions-iam
   ```

3. **Add to GitHub Secrets**:
   ```
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   AWS_REGION=us-east-1
   ```

#### For Cross-Account S3 Migration:

Add additional secrets:
```
AWS_ACCESS_KEY_ID_SOURCE=source_account_key
AWS_SECRET_ACCESS_KEY_SOURCE=source_account_secret
AWS_ROLE_ARN_SOURCE=arn:aws:iam::source:role/role-name
AWS_ACCESS_KEY_ID_TARGET=target_account_key
AWS_SECRET_ACCESS_KEY_TARGET=target_account_secret
AWS_ROLE_ARN_TARGET=arn:aws:iam::target:role/role-name
```

#### For NPM Publishing:

```
NPM_TOKEN=your_npm_token
```

### Step 5: Testing

#### Test PR Reviewers:

1. Create a PR with changes to `frontend/` files
2. Verify that frontend reviewers are automatically assigned

#### Test Sensitive Files Detection:

1. Try to commit a file named `.env`
2. Verify the workflow fails and comments on the PR

#### Test Test Runner:

1. Ensure your project has a `package.json` with test script
2. Create a PR and verify tests run

#### Test Versioning:

1. Merge a PR with conventional commit message (e.g., `feat: add new feature`)
2. Verify version is bumped and release is created

#### Test Manual Workflows:

1. Go to Actions tab
2. Select "S3 Bucket Migration" or "IAM User Creation"
3. Fill in required parameters
4. Run the workflow

## 🔍 Troubleshooting

### Common Issues

#### 1. Workflows not triggering

**Problem**: Workflows don't run on PRs
**Solution**: Check branch protection rules and ensure workflows are enabled

#### 2. Permission denied errors

**Problem**: AWS workflows fail with permission errors
**Solution**: Verify IAM policies and access keys

#### 3. Configuration not loading

**Problem**: Workflows use default config instead of custom
**Solution**: Ensure custom config files are in the correct location

#### 4. Test failures

**Problem**: Test workflow fails
**Solution**: Check package.json test script and dependencies

### Debug Steps

1. **Check workflow logs**:
   - Go to Actions tab
   - Click on failed workflow
   - Review step-by-step logs

2. **Verify secrets**:
   - Go to Settings → Secrets
   - Ensure all required secrets are set

3. **Check file permissions**:
   ```bash
   chmod +x .github/scripts/*.py
   ```

4. **Test locally** (for scripts):
   ```bash
   cd .github/scripts
   python3 s3_migration.py --help
   python3 iam_user_creation.py --help
   ```

## 🔄 Updates and Maintenance

### Updating Workflows

1. **Pull latest changes**:
   ```bash
   git submodule update --remote
   ```

2. **Review changes**:
   ```bash
   git diff HEAD~1
   ```

3. **Test in development**:
   - Create test branch
   - Verify workflows work correctly
   - Merge to main

### Customization

1. **Modify workflows**:
   - Edit `.github/workflows/*.yml` files
   - Test changes thoroughly
   - Document modifications

2. **Add new workflows**:
   - Follow existing patterns
   - Include proper documentation
   - Add to this setup guide

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review workflow logs for specific error messages
3. Open an issue in this repository
4. Check the main README for additional documentation 