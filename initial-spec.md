Here’s your fully refined, comprehensive final specification, exactly as requested. This includes the previously omitted Prompt Manager Utility, improved CLI defaults, "latest" prompt handling, and a complete, explicit set of TDD Acceptance Criteria.

📌 FINAL Project Specification
📁 Project Structure
arduino
Copy
Edit
revops-agent-system/
├── cli/
│   ├── cli.py
│   └── commands.py
│
├── agents/
│   └── email_summary_agent/
│       ├── agent.py
│       ├── agent.md
│       ├── config.json
│       └── prompts/
│           └── email_prompt.txt
│
├── adapters/
│   ├── crm/
│   │   ├── salesforce_adapter.py
│   │   └── gong_adapter.py
│   └── llm/
│       ├── openai_adapter.py
│       ├── claude_adapter.py
│       └── gemini_adapter.py
│
├── core/
│   ├── job_runner.py
│   ├── logger.py
│   ├── orchestrator.py
│   ├── utils.py                 # prompt loading utilities
│   └── prompt_manager.py        # prompt versioning CLI utility
│
├── storage/
│   ├── logs/
│   └── job_results/
│
├── config/
│   └── .env
│
├── docs/
│   └── AGENTS.md
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
🚀 Complete APIs & Interfaces
✅ CLI API
bash
Copy
Edit
cli.py run [agent_name] --config=config.json
cli.py run                     # Default: run agent in current dir with current config
cli.py validate-agent [agent_name] --config=config.json
cli.py logs --job-id JOB_ID
cli.py results --job-id JOB_ID
cli.py list agents
cli.py status --job-id JOB_ID
Default behavior:

cli.py run without arguments runs agent in current directory with current config.json.
✅ Agent API
python
Copy
Edit
class Agent:
    def __init__(self, config_path: str):
        pass

    def run(self, input_params: dict) -> dict:
        pass
Each agent includes:

agent.md: Description, API usage, Mermaid flow diagram
config.json
Prompts in /prompts
✅ Adapters API
CRMAdapter:

python
Copy
Edit
class CRMAdapter:
    def fetch_data(self, query: dict) -> dict:
        pass

    def update_data(self, data: dict) -> bool:
        pass
LLMAdapter:

python
Copy
Edit
class LLMAdapter:
    def complete(prompt: str, model: str, temperature: float = 0.7, tools=None, files=None, **kwargs) -> dict:
        pass
✅ Prompt Manager CLI Utility
Enforces prompt versioning conventions via Git tags:

bash
Copy
Edit
prompt-cli commit <prompt_file> --tag email_prompt/v1.1.0 --message "Update prompt instructions"
prompt-cli list-tags [prompt_name]
prompt-cli history <prompt_file>
Enforces explicitly:

Single-file commits
Semantic versioning with prompt_name/vX.Y.Z convention
✅ Prompt Loading Utility (core/utils.py)
python
Copy
Edit
def load_prompt(repo_path, file_name, version_tag="latest"):
    repo = Repo(repo_path)
    if version_tag == "latest":
        version_tag = sorted(
            [t.name for t in repo.tags if t.name.startswith(file_name)],
            reverse=True
        )[0]
    prompt = repo.git.show(f"{version_tag}:{file_name}")
    return prompt
Supports "latest" to dynamically load most recent prompt version.
✅ Config Management
Implicit versioning via Git commits.
Runtime logs include explicit snapshots:
json
Copy
Edit
"config_snapshot": {...},
"git_commit_hash": "abc123"
✅ Logging & Storage
Logs: storage/logs/<job_id>.json
Results: storage/job_results/<job_id>_results.json
Job log structured clearly:

json
Copy
Edit
{
  "job_id": "20250310-1430",
  "agent": "email_summary_agent",
  "timestamp": "...",
  "config_snapshot": {...},
  "prompt_snapshot": "...",
  "git_commit_hash": "...",
  "metrics": {
    "llm_latency_seconds": 1.8,
    "tokens_used": 800,
    "api_call_counts": {"salesforce": 1, "openai": 1}
  },
  "status": "completed"
}
✅ Environment Variables (.env)
env
Copy
Edit
OPENAI_API_KEY=xxxx
SALESFORCE_API_KEY=xxxx
✅ Documentation (agent.md)
Description & APIs used
Mermaid diagram before development begins
✅ Complete TDD Acceptance Criteria
📋 CLI
✅ Runs default agent (cli.py run) from current directory without args.
✅ Validates agents explicitly (cli.py validate-agent) before runtime.
✅ Logs, results, and status commands accurately retrieve information.
📋 Agents
✅ Instantiates correctly from specified config file.
✅ Successfully composes and executes adapters.
✅ Logs correct output structured in storage.
📋 Adapters
✅ CRMAdapter fetches and updates mocked data successfully.
✅ LLMAdapter returns correctly structured completion data from mock APIs.
✅ Clearly handles API errors (timeouts, auth errors).
📋 Prompt Manager Utility
✅ Enforces single-file commits for prompt changes.
✅ Rejects improperly formatted tags (prompt_name/vX.Y.Z enforced).
✅ Clearly lists prompt tags & commit histories.
📋 Prompt Loading
✅ Loads explicit prompt versions correctly via Git tags.
✅ "latest" always returns newest tag version.
✅ Handles missing/nonexistent prompt tags gracefully.
📋 Config Versioning & Logging
✅ Implicit config versioning via Git commits works correctly.
✅ Runtime logs always include explicit config snapshot and Git commit hash.
📋 Logging & Storage
✅ Logs written predictably to structured JSON files.
✅ Job results stored clearly in separate JSON files.
📋 Metrics
✅ Logs execution metrics (LLM latency, tokens used, API call counts).
📋 Documentation
✅ Each agent includes descriptive agent.md and accurate Mermaid diagram.
✅ Central docs/AGENTS.md always updated and consistent with agents.
📋 Secrets Management
✅ Credentials only loaded from .env; never committed to repo.
🛠️ Minimal Dependencies
arduino
Copy
Edit
GitPython
click
requests
python-dotenv
pytest
🚩 Immediate MVP Next Steps
✅ Set up repo exactly as above.
✅ Implement Prompt Manager Utility immediately.
✅ Implement CLI defaults (cli.py run) & validation mode.
✅ Explicitly test prompt loading, especially "latest".
✅ Fully implement logging including config and prompt snapshots.
✅ Document clearly with agent.md before starting code.
🎯 This specification is now fully complete and explicitly addresses every requirement you've outlined. It captures a clear, actionable path forward for a robust, maintainable MVP ready for development.

If this fully aligns with your vision, you're all set. Otherwise, let me know if there's any final nuance you'd like to adjust!