## Architecture

The service uses FastAPI as the REST API layer. It communicates with GitHub through the GitHub REST API using `httpx`. GitHub sends issue and comment events back to the service through webhook endpoints.

## Configuration and Security

Repository settings and secrets are stored in a local `.env` file and loaded through `pydantic-settings`. The `.env` file is excluded from Git.

Webhook requests are verified using HMAC SHA-256. The calculated signature is compared with GitHub’s `X-Hub-Signature-256` header using a constant-time comparison.

## Error Mapping

GitHub HTTP errors are converted into appropriate API responses. Invalid webhook signatures return `401`, invalid event types or request parameters return `400`, missing GitHub resources return `404`, and rate-limit responses return `429`.

## Pagination and Rate Limits

The issue-list endpoint supports `state`, `labels`, `page`, and `per_page` parameters. The `per_page` value is limited to a maximum of 100. GitHub pagination information is forwarded through the response `Link` header. When GitHub reports that its rate limit has been exhausted, the service returns `429`.

## Webhook Processing and Deduplication

Accepted `issues`, `issue_comment`, and `ping` events are validated and stored in SQLite. Each event uses GitHub’s delivery ID as a unique key. If GitHub retries the same delivery, the database ignores the duplicate.

## Event Storage

Webhook events are stored in a local SQLite database. This provides a lightweight way to review received events without requiring a separate database server.

## Testing

The project uses pytest. Tests cover health checks, webhook signature validation, unsupported events, issue-comment events, pagination validation, event storage, duplicate delivery handling, and mocked GitHub client methods.

The final test suite passed 10 tests with 86% line coverage.

## Deployment

The application can run directly with Uvicorn or inside Docker. During local webhook development, ngrok provides a temporary public URL that forwards requests to the local service.
