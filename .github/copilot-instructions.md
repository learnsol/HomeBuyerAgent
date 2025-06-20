<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This project is a multi-agent home buying application using the Google ADK (Agent Development Kit) framework. 

- Follow existing patterns for dependency injection and modular agent design.
- Agents should extend `Agent` or `LlmAgent` from google.adk and use `FunctionTool` for their primary functions.
- Orchestrator should coordinate agents using `google.adk` framework components.
- Configuration should be in `config/settings.py` and loaded via environment variables.
- Ensure all utilities are reusable and tests can inject mocks for dependencies.
- Use ADK patterns: Sequential Pipeline, Parallel Fan-Out/Gather, and proper session state management.
