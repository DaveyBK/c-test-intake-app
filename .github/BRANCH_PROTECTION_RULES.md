# GitHub Branch Protection Rules Configuration

This document outlines the recommended branch protection rules for the C-Test Intake App repository.

## Main Branch Protection Rules

### Required Settings

**Branch name pattern:** `main`

#### Protect matching branches:
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [ ] Require review from Code Owners (optional - create CODEOWNERS file first)

- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
  - Required status checks:
    - `test (3.8)` - Python 3.8 tests
    - `test (3.9)` - Python 3.9 tests
    - `test (3.10)` - Python 3.10 tests
    - `test (3.11)` - Python 3.11 tests
    - `lint` - Code quality checks

- [x] Require conversation resolution before merging

- [x] Require signed commits (recommended for security)

- [x] Require linear history

- [x] Include administrators (optional - strict mode)

- [ ] Allow force pushes (keep disabled)

- [ ] Allow deletions (keep disabled)

### Additional Settings

#### Rules applied to everyone including administrators:
- Restrict who can push to matching branches
  - Only allow specific people, teams, or apps to push

#### Lock branch:
- [ ] Lock branch (not recommended for active development)

---

## Development Branches

### Copilot Branches

**Branch name pattern:** `copilot/*`

#### Protect matching branches:
- [x] Require a pull request before merging
  - [x] Require approvals: 1

- [x] Require status checks to pass before merging
  - Required status checks:
    - `test (3.10)` - At least one Python version
    - `lint` - Code quality checks

- [ ] Require conversation resolution before merging (optional)

- [ ] Allow force pushes (allowed for development branches)

- [ ] Allow deletions (allowed for cleanup)

---

## Feature Branches

**Branch name pattern:** `feature/*`

#### Protect matching branches:
- [x] Require status checks to pass before merging
  - Required status checks:
    - `test (3.10)` - At least one Python version
    - `lint` - Code quality checks

- [ ] Allow force pushes (allowed for development)

- [ ] Allow deletions (allowed for cleanup)

---

## How to Apply These Rules

### Via GitHub Web UI:
1. Go to Repository Settings
2. Click "Branches" in the left sidebar
3. Click "Add branch protection rule"
4. Enter the branch name pattern
5. Configure the settings as outlined above
6. Click "Create" or "Save changes"

### Via GitHub API:
```bash
# Example using GitHub CLI
gh api repos/{owner}/{repo}/branches/{branch}/protection \
  --method PUT \
  --field required_pull_request_reviews.required_approving_review_count=1 \
  --field required_status_checks.strict=true \
  --field required_status_checks.contexts='["test (3.10)", "lint"]'
```

---

## CODEOWNERS File (Optional)

Create `.github/CODEOWNERS` to automatically request reviews:

```
# Global owners
* @DaveyBK

# Python code
*.py @DaveyBK

# Tests
/tests/ @DaveyBK

# Documentation
*.md @DaveyBK

# Configuration
*.yml @DaveyBK
*.yaml @DaveyBK
*.toml @DaveyBK
```

---

## Rulesets (GitHub Rulesets - Modern Approach)

GitHub now offers "Rulesets" as a more flexible alternative to branch protection rules.

### Recommended Ruleset Configuration:

**Name:** Main Protection Ruleset

**Target branches:** `main`

**Rules:**
1. **Require pull request before merging**
   - Required approvals: 1
   - Dismiss stale reviews: Yes

2. **Require status checks to pass**
   - Required checks:
     - Python CI / test (3.8)
     - Python CI / test (3.9)
     - Python CI / test (3.10)
     - Python CI / test (3.11)
     - Code Quality / lint

3. **Block force pushes**

4. **Require signed commits**

5. **Require linear history**

**Bypass list:**
- Repository administrators (optional)

---

## Security Settings

### Additional Repository Security Settings:

1. **Dependabot alerts:** Enabled
2. **Dependabot security updates:** Enabled
3. **Code scanning:** Enable CodeQL analysis
4. **Secret scanning:** Enabled
5. **Private vulnerability reporting:** Enabled

### Dependabot Configuration

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "DaveyBK"
```

---

## Summary

These rulesets provide:
- ✅ Automated testing before merge
- ✅ Code quality enforcement
- ✅ Security scanning
- ✅ Protected main branch
- ✅ Flexible development workflow
- ✅ Comprehensive documentation

Apply these rules to maintain high code quality and security standards for the C-Test Intake App.
