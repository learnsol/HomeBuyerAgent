<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This project is a multi-agent home buying application using a mock Google ADK framework. 

- Follow existing patterns for dependency injection and modular agent design.
- Agents should extend `BaseAgent` and use `FunctionTool` for their primary functions.
- Orchestrator should coordinate agents using `mock_adk.Agent`.
- Configuration should be in `config/settings.py` and loaded via environment variables.
- Ensure all utilities are reusable and tests can inject mocks for dependencies.
