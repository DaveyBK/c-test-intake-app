# Development Guide

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DaveyBK/c-test-intake-app.git
   cd c-test-intake-app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Configure the application:**
   ```bash
   cp config.example.py config.py
   # Edit config.py with your settings
   ```

---

## Development Workflow

### Code Quality Standards

This project enforces code quality through automated checks:

- **Black** - Code formatting (line length: 100)
- **isort** - Import sorting
- **flake8** - Linting
- **pylint** - Advanced linting
- **mypy** - Type checking
- **bandit** - Security scanning

### Running Code Quality Checks

**Format code automatically:**
```bash
black .
isort .
```

**Check code quality:**
```bash
flake8 .
pylint *.py
mypy --ignore-missing-imports .
```

**Run all pre-commit hooks manually:**
```bash
pre-commit run --all-files
```

**Security scan:**
```bash
bandit -r . -ll
safety check
```

---

## Testing

### Run Tests

**Run all tests:**
```bash
python -m unittest discover tests/
```

**Run specific test file:**
```bash
python -m unittest tests.test_c_test_grader
```

**Run with coverage:**
```bash
coverage run -m unittest discover tests/
coverage report
coverage html  # Generate HTML report in htmlcov/
```

**Using pytest (alternative):**
```bash
pytest
pytest --cov=. --cov-report=html
```

---

## Git Workflow

### Branch Naming

- `main` - Production-ready code
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `copilot/description` - AI-assisted changes

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
git commit -m "feat(grader): add support for British spelling variants"
git commit -m "fix(parser): handle empty student answers correctly"
git commit -m "docs: update schema documentation"
git commit -m "test: add edge cases for C-Test grading"
```

### Pull Request Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **Run tests locally:**
   ```bash
   python -m unittest discover tests/
   pre-commit run --all-files
   ```

4. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature
   ```

5. **Create Pull Request on GitHub**

6. **Wait for CI checks to pass**

7. **Request review** (if CODEOWNERS is set up, reviewers are auto-assigned)

8. **Merge after approval**

---

## Continuous Integration

### GitHub Actions Workflows

Three automated workflows run on every push/PR:

#### 1. Python CI (`python-tests.yml`)
- Tests on Python 3.8, 3.9, 3.10, 3.11
- Runs all unit tests
- Generates coverage report
- Uploads to Codecov

#### 2. Code Quality (`code-quality.yml`)
- flake8 linting
- black formatting check
- isort import sorting check
- mypy type checking

#### 3. Security (`security.yml`)
- bandit security scanning
- safety dependency checking
- Runs weekly and on push to main

### Viewing CI Results

Check the **Actions** tab on GitHub to see:
- Test results for each Python version
- Code quality check results
- Security scan results

---

## Code Style Guide

### Python Style

Follow PEP 8 with these specifics:

- **Line length:** 100 characters
- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings (configurable)
- **Imports:** Grouped and sorted by isort
- **Docstrings:** Google style (preferred)

**Example:**

```python
from typing import List, Optional

from models import Student, CTestResult


def grade_c_test(
    answer_key: dict,
    student_answers: dict,
    accept_variants: bool = True
) -> tuple:
    """
    Grade a C-Test submission.

    Args:
        answer_key: Dictionary mapping item numbers to correct answers
        student_answers: Dictionary mapping item numbers to student answers
        accept_variants: Whether to accept spelling variants

    Returns:
        Tuple of (score, items, feedback)
    """
    # Implementation
    pass
```

### Documentation

- All modules should have docstrings
- Complex functions should have detailed docstrings
- Use type hints where appropriate
- Update README.md for major changes
- Keep SCHEMA_REVIEW.md current with database changes

---

## Database Migrations

### Local Database (c_test.db)

Changes to local schema:
1. Update `SCHEMA` constant in `db.py`
2. Test with fresh database
3. Document in code comments
4. Add migration notes to PR

### Shared Database (inventory.db)

**CRITICAL:** Changes to inventory.db require careful planning.

1. **Propose changes** in an issue first
2. **Update** `CREATE_C_TEST_TABLES` in `inventory_db.py`
3. **Document** in `SCHEMA_REVIEW.md`
4. **Test** on a database copy
5. **Get approval** before merging
6. **Backup** inventory.db before deployment

See `SCHEMA_REVIEW.md` for detailed schema information.

---

## Troubleshooting

### Pre-commit hooks fail

**Clear cache and reinstall:**
```bash
pre-commit clean
pre-commit install --install-hooks
pre-commit run --all-files
```

### Import errors

**Reinstall dependencies:**
```bash
pip install -r requirements.txt -r requirements-dev.txt --upgrade
```

### Tests fail locally but pass in CI

**Check Python version:**
```bash
python --version
```

Ensure you're using Python 3.8+.

### Coverage too low

**Identify uncovered code:**
```bash
coverage run -m unittest discover tests/
coverage report --show-missing
```

Add tests for uncovered lines.

---

## Release Process

1. **Update version** in relevant files
2. **Update CHANGELOG.md** with changes
3. **Create release branch:** `release/vX.Y.Z`
4. **Run full test suite**
5. **Create GitHub Release** with tag
6. **Deploy** to production environment

---

## Resources

### Documentation
- [README.md](../README.md) - App overview
- [SCHEMA_REVIEW.md](../SCHEMA_REVIEW.md) - Database schemas
- [SETUP_GUIDE.md](../SETUP_GUIDE.md) - Integration setup
- [GAP_ANALYSIS_REPORT.md](../GAP_ANALYSIS_REPORT.md) - Architecture analysis

### Tools
- [Black documentation](https://black.readthedocs.io/)
- [isort documentation](https://pycqa.github.io/isort/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [pytest documentation](https://docs.pytest.org/)
- [pre-commit documentation](https://pre-commit.com/)

### GitHub
- [Branch Protection Rules](.github/BRANCH_PROTECTION_RULES.md)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)

---

## Getting Help

- **Issues:** Use GitHub Issues for bug reports and feature requests
- **Discussions:** Use GitHub Discussions for questions
- **Code Review:** Request review from CODEOWNERS
- **Documentation:** Check existing docs in the repository

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

All contributions must pass CI checks and code review before merging.
