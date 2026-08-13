from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from routing import resolve_target

app = FastAPI(title="Bail Reckoner API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/api/v1/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(full_path: str, request: Request):
    path = f"/api/v1/{full_path}"
    target = resolve_target(path)
    if not target:
        return {"success": False, "data": None,
                "error": {"code": "NOT_FOUND", "message": f"No route for {path}"}}
    body = await request.body()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(request.method, target, content=body,
                                         headers=dict(request.headers), timeout=15)
        return resp.json()
    except httpx.ConnectError:
        return {"success": False, "data": None,
                "error": {"code": "SERVICE_UNAVAILABLE",
                          "message": f"The service at {target} is not reachable right now."}}
    except httpx.TimeoutException:
        return {"success": False, "data": None,
                "error": {"code": "SERVICE_TIMEOUT",
                          "message": f"The service at {target} took too long to respond."}}