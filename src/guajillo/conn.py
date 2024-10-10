import json


from guajillo.exceptions import GuajilloException
from httpx import AsyncClient, URL, Headers, Cookies, Request


class Guajillo:
    def __init__(self, url: str = "https://salt:8000") -> None:
        self.url: URL = URL(url)
        if self.url.scheme not in ["http", "https"]:
            raise GuajilloException(
                f"Unknown URL Scheme {self.url.scheme} in url: {self.url}"
            )
        self.client: AsyncClient = AsyncClient()
        self.headers: Headers = Headers(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        self.cookies: Cookies = Cookies()

    async def login(self, username: str, password: str, auth: str = "pam"):
        url: URL = URL(f"{self.url}/login")
        params: dict[str, str] = {
            "username": username,
            "password": password,
            "eauth": auth,
        }
        request: Request = Request(
            "POST",
            url,
            headers=self.headers,
            cookies=self.cookies,
            data=json.dumps(params),
        )
        response = await self.client.send(request)
        if response.status_code == 200:
            self.cookies = response.cookies
        return response
