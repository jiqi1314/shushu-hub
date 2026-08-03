"""/api/systems — list available divination systems."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.modules import ModuleRegistry

router = APIRouter()


class SystemInfo(BaseModel):
    system_id: str
    system_name: str
    description: str


class SystemListResponse(BaseModel):
    systems: list[SystemInfo]


@router.get("/api/systems", response_model=SystemListResponse)
async def list_systems() -> SystemListResponse:
    return SystemListResponse(
        systems=[
            SystemInfo(
                system_id=m.system_id,
                system_name=m.system_name,
                description=m.description,
            )
            for m in ModuleRegistry.values()
        ]
    )
