import asyncio

import github_client


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.headers = {
            "Link": '<https://api.github.com/next>; rel="next"'
        }

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None

    async def get(self, *args, **kwargs):
        return FakeResponse({"result": "get"})

    async def post(self, *args, **kwargs):
        return FakeResponse({"result": "post"})

    async def patch(self, *args, **kwargs):
        return FakeResponse({"result": "patch"})


def test_github_client_methods(monkeypatch):
    monkeypatch.setattr(
        github_client.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    client = github_client.GitHubClient()

    issue = asyncio.run(client.get_issue(1))
    assert issue == {"result": "get"}

    created_issue = asyncio.run(
        client.create_issue(
            title="Test issue",
            body="Test body",
        )
    )
    assert created_issue == {"result": "post"}

    issues, headers = asyncio.run(
        client.list_issues(
            state="open",
            labels="bug",
            page=1,
            per_page=10,
        )
    )
    assert issues == {"result": "get"}
    assert "Link" in headers

    updated_issue = asyncio.run(
        client.update_issue(
            issue_number=1,
            title="Updated issue",
            body="Updated body",
            state="closed",
        )
    )
    assert updated_issue == {"result": "patch"}

    comments = asyncio.run(client.list_comments(1))
    assert comments == {"result": "get"}

    created_comment = asyncio.run(
        client.create_comment(
            issue_number=1,
            body="Test comment",
        )
    )
    assert created_comment == {"result": "post"}
