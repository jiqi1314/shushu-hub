"""Divination module adapters."""

from .base import BaseModule, ModuleRegistry, get_module, register_module
from .ichingshifa import IchingShifaModule
from .liuren import LiuRenModule
from .qimen import QiMenModule
from .taiyi import TaiYiModule

register_module(IchingShifaModule())
register_module(LiuRenModule())
register_module(QiMenModule())
register_module(TaiYiModule())

__all__ = [
    "BaseModule",
    "ModuleRegistry",
    "get_module",
    "register_module",
    "IchingShifaModule",
    "LiuRenModule",
    "QiMenModule",
    "TaiYiModule",
]
