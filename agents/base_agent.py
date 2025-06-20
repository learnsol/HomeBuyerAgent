"""
Base Agent class for the Home Buyer Agent application following ADK patterns.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator
from google.adk.agents import Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.sessions import Session

class HomeBuyerBaseAgent(Agent):
    """Base class for Home Buyer agents following ADK patterns."""
    
    def __init__(self, name: str, description: str = "", sub_agents: list = None):
        super().__init__(name=name, description=description, sub_agents=sub_agents or [])
        self._log(f"HomeBuyerBaseAgent '{self.name}' initialized.")

    def _log(self, message: str):
        print(f"[{self.name} BASE LOG]: {message}")

    @abstractmethod
    async def process_business_logic(self, ctx: InvocationContext) -> Any:
        """Process business logic specific to this agent."""
        pass

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Implementation following ADK BaseAgent pattern."""
        yield Event(author=self.name, content=f"{self.name} starting processing")
        
        try:
            result = await self.process_business_logic(ctx)
            yield Event(author=self.name, content=result)
        except Exception as e:
            yield Event(author=self.name, content=f"Error in {self.name}: {str(e)}")
