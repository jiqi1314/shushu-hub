"""Divination module adapters."""

from .base import BaseModule, ModuleRegistry, get_module, register_module
from .ichingshifa import IchingShifaModule

register_module(IchingShifaModule())

__all__ = [
    "BaseModule",
    "ModuleRegistry",
    "get_module",
    "register_module",
    "IchingShifaModule",
]
