"""HTMX API endpoints for the dashboard."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import get_region, get_all_regions
from app.database import (
    test_connection,
    measure_latency,
    load_test,
    get_health_metrics,
    test_all_regions,
    save_connection_check,
    save_latency_check,
    save_load_test_check,
    save_health_metrics_check,
    get_recent_connection_checks,
    get_connection_check_summary,
    get_all_recent_checks,
)
from app.chat import get_chat_response, chat_with_ollama, get_system_prompt
from app.feature_flags import (
    is_region_enabled,
    is_health_checks_enabled,
    is_load_testing_enabled,
    is_test_all_regions_enabled,
    get_enabled_regions,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_user_key(request: Request) -> str:
    """Extract user key from request."""
    user_key = request.cookies.get("user_key")
    if not user_key:
        user_key = request.client.host if request.client else "anonymous"
    return user_key


@router.post("/regions/{region_id}/test")
async def test_region(region_id: str, request: Request):
    """Test connection to a specific region."""
    user_key = get_user_key(request)

    # Check if region is enabled
    if not is_region_enabled(region_id, user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Region unavailable"},
        )

    region = get_region(region_id)
    if not region:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": f"Unknown region: {region_id}"},
        )

    result = await test_connection(region_id)

    # Save the check result to database
    await save_connection_check(region_id, result, user_key)

    response = templates.TemplateResponse(
        "partials/connection_result.html",
        {"request": request, "region": region, "result": result},
    )

    # Add test result data as a custom header for the map visualization
    import json
    response.headers["X-Test-Result"] = json.dumps({
        "region_id": region_id,
        "test_type": "test",
        "success": result.get("success", False),
        "latency_ms": result.get("latency_ms"),
        "error": result.get("error")
    })

    return response


@router.post("/regions/{region_id}/latency")
async def test_latency(region_id: str, request: Request, iterations: int = 5):
    """Measure latency to a specific region."""
    import json
    user_key = get_user_key(request)

    if not is_region_enabled(region_id, user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Region unavailable"},
        )

    region = get_region(region_id)
    if not region:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": f"Unknown region: {region_id}"},
        )

    result = await measure_latency(region_id, iterations)

    # Save the check result to database
    await save_latency_check(region_id, result, user_key)

    response = templates.TemplateResponse(
        "partials/latency_result.html",
        {"request": request, "region": region, "result": result},
    )

    # Add test result data as a custom header for the map visualization
    response.headers["X-Test-Result"] = json.dumps({
        "region_id": region_id,
        "test_type": "latency",
        "success": result.get("success", False),
        "avg_latency_ms": result.get("avg_latency_ms"),
        "min_latency_ms": result.get("min_latency_ms"),
        "max_latency_ms": result.get("max_latency_ms"),
        "error": result.get("error")
    })

    return response


@router.post("/regions/{region_id}/load-test")
async def run_load_test(region_id: str, request: Request, concurrent: int = 10):
    """Run load test on a specific region."""
    import json
    user_key = get_user_key(request)

    if not is_load_testing_enabled(user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Load testing is disabled"},
        )

    if not is_region_enabled(region_id, user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Region unavailable"},
        )

    region = get_region(region_id)
    if not region:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": f"Unknown region: {region_id}"},
        )

    result = await load_test(region_id, concurrent)

    # Save the check result to database
    await save_load_test_check(region_id, result, user_key)

    response = templates.TemplateResponse(
        "partials/load_test_result.html",
        {"request": request, "region": region, "result": result},
    )

    # Add test result data as a custom header for the map visualization
    response.headers["X-Test-Result"] = json.dumps({
        "region_id": region_id,
        "test_type": "load-test",
        "success": result.get("success", False),
        "connections": result.get("successful_connections"),
        "avg_latency_ms": result.get("avg_latency_ms"),
        "error": result.get("error")
    })

    return response


@router.post("/regions/{region_id}/health")
async def get_region_health(region_id: str, request: Request):
    """Get health metrics for a specific region."""
    import json
    user_key = get_user_key(request)

    if not is_health_checks_enabled(user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Health checks are disabled"},
        )

    if not is_region_enabled(region_id, user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Region unavailable"},
        )

    region = get_region(region_id)
    if not region:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": f"Unknown region: {region_id}"},
        )

    result = await get_health_metrics(region_id)

    # Save the check result to database
    await save_health_metrics_check(region_id, result, user_key)

    response = templates.TemplateResponse(
        "partials/health_result.html",
        {"request": request, "region": region, "result": result},
    )

    # Add test result data as a custom header for the map visualization
    response.headers["X-Test-Result"] = json.dumps({
        "region_id": region_id,
        "test_type": "health",
        "success": result.get("success", False),
        "connections": result.get("active_connections"),
        "error": result.get("error")
    })

    return response


@router.post("/regions/test-all")
async def test_all(request: Request):
    """Test all enabled regions simultaneously."""
    user_key = get_user_key(request)

    if not is_test_all_regions_enabled(user_key):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "Test all regions is disabled"},
        )

    enabled_regions = get_enabled_regions(user_key)

    if not enabled_regions:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": "No regions available"},
        )

    result = await test_all_regions(enabled_regions)

    # Enrich results with region info
    all_regions = {r.id: r for r in get_all_regions()}
    for r in result["results"]:
        r["region"] = all_regions.get(r["region_id"])

    return templates.TemplateResponse(
        "partials/all_regions_result.html",
        {"request": request, "results": result["results"]},
    )


@router.get("/regions/summary")
async def regions_summary(request: Request):
    """Get summary of all regions (for auto-refresh)."""
    user_key = get_user_key(request)
    enabled_regions = get_enabled_regions(user_key)

    if not enabled_regions:
        return HTMLResponse("<div class='text-muted'>No regions available</div>")

    result = await test_all_regions(enabled_regions)

    all_regions = {r.id: r for r in get_all_regions()}
    for r in result["results"]:
        r["region"] = all_regions.get(r["region_id"])

    return templates.TemplateResponse(
        "partials/regions_summary.html",
        {"request": request, "results": result["results"]},
    )


@router.get("/regions/locations")
async def get_region_locations(request: Request):
    """Get region location data for map display."""
    user_key = get_user_key(request)
    enabled_region_ids = get_enabled_regions(user_key)

    all_regions = get_all_regions()
    enabled_regions = [r for r in all_regions if r.id in enabled_region_ids]

    locations = [
        {
            "id": region.id,
            "name": region.name,
            "latitude": region.latitude,
            "longitude": region.longitude,
        }
        for region in enabled_regions
    ]

    return JSONResponse(content={"regions": locations})


@router.get("/checks/history")
async def get_check_history(request: Request, limit: int = 20):
    """Get recent check history across all regions."""
    user_key = get_user_key(request)
    enabled_region_ids = get_enabled_regions(user_key)

    if not enabled_region_ids:
        return templates.TemplateResponse(
            "partials/check_history.html",
            {"request": request, "checks": []},
        )

    checks = await get_all_recent_checks(enabled_region_ids, limit)

    # Enrich checks with region info
    all_regions = {r.id: r for r in get_all_regions()}
    for check in checks:
        check["region"] = all_regions.get(check["region_id"])

    return templates.TemplateResponse(
        "partials/check_history.html",
        {"request": request, "checks": checks},
    )


@router.get("/checks/chart-data")
async def get_check_chart_data(request: Request):
    """Get check data formatted for charts, grouped by check type."""
    user_key = get_user_key(request)
    enabled_region_ids = get_enabled_regions(user_key)

    if not enabled_region_ids:
        return JSONResponse(content={
            "connection": {"datasets": []},
            "latency": {"datasets": []},
            "load_test": {"datasets": []},
            "health": {"datasets": []}
        })

    # Get recent checks
    checks = await get_all_recent_checks(enabled_region_ids, limit=100)

    # Group by region and check type
    from collections import defaultdict
    region_data = defaultdict(lambda: defaultdict(list))

    for check in checks:
        region_id = check["region_id"]
        check_type = check["check_type"]

        if check["success"] and check["metric_value"]:
            region_data[region_id][check_type].append({
                "timestamp": check["checked_at"].isoformat(),
                "value": float(check["metric_value"])
            })

    # Prepare data for Chart.js
    all_regions = {r.id: r for r in get_all_regions()}

    colors = {
        "us-east": "rgb(255, 53, 84)",      # Aiven red
        "eu-west": "rgb(64, 91, 255)",       # LaunchDarkly purple
        "asia-pacific": "rgb(40, 167, 69)"   # Green
    }

    # Create separate datasets for each check type
    result = {
        "connection": {"datasets": []},
        "latency": {"datasets": []},
        "load_test": {"datasets": []},
        "health": {"datasets": []}
    }

    for region_id in enabled_region_ids:
        region = all_regions.get(region_id)
        if not region:
            continue

        base_color = colors.get(region_id, "rgb(128, 128, 128)")
        bg_color = base_color.replace("rgb", "rgba").replace(")", ", 0.1)")

        # Connection data
        connection_data = region_data[region_id].get("connection", [])
        if connection_data:
            connection_data.sort(key=lambda x: x["timestamp"])
            result["connection"]["datasets"].append({
                "label": region.name,
                "data": [{"x": d["timestamp"], "y": d["value"]} for d in connection_data[-30:]],
                "borderColor": base_color,
                "backgroundColor": bg_color,
                "tension": 0.4,
                "fill": True
            })

        # Latency data
        latency_data = region_data[region_id].get("latency", [])
        if latency_data:
            latency_data.sort(key=lambda x: x["timestamp"])
            result["latency"]["datasets"].append({
                "label": region.name,
                "data": [{"x": d["timestamp"], "y": d["value"]} for d in latency_data[-30:]],
                "borderColor": base_color,
                "backgroundColor": bg_color,
                "tension": 0.4,
                "fill": True
            })

        # Load test data (queries per second)
        load_test_data = region_data[region_id].get("load_test", [])
        if load_test_data:
            load_test_data.sort(key=lambda x: x["timestamp"])
            result["load_test"]["datasets"].append({
                "label": region.name,
                "data": [{"x": d["timestamp"], "y": d["value"]} for d in load_test_data[-30:]],
                "borderColor": base_color,
                "backgroundColor": bg_color,
                "tension": 0.4,
                "fill": True
            })

        # Health data (cache hit ratio)
        health_data = region_data[region_id].get("health", [])
        if health_data:
            health_data.sort(key=lambda x: x["timestamp"])
            result["health"]["datasets"].append({
                "label": region.name,
                "data": [{"x": d["timestamp"], "y": d["value"]} for d in health_data[-30:]],
                "borderColor": base_color,
                "backgroundColor": bg_color,
                "tension": 0.4,
                "fill": True
            })

    return JSONResponse(content=result)


@router.post("/chat")
async def chat(request: Request):
    """Chat with AI assistant about database performance."""
    from fastapi.responses import StreamingResponse

    user_key = get_user_key(request)
    enabled_region_ids = get_enabled_regions(user_key)

    # Get the message from request body
    body = await request.json()
    message = body.get("message", "")

    if not message:
        return JSONResponse(content={"error": "No message provided"}, status_code=400)

    # Get recent checks for context
    recent_checks = []
    if enabled_region_ids:
        recent_checks = await get_all_recent_checks(enabled_region_ids, limit=10)

    # Get response from Ollama
    try:
        response = await get_chat_response(message, recent_checks)
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(
            content={"error": f"Chat service error: {str(e)}"},
            status_code=500
        )
