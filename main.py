import time
import uuid
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

ALLOWED_ORIGIN = "https://dash-l24hb0.example.com"
EMAIL = "24f2000961@ds.study.iitm.ac.in"  

app = FastAPI()


@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    # Handle CORS manually for strict per-origin enforcement
    origin = request.headers.get("origin", "")

    if request.method == "OPTIONS":
        # Preflight
        if origin == ALLOWED_ORIGIN:
            response = JSONResponse(content={}, status_code=200)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Max-Age"] = "600"
        else:
            # Reject: no ACAO header
            response = JSONResponse(content={}, status_code=200)
        elapsed = time.perf_counter() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"
        return response

    response = await call_next(request)
    elapsed = time.perf_counter() - start

    # Add ACAO only for allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = Query(...)):
    nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    n = len(nums)
    s = sum(nums)
    mn = min(nums)
    mx = max(nums)
    mean = s / n if n > 0 else 0.0

    return {
        "email": EMAIL,
        "count": n,
        "sum": s,
        "min": mn,
        "max": mx,
        "mean": mean,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
