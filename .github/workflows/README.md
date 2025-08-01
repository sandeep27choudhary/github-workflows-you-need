# GitHub Workflows

This directory contains all the GitHub Actions workflows for the project. Each workflow is designed to be modular and reusable across different projects.

## 📋 Workflow Overview

| Workflow | Description | Trigger | Manual |
|----------|-------------|---------|---------|
| `pr-reviewers.yml` | Auto-assign PR reviewers based on file paths | PR events | ❌ |
| `sensitive-files-check.yml` | Detect and prevent sensitive file commits | PR/Push events | ❌ |
| `test.yml` | Run tests using reusable workflow | PR/Push events | ❌ |
| `version-and-release.yml` | Semantic versioning and releases | Push to main | ❌ |
| `s3-migration.yml` | Cross-account S3 bucket migration | Manual | ✅ |
| `iam-user-creation.yml` | Create IAM users with minimal permissions | Manual | ✅ |

## 🔧 Configuration

### Required Secrets

#### For AWS Workflows
```bash
# Basic AWS credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# For cross-account S3 migration
AWS_ACCESS_KEY_ID_SOURCE=source_account_key
AWS_SECRET_ACCESS_KEY_SOURCE=source_account_secret
AWS_ROLE_ARN_SOURCE=arn:aws:iam::source:role/role-name
AWS_ACCESS_KEY_ID_TARGET=target_account_key
AWS_SECRET_ACCESS_KEY_TARGET=target_account_secret
AWS_ROLE_ARN_TARGET=arn:aws:iam::target:role/role-name
```

#### For NPM Publishing
```bash
NPM_TOKEN=your_npm_token
```

## 📁 Directory Structure

```
workflows/
├── pr-reviewers.yml              # Auto-assign PR reviewers
├── sensitive-files-check.yml     # Detect sensitive files
├── test.yml                      # Main test workflow
├── version-and-release.yml       # Versioning and releases
├── s3-migration.yml              # S3 bucket migration
├── iam-user-creation.yml         # IAM user creation
├── reusable/                     # Reusable workflow components
│   └── test-runner.yml          # Reusable test workflow
└── config/                       # Default configuration files
    ├── default_reviewers.yml     # Default reviewer config
    ├── default_sensitive_files.yml # Sensitive files config
    └── default_versioning.yml    # Versioning config
```

## 🚀 Quick Setup

1. **Copy workflows** to your repository's `.github/workflows/` directory
2. **Set up secrets** in your repository settings
3. **Create custom config files** (optional) to override defaults
4. **Test workflows** in a development environment

## 📖 Individual Workflow Documentation

### [PR Reviewers](./pr-reviewers.yml)
Automatically assigns reviewers to pull requests based on file paths and configuration.

**Configuration**: `.github/auto_reviewers.yml` or `.github/workflows/config/default_reviewers.yml`

### [Sensitive Files Check](./sensitive-files-check.yml)
Detects and prevents commits containing sensitive files like `.env`, `*.pem`, etc.

**Configuration**: `.github/sensitive_files.yml` or `.github/workflows/config/default_sensitive_files.yml`

### [Test Runner](./test.yml)
Executes tests using the reusable test workflow with support for multiple package managers.

**Configuration**: Modify the workflow inputs in `test.yml`

### [Version and Release](./version-and-release.yml)
Handles semantic versioning, package.json updates, and GitHub releases.

**Configuration**: `.github/versioning.yml` or `.github/workflows/config/default_versioning.yml`

### [S3 Migration](./s3-migration.yml)
Migrates S3 buckets between AWS accounts with metadata preservation.

**Usage**: Manual workflow dispatch with input parameters

### [IAM User Creation](./iam-user-creation.yml)
Creates IAM users with minimal permissions and security policies.

**Usage**: Manual workflow dispatch with input parameters

## 🔄 Reusability

All workflows are designed to be reusable. To use in a new project:

1. **Copy the entire `.github/` directory**
2. **Update configuration files** for your project
3. **Set up required secrets**
4. **Customize as needed**

### Minimal Changes Required

- **Reviewer names** in `.github/auto_reviewers.yml`
- **Sensitive file patterns** in `.github/sensitive_files.yml`
- **Test commands** in `.github/workflows/test.yml`
- **AWS credentials** in repository secrets
- **Versioning rules** in `.github/versioning.yml`

## 🛡️ Security

- All workflows use GitHub secrets for sensitive data
- IAM workflows follow least privilege principle
- Sensitive file detection prevents accidental commits
- MFA enforcement for IAM users

## 📝 Notes

- Workflows are production-ready but should be tested in your environment
- Configuration files can be overridden by creating custom versions in your repository
- Manual workflows require appropriate permissions to run
- All workflows include comprehensive logging and error handling 