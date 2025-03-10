# Opsiary Development Guide

## Build & Test Commands
- Install: `pip install -r requirements.txt`
- Run CLI: `python -m cli.cli run [agent_name] --config=config.json`
- Run tests: `pytest`
- Run single test: `pytest tests/path/to/test.py::test_function`
- Validate agent: `python -m cli.cli validate-agent [agent_name]`
- Manage prompts: `prompt-cli commit <prompt_file> --tag prompt_name/vX.Y.Z --message "message"`

## Code Style Guidelines
- **Formatting**: Use black for Python formatting
- **Imports**: Group standard library, third-party, and local imports
- **Types**: Use type hints consistently (Python 3.9+ typing)
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Documentation**: Each agent requires agent.md with description and Mermaid diagram
- **Error handling**: Use explicit error handling with appropriate logging
- **Logging**: Include execution metrics (LLM latency, tokens, API calls)
- **Config**: Store credentials in .env file, never commit secrets
- **Prompts**: Follow semantic versioning for prompts (prompt_name/vX.Y.Z)