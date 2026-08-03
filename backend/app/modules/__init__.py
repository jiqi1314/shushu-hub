"""Divination module adapters."""

from .base import BaseModule, ModuleRegistry, get_module, register_module
from .ichingshifa import IchingShifaModule
from .liuren import LiuRenModule
from .qimen import QiMenModule

register_module(IchingShifaModule())
register_module(LiuRenModule())
register_module(QiMenModule())

__all__ = [
    "BaseModule",
    "ModuleRegistry",
    "get_module",
    "register_module",
    "IchingShifaModule",
    "LiuRenModule",
    "QiMenModule",
]
