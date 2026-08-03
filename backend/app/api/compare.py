"""/api/compare — run multiple systems in parallel and aggregate analysis."""

from fastapi import APIRouter, HTTPException, status

from app.core import (
    apply_true_solar_time,
    build_cross_analysis,
)
from app.modules import ModuleRegistry, get_module
from app.schemas.common import (
    CompareRequest,
    CompareResponse,
    DivinationRequest,
    SystemFailure,
)
from app.schemas.errors import ErrorCode, fallback_message

router = APIRouter()


@router.post(
    "/api/compare",
    response_model=CompareResponse,
    responses={
        422: {"model": dict},
    },
)
async def compare_systems(request: CompareRequest) -> CompareResponse:
    """Run several systems on the same input and return aggregated analysis.

    The endpoint resolves the list of systems to invoke (either explicit or
    all registered), constructs a per-system ``DivinationRequest`` from the
    shared input, and collects results. Each failure is recorded but does
    not abort the whole call — the frontend can still render the
    successful subset.
    """
    systems_to_run = list(request.systems) if request.systems else list(
        ModuleRegistry.keys()
    )

    if not systems_to_run:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": ErrorCode.UNSUPPORTED_SYSTEM.value,
                "message": "No systems available to compare.",
            },
        )

    results = []
    failures: list[SystemFailure] = []

    for sys_id in systems_to_run:
        module = get_module(sys_id)
        if module is None:
            failures.append(
                SystemFailure(
                    system=sys_id,
                    error_code=ErrorCode.UNSUPPORTED_SYSTEM.value,
                    message=fallback_message(ErrorCode.UNSUPPORTED_SYSTEM),
                )
            )
            continue

        per_system_details = request.per_system.get(sys_id, {})
        div_req = DivinationRequest(
            system=sys_id,
            method=request.method,
            event_at=request.event_at,
            timezone=request.timezone,
            manual_lines=request.manual_lines,
            question=request.question,
            gender=request.gender,
            latitude=request.latitude,
            longitude=request.longitude,
            use_true_solar_time=request.use_true_solar_time,
            locale=request.locale,
            details=per_system_details,
        )

        if div_req.use_true_solar_time:
            if div_req.longitude is None or div_req.event_at is None:
                failures.append(
                    SystemFailure(
                        system=sys_id,
                        error_code=ErrorCode.MISSING_LOCATION.value,
                        message=fallback_message(ErrorCode.MISSING_LOCATION),
                    )
                )
                continue
            div_req = div_req.model_copy(
                update={
                    "event_at": apply_true_solar_time(
                        div_req.event_at, div_req.longitude
                    )
                }
            )

        try:
            module.validate(div_req)
            result = module.compute(div_req)
            results.append(result)
        except ValueError as exc:
            failures.append(
                SystemFailure(
                    system=sys_id,
                    error_code=ErrorCode.INVALID_DATETIME.value,
                    message=str(exc),
                )
            )
        except Exception:  # pragma: no cover - defensive
            failures.append(
                SystemFailure(
                    system=sys_id,
                    error_code=ErrorCode.SYSTEM_COMPUTATION_FAILED.value,
                    message=fallback_message(ErrorCode.SYSTEM_COMPUTATION_FAILED),
                )
            )

    cross_analysis = build_cross_analysis(results) if results else {}

    return CompareResponse(
        results=results,
        cross_analysis=cross_analysis,
        failures=failures,
        question=request.question,
    )
