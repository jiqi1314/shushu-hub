"""/api/divination — execute a divination on a single system."""

from fastapi import APIRouter, HTTPException, status

from app.core import apply_true_solar_time
from app.modules import get_module
from app.schemas.common import DivinationRequest, DivinationResult
from app.schemas.errors import ErrorCode, ErrorResponse, fallback_message

router = APIRouter()


@router.post(
    "/api/divination",
    response_model=DivinationResult,
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def run_divination(request: DivinationRequest) -> DivinationResult:
    """Execute a divination across a single supported system."""
    module = get_module(request.system)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": ErrorCode.UNSUPPORTED_SYSTEM.value,
                "message": fallback_message(ErrorCode.UNSUPPORTED_SYSTEM),
                "details": {"system": request.system},
            },
        )

    if request.use_true_solar_time:
        if request.longitude is None or request.event_at is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": ErrorCode.MISSING_LOCATION.value,
                    "message": fallback_message(ErrorCode.MISSING_LOCATION),
                    "details": {"hint": "longitude required for true solar time"},
                },
            )
        request = request.model_copy(
            update={
                "event_at": apply_true_solar_time(
                    request.event_at, request.longitude
                )
            }
        )

    try:
        module.validate(request)
        return module.compute(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": ErrorCode.INVALID_DATETIME.value,
                "message": str(exc),
            },
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ErrorCode.SYSTEM_COMPUTATION_FAILED.value,
                "message": fallback_message(ErrorCode.SYSTEM_COMPUTATION_FAILED),
                "details": {"error": str(exc)},
            },
        ) from exc
