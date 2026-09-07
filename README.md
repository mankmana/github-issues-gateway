# GitHub Issues Gateway

A FastAPI service that sits between a client application and GitHub Issues. The service exposes a small REST API for managing issues and comments, receives GitHub webhook events, verifies webhook signatures, and stores received events in SQLite.

## Architecture

```text
Client → FastAPI → GitHub REST API
                 ↑
GitHub webhook → ngrok (development tunnel) → FastAPI → SQLite
```

## Features

- Health check endpoint
- List and retrieve GitHub issues
- Create, update, close, and reopen issues
- List and create issue comments
- GitHub webhook endpoint
- HMAC SHA-256 webhook signature verification
- SQLite storage for accepted webhook events
- Automatic interactive API documentation through FastAPI
- Unit tests with pytest
- Docker support
- OpenAPI specification export

## Repository

GitHub repository:

```text
https://github.com/mankmana/github-issues-gateway
```

## Requirements

- Python 3.10 or newer
- Git
- Docker (optional, for containerized execution)
- A GitHub fine-grained personal access token

The token must be restricted to this repository and have **Issues: Read and write** permission.

## Configuration

Create a file named `.env` in the project root:

```env
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=mankmana
GITHUB_REPO=github-issues-gateway
WEBHOOK_SECRET=your_webhook_secret
PORT=8000
```

Never commit `.env` or share its contents. The file is excluded through `.gitignore`.

## Local Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/mankmana/github-issues-gateway.git
cd github-issues-gateway
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If dependencies need to be refreshed during development:

```bash
pip freeze > requirements.txt
```

## Run the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The service runs at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Confirm that the service is running |
| GET | `/issues` | List repository issues |
| GET | `/issues/{issue_number}` | Retrieve one issue |
| POST | `/issues` | Create an issue |
| PATCH | `/issues/{issue_number}` | Update, close, or reopen an issue |
| GET | `/issues/{issue_number}/comments` | List comments for an issue |
| POST | `/issues/{issue_number}/comments` | Add a comment to an issue |
| POST | `/webhooks/github` | Receive and verify GitHub webhook events |
| GET | `/webhook-events` | View stored webhook events |

### Create an Issue

```json
{
  "title": "Example issue",
  "body": "Created through the GitHub Issues Gateway."
}
```

### Update or Close an Issue

```json
{
  "state": "closed"
}
```

Use `"state": "open"` to reopen an issue.

### Add a Comment

```json
{
  "body": "This comment was added through the gateway."
}
```

## Webhooks

GitHub cannot reach a service running only at `127.0.0.1`. During development, ngrok can provide a temporary public URL:

```bash
ngrok http 8000
```

Configure the GitHub webhook with:

```text
https://YOUR_NGROK_URL/webhooks/github
```

Use:

- Content type: `application/json`
- Secret: the same value as `WEBHOOK_SECRET`
- Event: `Issues`

The application calculates an HMAC SHA-256 signature from the raw request body and compares it with GitHub's `X-Hub-Signature-256` header. Requests with missing or invalid signatures are rejected.

Accepted events are stored in `events.db` in the `webhook_events` table.

## Testing

Run the automated tests from the project root:

```bash
python -m pytest
```

The tests cover the health endpoint and rejection of webhooks without a signature.

## OpenAPI

FastAPI serves the live OpenAPI document at:

```text
http://127.0.0.1:8000/openapi.json
```

The repository also includes the exported OpenAPI 3.1 YAML specification:

```text
openapi.yaml
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

For local SQLite persistence when using Docker, mount the database file:

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
├── main.py              # FastAPI application and routes
├── config.py            # Environment-based configuration
├── github_client.py     # GitHub REST API client
├── event_store.py       # SQLite event storage
├── events.db            # Local webhook event database
├── tests/
│   └── test_main.py     # Automated tests
├── Dockerfile
├── .dockerignore
├── .gitignore
├── openapi.yaml
├── requirements.txt
└── .env                 # Local secrets; never commit
```

## Security Notes

- Keep GitHub tokens and webhook secrets out of source control.
- Revoke any token that is accidentally exposed.
- Use a restricted fine-grained token rather than a broad personal token.
- Use HTTPS for public webhook delivery.
- The ngrok URL is temporary and intended for development only.

## Known Improvements

For a production-ready version, add pagination support, clearer GitHub rate-limit handling, persistent duplicate-event protection, structured logging, and broader unit and integration test coverage.
