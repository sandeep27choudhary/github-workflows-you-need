# Workflow Summary

This document provides a quick overview of all available GitHub Actions workflows in this repository.

## 📋 Workflow Overview

| Workflow | File | Trigger | Purpose | Manual |
|----------|------|---------|---------|---------|
| **PR Reviewers** | `pr-reviewers.yml` | PR events | Auto-assign reviewers based on file paths | ❌ |
| **Sensitive Files Check** | `sensitive-files-check.yml` | PR/Push | Detect and prevent sensitive file commits | ❌ |
| **Test Runner** | `test.yml` | PR/Push | Execute tests with multiple package managers | ❌ |
| **Version & Release** | `version-and-release.yml` | Push to main | Semantic versioning and GitHub releases | ❌ |
| **S3 Migration** | `s3-migration.yml` | Manual | Cross-account S3 bucket migration | ✅ |
| **IAM User Creation** | `iam-user-creation.yml` | Manual | Create IAM users with minimal permissions | ✅ |

## 🔍 Detailed Workflow Information

### 1. PR Reviewers (`pr-reviewers.yml`)

**Purpose**: Automatically assign reviewers to pull requests based on file paths and configuration.

**Features**:
- ✅ Default reviewers for all PRs
- ✅ Path-based reviewer assignment using regex patterns
- ✅ Configurable via `.github/auto_reviewers.yml`
- ✅ Supports multiple reviewers per path pattern
- ✅ Handles existing reviewers gracefully

**Configuration**:
```yaml
# .github/auto_reviewers.yml
default_reviewers:
  - "team-lead"
  - "senior-dev"

path_reviewers:
  "frontend/.*":
    - "frontend-lead"
  "backend/.*":
    - "backend-lead"
```

**Triggers**: PR opened, synchronized, or marked ready for review

---

### 2. Sensitive Files Check (`sensitive-files-check.yml`)

**Purpose**: Detect and prevent commits containing sensitive files like `.env`, `*.pem`, etc.

**Features**:
- ✅ Comprehensive sensitive file pattern detection
- ✅ Exclusion patterns for intentional files
- ✅ PR comments with detailed violation information
- ✅ Configurable via `.github/sensitive_files.yml`
- ✅ Supports both PR and push events

**Configuration**:
```yaml
# .github/sensitive_files.yml
sensitive_patterns:
  - "\\.env$"
  - ".*\\.key$"
  - ".*\\.pem$"

excluded_patterns:
  - "\\.env\\.example$"
  - "docs/.*"
```

**Triggers**: PR opened/synchronized, push to main/master

---

### 3. Test Runner (`test.yml`)

**Purpose**: Execute tests using a reusable workflow with support for multiple package managers.

**Features**:
- ✅ Reusable workflow design
- ✅ Multiple Node.js version support
- ✅ Package manager flexibility (npm, yarn, pnpm)
- ✅ Dependency caching for performance
- ✅ Test result artifacts
- ✅ Customizable test commands

**Configuration**:
```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable/test-runner.yml
    with:
      node-version: '18'
      package-manager: 'npm'
      test-command: 'test:ci'
```

**Triggers**: PR to main/develop, push to main/develop

---

### 4. Version & Release (`version-and-release.yml`)

**Purpose**: Handle semantic versioning, package.json updates, and GitHub releases.

**Features**:
- ✅ Conventional commit analysis
- ✅ Automatic semantic version bumping
- ✅ Package.json version updates
- ✅ GitHub release creation with changelogs
- ✅ Configurable versioning rules
- ✅ Skip keywords support

**Configuration**:
```yaml
# .github/versioning.yml
version_bump_rules:
  major:
    - "BREAKING CHANGE"
  minor:
    - "feat:"
  patch:
    - "fix:"
    - "docs:"
```

**Triggers**: Push to main/master

---

### 5. S3 Migration (`s3-migration.yml`)

