import hashlib
import hmac
import json
from fastapi.responses import JSONResponse, Response
import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from config import settings
from event_store import get_events, save_event
from github_client import GitHubClient


app = FastAPI(title="GitHub Issues Gateway")
github_client = GitHubClient()


class IssueCreate(BaseModel):
    title: str
    body: str | None = None


class IssueUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    state: str | None = None


class CommentCreate(BaseModel):
    body: str


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/issues")
async def list_issues():
    try:
        return await github_client.list_issues()
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail="GitHub request failed",
        )


@app.get("/issues/{issue_number}")
async def get_issue(
    issue_number: int,
    if_none_match: str | None = Header(default=None),
):
    issue = await github_client.get_issue(issue_number)

    content = json.dumps(issue, sort_keys=True).encode()
    etag = f'"{hashlib.sha256(content).hexdigest()}"'

    if if_none_match == etag:
        return Response(
            status_code=304,
            headers={"ETag": etag},
        )

    return JSONResponse(
        content=issue,
        headers={"ETag": etag},
    )

@app.post("/issues")
async def create_issue(issue: IssueCreate):
    try:
        return await github_client.create_issue(
            title=issue.title,
            body=issue.body,
        )
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail="GitHub request failed",
        )


@app.patch("/issues/{issue_number}")
async def update_issue(issue_number: int, issue: IssueUpdate):
    try:
        return await github_client.update_issue(
            issue_number=issue_number,
            title=issue.title,
            body=issue.body,
            state=issue.state,
        )
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail="GitHub request failed",
        )


@app.get("/issues/{issue_number}/comments")
async def list_comments(issue_number: int):
    return await github_client.list_comments(issue_number)


@app.post("/issues/{issue_number}/comments")
async def create_comment(issue_number: int, comment: CommentCreate):
    return await github_client.create_comment(
        issue_number=issue_number,
        body=comment.body,
    )


@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
):
    payload = await request.body()

    if not x_hub_signature_256:
        raise HTTPException(
            status_code=401,
            detail="Missing GitHub signature",
        )

    expected_signature = (
        "sha256="
        + hmac.new(
            settings.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(
        expected_signature,
        x_hub_signature_256,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub signature",
        )

    event = await request.json()
    event_name = request.headers.get("X-GitHub-Event", "unknown")

    save_event(
        event_name=event_name,
        action=event.get("action"),
        payload=event,
    )

    return {
        "received": True,
        "event": event.get("action"),
    }


@app.get("/webhook-events")
def list_webhook_events():
    return get_events()
