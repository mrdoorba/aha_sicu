"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="Store ICU API", version="0.1.0")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy"}
