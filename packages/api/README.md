# Teto API

FastAPI ベースの動画生成 API サーバー

## Development

```bash
cd packages/api
uvicorn teto_api.main:app --reload
```

## Endpoints

- `GET /` - API ルート
- `GET /health` - ヘルスチェック
