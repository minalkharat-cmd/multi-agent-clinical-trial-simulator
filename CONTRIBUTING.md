# Contributing to ClinicalMind: Multi-Agent Clinical Trial Simulator

Thank you for your interest in contributing to ClinicalMind! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- - Docker and Docker Compose (optional, for containerized development)
  - - Git
   
    - ### Development Setup
   
    - 1. **Clone the repository**
      2.    ```bash
               git clone https://github.com/minalkharat-cmd/multi-agent-clinical-trial-simulator.git
               cd multi-agent-clinical-trial-simulator
               ```

            2. **Create a virtual environment**
            3.    ```bash
                     python -m venv venv
                     source venv/bin/activate  # On Windows: venv\Scripts\activate
                     ```

                  3. **Install dependencies**
                  4.    ```bash
                           pip install -e ".[dev]"
                           ```

                        4. **Set up pre-commit hooks**
                        5.    ```bash
                                 pre-commit install
                                 ```

                              5. **Configure environment variables**
                              6.    ```bash
                                       cp .env.example .env
                                       # Edit .env with your API keys
                                       ```

                                    ## 📝 Development Workflow

                                ### Branch Naming Convention

                          - `feature/` - New features
                          - - `fix/` - Bug fixes
                            - - `docs/` - Documentation updates
                              - - `refactor/` - Code refactoring
                                - - `test/` - Test additions or modifications
                                 
                                  - ### Commit Message Format
                                 
                                  - Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
                                 
                                  - ```
                                    <type>(<scope>): <description>

                                    [optional body]

                                    [optional footer]
                                    ```

                                    Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

                                    ### Pull Request Process

                                    1. Create a feature branch from `main`
                                    2. 2. Make your changes with proper tests
                                       3. 3. Ensure all tests pass: `pytest`
                                          4. 4. Run linting: `ruff check src/` and `black --check src/`
                                             5. 5. Submit a pull request with a clear description
                                               
                                                6. ## 🧪 Testing
                                               
                                                7. ```bash
                                                   # Run all tests
                                                   pytest

                                                   # Run with coverage
                                                   pytest --cov=src --cov-report=html

                                                   # Run specific test file
                                                   pytest tests/test_agents.py
                                                   ```

                                                   ## 📐 Code Style

                                                   We use:
                                                   - **Black** for code formatting
                                                   - - **Ruff** for linting
                                                     - - **MyPy** for type checking
                                                      
                                                       - ```bash
                                                         # Format code
                                                         black src/ tests/

                                                         # Check linting
                                                         ruff check src/

                                                         # Type checking
                                                         mypy src/
                                                         ```

                                                         ## 📚 Documentation

                                                         - Update docstrings for all public functions
                                                         - - Add type hints to all function signatures
                                                           - - Update README.md for user-facing changes
                                                            
                                                             - ## 🔒 Security
                                                            
                                                             - - Never commit API keys or secrets
                                                               - - Report security vulnerabilities privately
                                                                 - - Follow OWASP guidelines for healthcare data
                                                                  
                                                                   - ## 📄 License
                                                                  
                                                                   - By contributing, you agree that your contributions will be licensed under the MIT License.
