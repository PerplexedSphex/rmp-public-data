# Opsiary Agents Documentation

This document provides an overview of all available agents in the Opsiary system.

## Available Agents

### Email Summary Agent
- **Purpose**: Generates concise email summaries for sales accounts
- **Location**: `/agents/email_summary_agent`
- **Configuration**: `config.json`
- **Usage**: `python -m cli.cli run email_summary_agent`
- **Details**: [Email Summary Agent Documentation](../agents/email_summary_agent/agent.md)

## Adding New Agents

To add a new agent to the system, follow these steps:

1. Create a new directory in the `agents` folder: `agents/your_agent_name`
2. Create the required files:
   - `agent.py`: The agent implementation
   - `agent.md`: Documentation with Mermaid diagram
   - `config.json`: Configuration for the agent
   - `prompts/`: Directory for prompt templates
3. Implement the Agent class with the required methods:
   - `__init__(self, config_path: str)`
   - `run(self, input_params: dict) -> dict`
4. Update this documentation file with the new agent

## Agent Structure Requirements

Each agent must include:

1. A valid `config.json` file in the agent directory
2. An `agent.py` file with an `Agent` class
3. An `agent.md` file with documentation and flow diagram
4. A `prompts` directory with any required prompt templates
5. The `Agent` class must implement the required API:
   - `__init__(self, config_path: str)`
   - `run(self, input_params: dict) -> dict`

## Validating Agents

To validate an agent without running it:

```bash
python -m cli.cli validate-agent your_agent_name
```

This will check that the agent meets all the required structure and API.