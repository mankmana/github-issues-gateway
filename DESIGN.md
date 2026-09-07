# Design Note

## Architecture

The service uses FastAPI as the REST API layer. It communicates with GitHub through the GitHub REST API using `httpx`. GitHub sends issue events back to the service through a webhook endpoint.

## Configuration

Secrets and repository settings are stored in a local `.env` file and loaded through `pydantic-settings`. The `.env` file is excluded from Git.

## Webhook Security

Each webhook request is verified using an HMAC SHA-256 signature. The signature is calculated using the shared webhook secret and compared with GitHub’s `X-Hub-Signature-256` header.

## Event Storage

Accepted webhook events are stored in a local SQLite database. This provides a lightweight way to review received events without requiring a separate database server.

## Testing

Pytest tests verify the health endpoint and confirm that unsigned webhook requests are rejected.

## Deployment

The application can run directly with Uvicorn or inside Docker. During local webhook development, ngrok provides a temporary public URL that forwards requests to the local service.
