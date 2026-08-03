"""Adapter base class and registry for divination systems."""

from abc import ABC, abstractmethod

from app.schemas.common import DivinationRequest, DivinationResult


class BaseModule(ABC):
    """Adapter interface that every divination system implements."""

    system_id: str
    system_name: str
    description: str = ""

    @abstractmethod
    def compute(self, request: DivinationRequest) -> DivinationResult:
        """Execute the divination and return a normalized result."""
        raise NotImplementedError

    def validate(self, request: DivinationRequest) -> None:
        """Hook for modules to reject incompatible requests.

        Should raise ``ValueError`` with a user-friendly message; the API
        layer maps this to a 422 with the appropriate ``ErrorCode``.
        """
        return None


ModuleRegistry: dict[str, BaseModule] = {}


def register_module(module: BaseModule) -> None:
    """Register a module instance under its ``system_id``."""
    ModuleRegistry[module.system_id] = module


def get_module(system_id: str) -> BaseModule | None:
    """Look up a registered module by its ``system_id``."""
    return ModuleRegistry.get(system_id)
