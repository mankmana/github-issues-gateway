import httpx


from config import settings



class GitHubClient:
    def __init__(self):
        self.base_url = (
            f"https://api.github.com/repos/"
            f"{settings.github_owner}/{settings.github_repo}"
        )
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_issue(self, issue_number: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def create_issue(self, title: str, body: str | None = None):
        payload = {"title": title}

        if body:
            payload["body"] = body

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/issues",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

   
    async def list_issues(self,state: str = "open",labels: str | None = None,page: int = 1,per_page: int = 30,):
    	params = {
        	"state": state,
        	"page": page,
        	"per_page": per_page,
    	}

    	if labels:
        	params["labels"] = labels

    	async with httpx.AsyncClient() as client:
        	response = await client.get(
            	f"{self.base_url}/issues",
            	headers=self.headers,
            	params=params,
        	)

        	response.raise_for_status()

        	return response.json(), response.headers


 
    async def update_issue(
        self,
        issue_number: int,
        title: str | None = None,
        body: str | None = None,
        state: str | None = None,
    ):
        payload = {}

        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if state is not None:
            payload["state"] = state

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def list_comments(self, issue_number: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues/{issue_number}/comments",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def create_comment(self, issue_number: int, body: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/issues/{issue_number}/comments",
                headers=self.headers,
                json={"body": body},
            )
            response.raise_for_status()
            return response.json()
