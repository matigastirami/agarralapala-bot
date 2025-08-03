from abc import ABC, abstractmethod


class Agent(ABC):
    """Abstract interface for AI agents"""
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the agent"""
        pass

    @abstractmethod
    def exec(self, **kwargs):
        """Main entrypoint for executing the agent"""
        pass

