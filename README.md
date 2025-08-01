# GitHub Workflows You Need

A comprehensive collection of modular, reusable GitHub Actions workflows that can be integrated into any project with minimal configuration changes.

## 🚀 Features

- **🔍 Auto PR Reviewers**: Automatically assign reviewers based on file paths and configuration
- **🚨 Sensitive Files Detection**: Prevent commits with sensitive files like `.env`, `*.pem`, etc.
- **🧪 Test Runner**: Modular test execution with support for multiple package managers
- **🏷️ Versioning & Releases**: Automatic semantic versioning and GitHub releases
- **☁️ S3 Migration**: Cross-account S3 bucket migration with metadata preservation
- **👤 IAM User Creation**: Create IAM users with minimal permissions and security policies

## 📁 Project Structure

```
.github/
├── workflows/
│   ├── pr-reviewers.yml              # Auto-assign PR reviewers
│   ├── sensitive-files-check.yml     # Detect sensitive files
│   ├── test.yml                      # Main test workflow
│   ├── version-and-release.yml       # Versioning and releases
│   ├── s3-migration.yml              # S3 bucket migration
│   ├── iam-user-creation.yml         # IAM user creation
│   ├── reusable/
│   │   └── test-runner.yml           # Reusable test workflow
│   └── config/
│       ├── default_reviewers.yml     # Default reviewer config
│       ├── default_sensitive_files.yml # Sensitive files config
│       └── default_versioning.yml    # Versioning config
├── scripts/
│   ├── s3_migration.py               # S3 migration script
│   └── iam_user_creation.py          # IAM user creation script
```

## 🛠️ Quick Start

1. **Copy the workflows** to your repository's `.github/workflows/` directory
2. **Configure the workflows** by creating custom config files or modifying the defaults
3. **Set up required secrets** in your repository settings
4. **Customize as needed** for your specific project requirements

## 📋 Prerequisites

### Required Secrets

#### For All Workflows
- `GITHUB_TOKEN` (automatically provided)

#### For AWS Workflows (S3 Migration & IAM Creation)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional, defaults to us-east-1)

#### For Cross-Account S3 Migration
- `AWS_ACCESS_KEY_ID_SOURCE`
- `AWS_SECRET_ACCESS_KEY_SOURCE`
- `AWS_ROLE_ARN_SOURCE`
- `AWS_ACCESS_KEY_ID_TARGET`
- `AWS_SECRET_ACCESS_KEY_TARGET`
- `AWS_ROLE_ARN_TARGET`

#### For NPM Publishing (if applicable)
- `NPM_TOKEN`

## 🔧 Configuration

### 1. PR Reviewers Configuration

Create `.github/auto_reviewers.yml` in your repository:

```yaml
# Default reviewers for all PRs
default_reviewers:
  - "your-username"
  - "team-lead"

# Path-based reviewers
path_reviewers:
  "frontend/.*":
    - "frontend-lead"
  "backend/.*":
    - "backend-lead"
  "infrastructure/.*":
    - "devops-lead"
```

### 2. Sensitive Files Configuration

Create `.github/sensitive_files.yml`:

```yaml
# Files to detect as sensitive
sensitive_patterns:
  - "\\.env$"
  - ".*\\.key$"
  - ".*\\.pem$"

# Files to exclude from detection
excluded_patterns:
  - "\\.env\\.example$"
  - "docs/.*"
```

### 3. Versioning Configuration

Create `.github/versioning.yml`:

```yaml
# Version bump rules
version_bump_rules:
  major:
    - "BREAKING CHANGE"
  minor:
    - "feat:"
  patch:
    - "fix:"
    - "docs:"
```

## 📖 Workflow Documentation

### 🔍 Auto PR Reviewers

**File**: `.github/workflows/pr-reviewers.yml`

Automatically assigns reviewers to pull requests based on:
- Default reviewers for all PRs
- Path-based reviewers for specific file changes
- Configuration from `.github/auto_reviewers.yml`

