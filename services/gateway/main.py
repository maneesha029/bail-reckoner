from fastapi import FastAPI, Request
import httpx
from routing import resolve_target

app = FastAPI(title="Bail Reckoner API Gateway")


@app.api_route("/api/v1/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(full_path: str, request: Request):
    path = f"/api/v1/{full_path}"
    target = resolve_target(path)
    if not target:
        return {"success": False, "data": None,
                "error": {"code": "NOT_FOUND", "message": f"No route for {path}"}}
    body = await request.body()
    async with httpx.AsyncClient() as client:
        resp = await client.request(request.method, target, content=body,
                                     headers=dict(request.headers), timeout=15)
    return resp.json()
