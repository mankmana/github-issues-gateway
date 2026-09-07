# Author: Manali Mankad
# GitHub Issues Gateway service implementation

# GitHub Issues Gateway

A FastAPI service that wraps the GitHub Issues REST API for one repository. It supports issue management, comments, secure webhooks, SQLite event storage, Docker, OpenAPI documentation, automated tests, and ETag caching.

## Architecture

```text
Client → FastAPI → GitHub REST API
                 ↑
GitHub webhook → ngrok → FastAPI → SQLite
```

## Features

- Health check endpoint
- List, retrieve, create, update, close, and reopen issues
- List and create issue comments
- Secure GitHub webhooks using HMAC SHA-256
- Support for `issues`, `issue_comment`, and `ping` events
- Duplicate webhook protection using GitHub delivery IDs
- SQLite storage for webhook events
- Pagination and rate-limit handling
- ETag caching for issue responses
- OpenAPI documentation
- Automated unit and mocked client tests
- GitHub Actions CI
- Docker support

## Repository

```text
https://github.com/mankmana/github-issues-gateway
```

## Requirements

- Python 3.10 or newer
- Git
- Docker, optional
- GitHub fine-grained personal access token
- ngrok, for local webhook testing

The GitHub token should be restricted to this repository with:

- Issues: Read and write
- Metadata: Read-only

## Configuration

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=mankmana
GITHUB_REPO=github-issues-gateway
WEBHOOK_SECRET=your_webhook_secret
PORT=8000
```

Never commit or share `.env`. It is excluded through `.gitignore`.

## Local Setup

Clone the repository:

```bash
git clone https://github.com/mankmana/github-issues-gateway.git
cd github-issues-gateway
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the Application

Start FastAPI:

```bash
uvicorn main:app --reload --port 8000
```

The service runs at:

```text
http://127.0.0.1:8000
```

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected response:

```json
{"status":"ok"}
```

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Check service status |
| GET | `/issues` | List repository issues |
| GET | `/issues/{issue_number}` | Retrieve one issue |
| POST | `/issues` | Create an issue |
| PATCH | `/issues/{issue_number}` | Update, close, or reopen an issue |
| GET | `/issues/{issue_number}/comments` | List comments |
| POST | `/issues/{issue_number}/comments` | Create a comment |
| POST | `/webhook` | Receive GitHub webhooks |
| POST | `/webhooks/github` | Backward-compatible webhook route |
| GET | `/webhook-events` | View stored webhook events |

## Issue Examples

### List Issues

```bash
curl -i \
  "http://127.0.0.1:8000/issues?state=open&page=1&per_page=30"
```

Supported query parameters:

- `state`: `open`, `closed`, or `all`
- `labels`: comma-separated labels
- `page`: page number
- `per_page`: number of results from 1 to 100

GitHub pagination information is forwarded through the `Link` response header.

### Get an Issue

```bash
curl -i http://127.0.0.1:8000/issues/1
```

The response includes an `ETag` header. To check whether the issue changed:

```bash
curl -i \
  -H 'If-None-Match: "PASTE_ETAG_HERE"' \
  http://127.0.0.1:8000/issues/1
```

If the issue has not changed, the service returns:

```text
HTTP/1.1 304 Not Modified
```

### Create an Issue

```bash
curl -i -X POST http://127.0.0.1:8000/issues \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example issue",
    "body": "Created through the GitHub Issues Gateway."
  }'
```

A successful request returns `201 Created` and a `Location` header.

### Update or Close an Issue

```bash
curl -i -X PATCH http://127.0.0.1:8000/issues/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated issue",
    "body": "Updated issue description",
    "state": "closed"
  }'
```

Use `"state": "open"` to reopen an issue.

### List Comments

```bash
curl -i http://127.0.0.1:8000/issues/1/comments
```

### Create a Comment

```bash
curl -i -X POST http://127.0.0.1:8000/issues/1/comments \
  -H "Content-Type: application/json" \
  -d '{
    "body": "This comment was added through the gateway."
  }'
```

A successful request returns `201 Created`.

## Webhooks

GitHub cannot reach a service running only at `127.0.0.1`. Start ngrok:

```bash
ngrok http 8000
```

Configure the GitHub webhook using:

```text
https://YOUR_NGROK_URL/webhook
```

The existing `/webhooks/github` path is also supported.

Use these webhook settings:

- Content type: `application/json`
- Secret: the same value as `WEBHOOK_SECRET`
- Events: Issues and Issue comments

Supported events:

- `issues`
- `issue_comment`
- `ping`

The service:

1. Reads the raw request body.
2. Calculates an HMAC SHA-256 signature.
3. Compares it with `X-Hub-Signature-256`.
4. Reads GitHub’s `X-GitHub-Delivery` ID.
5. Stores the event in SQLite.
6. Ignores repeated delivery IDs.
7. Returns `204 No Content`.

Invalid signatures return `401 Unauthorized`.

View stored events:

```bash
curl -i http://127.0.0.1:8000/webhook-events
```

## Pagination and Rate Limits

The issue-list endpoint supports page and page-size parameters:

```bash
curl -i \
  "http://127.0.0.1:8000/issues?page=1&per_page=2"
```

The `per_page` value must be between 1 and 100.

If GitHub reports that its rate limit has been exhausted, the service returns `429 Too Many Requests`.

## Testing

Run all tests from the project root:

```bash
python -m pytest
```

Run coverage:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

The test suite covers:

- Health checks
- Webhook signature validation
- Invalid webhook signatures
- Unsupported webhook events
- `issue_comment` events
- Pagination validation
- SQLite event storage
- Duplicate delivery protection
- Mocked GitHub client methods

Latest local result:

```text
10 passed
86% coverage
```

## OpenAPI

FastAPI serves the live OpenAPI document at:

```text
http://127.0.0.1:8000/openapi.json
```

The repository also includes:

```text
openapi.yaml
```

## GitHub Actions

GitHub Actions automatically runs the tests when code is pushed to `main` or a pull request is opened.

The workflow:

1. Checks out the repository.
2. Installs Python.
3. Installs dependencies.
4. Runs pytest.

Workflow file:

```text
.github/workflows/tests.yml
```

## Docker

Build the image:

```bash
sudo docker build -t github-issues-gateway .
```

Run the container:

```bash
sudo docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  github-issues-gateway
```

For local SQLite persistence, mount the database file:

```bash
sudo docker run --rm \
  --name github-issues-gateway-container \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/events.db:/app/events.db" \
  github-issues-gateway
```

## Project Structure

```text
.
├── main.py
├── config.py
├── github_client.py
├── event_store.py
├── events.db
├── tests/
│   ├── test_main.py
│   ├── test_event_store.py
│   └── test_github_client.py
├── Dockerfile
├── .dockerignore
├── .gitignore
├── openapi.yaml
├── DESIGN.md
├── requirements.txt
├── README.md
└── .env
```

The `.env` file and local database should not be committed if they contain private data.

## Security Notes

- Never commit GitHub tokens or webhook secrets.
- Revoke tokens that are accidentally exposed.
- Use fine-grained tokens with minimum permissions.
- Use HTTPS for public webhook delivery.
- Do not log secrets or raw webhook signatures.
- The ngrok URL is temporary and intended for development only.

## Design Note

Additional design decisions are documented in:

```text
DESIGN.md
```