**Triggers**: PR opened, synchronized, or marked ready for review

**Customization**:
- Modify `.github/auto_reviewers.yml` to change reviewer assignments
- Add path patterns using regex
- Configure different reviewers for different file types

### 🚨 Sensitive Files Detection

**File**: `.github/workflows/sensitive-files-check.yml`

Prevents commits containing sensitive files by:
- Scanning changed files against sensitive patterns
- Supporting exclusion patterns for intentional files
- Failing the workflow and commenting on PRs with violations

**Triggers**: PR opened/synchronized, push to main/master

**Customization**:
- Modify `.github/sensitive_files.yml` to change detection patterns
- Add new sensitive file types
- Configure exclusions for example files

### 🧪 Test Runner

**File**: `.github/workflows/test.yml` (calls `.github/workflows/reusable/test-runner.yml`)

Executes tests with support for:
- Multiple Node.js versions
- Different package managers (npm, yarn, pnpm)
- Custom test commands
- Dependency caching
- Test result artifacts

**Triggers**: PR to main/develop, push to main/develop

**Customization**:
```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable/test-runner.yml
    with:
      node-version: '18'
      package-manager: 'npm'
      test-command: 'test:ci'
```

### 🏷️ Versioning & Releases

**File**: `.github/workflows/version-and-release.yml`

Handles semantic versioning by:
- Analyzing commit messages for conventional commits
- Automatically bumping version numbers
- Updating package.json
- Creating GitHub releases with changelogs
- Generating semantic version tags

**Triggers**: Push to main/master

**Customization**:
- Modify `.github/versioning.yml` for custom versioning rules
- Configure release notes templates
- Set up different bump strategies

### ☁️ S3 Migration

**File**: `.github/workflows/s3-migration.yml`

Migrates S3 buckets between AWS accounts with:
- Cross-account bucket copying
- Metadata and ACL preservation
- Dry-run capability
- Comprehensive logging
- Support for single or multiple buckets

**Triggers**: Manual workflow dispatch

**Usage**:
1. Go to Actions → S3 Bucket Migration
2. Fill in source/target bucket names
3. Configure AWS profiles
4. Set migration options
5. Run the workflow

**Customization**:
- Modify the Python script for custom migration logic
- Add additional metadata preservation
- Configure different storage classes

### 👤 IAM User Creation

**File**: `.github/workflows/iam-user-creation.yml`

Creates IAM users with:
- Minimal permissions (readonly, developer, admin)
- Password complexity enforcement
- Force password change on first login
- Optional access key creation
- MFA policy enforcement
- Group assignments

**Triggers**: Manual workflow dispatch

**Usage**:
1. Go to Actions → IAM User Creation
2. Enter username and password
3. Select access level
4. Configure additional options
5. Run the workflow

**Customization**:
- Modify the Python script for custom policies
- Add additional security policies
- Configure different access levels

## 🔄 Reusability

All workflows are designed to be reusable across projects. To use in a new repository:

1. **Copy the entire `.github/` directory**
2. **Update configuration files** for your project
3. **Set up required secrets**
4. **Customize workflows** as needed

### Minimal Changes Required

- **Reviewer names/usernames** in `.github/auto_reviewers.yml`
- **Sensitive file patterns** in `.github/sensitive_files.yml`
- **Test commands** in `.github/workflows/test.yml`
- **AWS credentials/profile names** in repository secrets
- **IAM usernames/passwords** when running the workflow
- **Project-specific tagging rules** in `.github/versioning.yml`

## 🛡️ Security Features

- **Sensitive file detection** prevents accidental commits
- **Minimal IAM permissions** following least privilege principle
- **MFA enforcement** for IAM users
- **Password complexity requirements**
- **Secure credential handling** via GitHub secrets

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the workflows
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the workflow documentation
- Review the configuration examples

---

**Note**: These workflows are designed to be production-ready but should be tested in your specific environment before deployment.