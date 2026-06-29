import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from jose import jwt

ALLOWED_ORIGIN = "https://dash-l24hb0.example.com"
EMAIL_ADDR = "24f2000961@ds.study.iitm.ac.in"  # ← PUT YOUR REAL EMAIL HERE

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-6x454egs.apps.exam.local"
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

app = FastAPI()

@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    origin = request.headers.get("origin", "")

    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            response = JSONResponse(content={}, status_code=200)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        else:
            response = JSONResponse(content={}, status_code=200)
        elapsed = time.perf_counter() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"
        return response

    response = await call_next(request)
    elapsed = time.perf_counter() - start
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    return response

@app.get("/stats")
async def stats(values: str):
    nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    n = len(nums)
    s = sum(nums)
    return {
        "email": EMAIL_ADDR,
        "count": n,
        "sum": s,
        "min": min(nums),
        "max": max(nums),
        "mean": s / n if n > 0 else 0.0,
    }

@app.post("/verify")
async def verify(request: Request):
    body = await request.json()
    token = body.get("token", "")
    try:
        claims = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
        return JSONResponse(status_code=200, content={
            "valid": True,
            "email": claims.get("email", ""),
            "sub": claims.get("sub", ""),
            "aud": claims.get("aud", ""),
        })
    except Exception:
        return JSONResponse(status_code=401, content={"valid": False})
