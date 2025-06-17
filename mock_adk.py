"""
Mock ADK Framework for development and testing.
This simulates the ADK Agent and FunctionTool classes following ADK patterns.
"""
import inspect
import asyncio
from typing import Callable, List, Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod

class Event:
    """Mock Event class for ADK events."""
    def __init__(self, author: str, content: Any = None, actions: Any = None):
        self.author = author
        self.content = content
        self.actions = actions

class EventActions:
    """Mock EventActions for controlling event flow."""
    def __init__(self, escalate: bool = False):
        self.escalate = escalate

class InvocationContext:
    """Mock InvocationContext for agent execution context."""
    def __init__(self, session_state: Dict[str, Any] = None):
        self.session = type('Session', (), {})()
        self.session.state = session_state or {}
        self.branch = "main"

class FunctionTool:
    """Mock FunctionTool class that wraps a function for agent use."""
    def __init__(self, func: Callable):
        if not callable(func):
            raise TypeError("Tool function must be callable.")
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or f"Tool for {func.__name__}"
        self.parameters = self._extract_parameters()

    def _extract_parameters(self):
        sig = inspect.signature(self.func)
        params = {}
        for name, param in sig.parameters.items():
            params[name] = {
                "type": str(param.annotation) if param.annotation != param.empty else "any",
                "required": param.default == param.empty,
                "default": param.default if param.default != param.empty else None
            }
        return params

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class BaseAgent(ABC):
    """Mock BaseAgent following ADK patterns."""
    def __init__(self, name: str, description: str = "", sub_agents: List['BaseAgent'] = None):
        self.name = name
        self.description = description
        self.sub_agents = sub_agents or []
        self.parent_agent = None
        
        # Set parent relationship for sub-agents
        for agent in self.sub_agents:
            if agent.parent_agent is not None:
                raise ValueError(f"Agent {agent.name} already has a parent")
            agent.parent_agent = self

    def find_agent(self, name: str) -> 'BaseAgent':
        """Find agent by name in the hierarchy."""
        if self.name == name:
            return self
        for agent in self.sub_agents:
            found = agent.find_agent(name)
            if found:
                return found
        return None

    @abstractmethod
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Implementation of agent execution."""
        pass

    async def run_stream_async(self, user_input: str, ctx: InvocationContext = None) -> AsyncGenerator[Event, None]:
        """Main execution method."""
        if ctx is None:
            ctx = InvocationContext()
        
        async for event in self._run_async_impl(ctx):
            yield event

class LlmAgent(BaseAgent):
    """Mock LLM Agent following ADK patterns."""
    def __init__(self, 
                 name: str,
                 model: str = "gemini-1.5-flash",
                 description: str = "",
                 instruction: str = "",
                 tools: List[FunctionTool] = None,
                 sub_agents: List[BaseAgent] = None,
                 output_key: str = None,
                 temperature: float = 0.3,
                 max_tokens: int = 1024):
        super().__init__(name, description, sub_agents)
        self.model = model
        self.instruction = instruction
        self.tools = {tool.name: tool for tool in tools} if tools else {}
        self.output_key = output_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Mock LLM execution."""
        yield Event(author=self.name, content="Processing with LLM...")
        await asyncio.sleep(0.1)
        
        # Execute tools if available
        if self.tools:
            # For demo purposes, execute the first tool with session state data
            tool_name = list(self.tools.keys())[0]
            tool = self.tools[tool_name]
            
            # Get relevant data from session state based on tool name
            if "find_listings" in tool_name:
                user_criteria = ctx.session.state.get("user_criteria", {})
                result = tool.func(user_criteria)
                yield Event(author=self.name, content=f"Executed {tool_name} with criteria: {user_criteria}")
            elif "analyze_neighborhood" in tool_name:
                neighborhood_data = ctx.session.state.get("neighborhood_data", {})
                result = tool.func(neighborhood_data)
                yield Event(author=self.name, content=f"Executed {tool_name}")
            elif "analyze_hazards" in tool_name:
                hazard_data = ctx.session.state.get("hazard_data", {})
                result = tool.func(hazard_data)
                yield Event(author=self.name, content=f"Executed {tool_name}")
            elif "calculate_affordability" in tool_name:
                financial_info = ctx.session.state.get("user_financial_info", {})
                result = tool.func(financial_info)
                yield Event(author=self.name, content=f"Executed {tool_name}")
            elif "generate_recommendation" in tool_name:
                aggregated_data = ctx.session.state.get("aggregated_analysis", {})
                result = tool.func(aggregated_data)
                yield Event(author=self.name, content=f"Executed {tool_name}")
            else:
                result = f"Mock LLM result from {self.name}"
            
            # Save to output_key if specified
            if self.output_key:
                ctx.session.state[self.output_key] = result
                yield Event(author=self.name, content=f"Saved result to session state: {self.output_key}")
        else:
            # Simple mock execution - in real ADK this would involve LLM calls
            result = f"Mock LLM result from {self.name}"
            
            # Save to output_key if specified
            if self.output_key:
                ctx.session.state[self.output_key] = result
            
        yield Event(author=self.name, content=result)

class SequentialAgent(BaseAgent):
    """Mock Sequential Agent for pipeline execution."""
    def __init__(self, name: str, description: str = "", sub_agents: List[BaseAgent] = None):
        super().__init__(name, description, sub_agents)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Execute sub-agents sequentially, passing the same context."""
        yield Event(author=self.name, content=f"Starting sequential execution of {len(self.sub_agents)} agents")
        
        for agent in self.sub_agents:
            yield Event(author=self.name, content=f"Executing agent: {agent.name}")
            async for event in agent.run_stream_async("", ctx):
                yield event
        
        yield Event(author=self.name, content="Sequential execution completed")

class ParallelAgent(BaseAgent):
    """Mock Parallel Agent for concurrent execution."""
    def __init__(self, name: str, description: str = "", sub_agents: List[BaseAgent] = None):
        super().__init__(name, description, sub_agents)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Execute sub-agents in parallel with proper branch contexts."""
        yield Event(author=self.name, content=f"Starting parallel execution of {len(self.sub_agents)} agents")
        
        # Create tasks for parallel execution with branch contexts
        async def run_with_branch(agent, branch_name):
            # Create a copy of the context with modified branch
            branch_ctx = InvocationContext(ctx.session.state)
            branch_ctx.branch = f"{ctx.branch}.{branch_name}"
            
            events = []
            async for event in agent.run_stream_async("", branch_ctx):
                events.append(event)
            
            # Merge branch state back to main context
            ctx.session.state.update(branch_ctx.session.state)
            return events
        
        # Start all agents concurrently
        tasks = [run_with_branch(agent, agent.name) for agent in self.sub_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Yield all events from parallel execution
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                yield Event(author=self.name, content=f"Error in {self.sub_agents[i].name}: {result}")
            else:
                for event in result:
                    yield event
        
        yield Event(author=self.name, content="Parallel execution completed")

class AgentTool:
    """Mock AgentTool for explicit agent invocation."""
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.name = agent.name
        self.description = agent.description

    async def run_async(self, ctx: InvocationContext, **kwargs) -> Any:
        """Execute the wrapped agent and return result."""
        # Update context state with kwargs
        ctx.session.state.update(kwargs)
        
        final_result = None
        async for event in self.agent.run_stream_async("", ctx):
            if event.content:
                final_result = event.content
        
        return final_result