**Purpose**: Migrate S3 buckets between AWS accounts with metadata preservation.

**Features**:
- ✅ Cross-account bucket migration
- ✅ Metadata and ACL preservation
- ✅ Dry-run capability
- ✅ Comprehensive logging
- ✅ Support for single or multiple buckets
- ✅ Progress tracking and error handling

**Inputs**:
- `source_bucket`: Source S3 bucket name
- `target_bucket`: Target S3 bucket name
- `source_account_profile`: AWS profile for source account
- `target_account_profile`: AWS profile for target account
- `migrate_all`: Migrate all buckets or just specified ones
- `preserve_acl`: Preserve ACLs during migration
- `preserve_metadata`: Preserve metadata during migration
- `dry_run`: Perform a dry run without actual migration

**Triggers**: Manual workflow dispatch

---

### 6. IAM User Creation (`iam-user-creation.yml`)

**Purpose**: Create IAM users with minimal permissions and security policies.

**Features**:
- ✅ Minimal permissions (readonly, developer, admin)
- ✅ Password complexity enforcement
- ✅ Force password change on first login
- ✅ Optional access key creation
- ✅ MFA policy enforcement
- ✅ Group assignments
- ✅ Security best practices

**Inputs**:
- `username`: IAM username to create
- `password`: Initial password for the user
- `access_level`: Access level (readonly, developer, admin)
- `force_password_change`: Force password change on first login
- `create_access_keys`: Create access keys for the user
- `groups`: Comma-separated list of IAM groups

**Triggers**: Manual workflow dispatch

## 🔧 Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `default_reviewers.yml` | Default PR reviewer configuration | `.github/workflows/config/` |
| `default_sensitive_files.yml` | Default sensitive file patterns | `.github/workflows/config/` |
| `default_versioning.yml` | Default versioning rules | `.github/workflows/config/` |

## 📁 Scripts

| Script | Purpose | Dependencies |
|--------|---------|--------------|
| `s3_migration.py` | S3 bucket migration logic | boto3, botocore |
| `iam_user_creation.py` | IAM user creation logic | boto3, botocore |

## 🔑 Required Secrets

### Basic Workflows (PR Reviewers, Sensitive Files, Tests, Versioning)
- `GITHUB_TOKEN` (automatically provided)

### AWS Workflows
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional, defaults to us-east-1)

### Cross-Account S3 Migration
- `AWS_ACCESS_KEY_ID_SOURCE`
- `AWS_SECRET_ACCESS_KEY_SOURCE`
- `AWS_ROLE_ARN_SOURCE`
- `AWS_ACCESS_KEY_ID_TARGET`
- `AWS_SECRET_ACCESS_KEY_TARGET`
- `AWS_ROLE_ARN_TARGET`

### NPM Publishing
- `NPM_TOKEN`

## 🚀 Quick Start

1. **Copy workflows** to your repository's `.github/workflows/` directory
2. **Set up required secrets** in your repository settings
3. **Create custom config files** (optional) to override defaults
4. **Test workflows** in a development environment

## 🔄 Reusability

All workflows are designed to be reusable across projects with minimal changes:

- **Reviewer names** in `.github/auto_reviewers.yml`
- **Sensitive file patterns** in `.github/sensitive_files.yml`
- **Test commands** in `.github/workflows/test.yml`
- **AWS credentials** in repository secrets
- **Versioning rules** in `.github/versioning.yml`

## 🛡️ Security Features

- Sensitive file detection prevents accidental commits
- Minimal IAM permissions following least privilege principle
- MFA enforcement for IAM users
- Password complexity requirements
- Secure credential handling via GitHub secrets

## 📚 Documentation

- [Main README](README.md) - Comprehensive project documentation
- [Setup Guide](SETUP.md) - Detailed setup instructions
- [Workflows README](.github/workflows/README.md) - Workflow-specific documentation

## 🤝 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the workflow documentation
- Review the configuration examples 