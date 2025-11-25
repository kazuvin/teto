from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Teto API",
    description="API for video generation system",
    version="0.1.0",
)

# CORS設定（開発時はデスクトップアプリからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Teto API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
