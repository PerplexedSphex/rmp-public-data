# Opsiary

A flexible agent system for RevOps automation tasks, integrating with CRM systems and LLMs to streamline sales operations.

## Features

- Agent-based architecture for modular functionality
- CLI for running, validating, and monitoring agents
- Integrated CRM adapters (Salesforce, Gong)
- LLM adapters (OpenAI, Claude)
- Prompt versioning with Git tags
- Comprehensive logging and metrics

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/opsiary.git
cd opsiary

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/.env.example config/.env
# Edit config/.env with your API keys
```

### Running an Agent

```bash
# Run with specific agent
python -m cli.cli run email_summary_agent

# Run from agent directory (uses current directory)
cd agents/email_summary_agent
python -m cli.cli run
```

### Prompt Management

```bash
# Commit a prompt with versioning
python -m cli.commands prompt-cli commit agents/email_summary_agent/prompts/email_prompt.txt --tag email_prompt/v1.0.0 --message "Initial prompt version"

# List all prompt versions
python -m cli.commands prompt-cli list-tags email_prompt
```

## Documentation

- [Agent Documentation](docs/AGENTS.md)
- [Development Guide](CLAUDE.md)

## Project Structure

```
opsiary/
├── cli/                  # Command line interface
├── agents/               # Agent implementations
├── adapters/             # External system adapters
│   ├── crm/              # CRM system adapters
│   └── llm/              # Language model adapters
├── core/                 # Core utilities
├── storage/              # Data storage
├── config/               # Configuration
├── docs/                 # Documentation
└── tests/                # Test suite
```