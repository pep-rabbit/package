import asyncio
import json
import os
from typing import Any

import aiohttp
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Input, Static


class Client:
    def __init__(
        self,
        base_url: str,
        limit: int = 20,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._semaphore = asyncio.Semaphore(limit)
        self._limit = limit
        self.session: aiohttp.ClientSession | None = None

    def _build_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=self._limit,
                limit_per_host=200,
                use_dns_cache=True,
                ttl_dns_cache=300,
                keepalive_timeout=30.0,
                enable_cleanup_closed=True,
            ),
            timeout=aiohttp.ClientTimeout(
                total=12.0,
                connect=3.0,
                sock_connect=3.0,
                sock_read=8.0,
            ),
            auto_decompress=True,
            trust_env=False,
            raise_for_status=False,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "br, gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": "user-cli/0.1 aiohttp",
            },
        )

    def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = self._build_session()
        return self.session

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        async with self._semaphore:
            url = (
                path
                if path.startswith(("http://", "https://"))
                else f"{self.base_url}/{path.lstrip('/')}"
            )

            try:
                session = self._get_session()
                async with session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=payload,
                    headers=headers,
                ) as response:
                    raw = await response.text()
                    data: Any = json.loads(raw) if raw else {}

                    if isinstance(data, list):
                        return {"ok": 200 <= response.status < 300, "status": response.status, "items": data}
                    if isinstance(data, dict):
                        data.setdefault("ok", 200 <= response.status < 300)
                        data.setdefault("status", response.status)
                        return data

                    return {
                        "ok": 200 <= response.status < 300,
                        "status": response.status,
                        "items": [],
                    }
            except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as exc:
                return {"ok": False, "status": 0, "items": [], "error": str(exc)}

    async def close(self) -> None:
        if self.session is not None and not self.session.closed:
            await self.session.close()


class SearchApp(App):

    CSS = """
    #search-bar {
        height: 3;
        margin: 1 2;
        align: center top;
    }
    
    Input {
        width: 1fr;
        margin-right: 1;
    }
    
    Button {
        min-width: 15;
    }
    
    #results-container {
        margin: 1 2;
    }
    
    .card {
        border: solid $primary;
        padding: 1 2;
        margin-bottom: 1;
        background: $surface;
        border-title-color: $accent;
    }
    
    .placeholder {
        text-align: center;
        color: $text-muted;
        margin-top: 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.client = Client(base_url=os.getenv("API_BASE_URL", "http://127.0.0.1:80"))

    def compose(self) -> ComposeResult:
        with Horizontal(id="search-bar"):
            yield Input(placeholder="Введіть місто...", id="city-input")
            yield Input(placeholder="Процедура або препарат...", id="query-input")
            yield Button("Знайти", id="search-btn", variant="primary")

        with VerticalScroll(id="results-container"):
            yield Static(
                "Введіть дані для пошуку і натисніть «Знайти»", classes="placeholder"
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search-btn":
            city = self.query_one("#city-input", Input).value.strip()
            query = self.query_one("#query-input", Input).value.strip()
            results_container = self.query_one("#results-container", VerticalScroll)

            results_container.remove_children()

            if not city or not query:
                results_container.mount(
                    Static(
                        "Введіть і місто, і назву програми/препарата",
                        classes="placeholder",
                    )
                )
                return

            response = await self.client.request(
                "GET",
                "/api/top-pharmacies",
                params={"city": city, "medical_program": query},
            )

            items = response.get("items", [])
            if not response.get("ok", False):
                error_text = response.get("error", f"HTTP {response.get('status', 'unknown')}")
                results_container.mount(
                    Static(f"Помилка запиту: {error_text}", classes="placeholder")
                )
                return

            if not isinstance(items, list) or not items:
                results_container.mount(Static("Нічого не знайдено", classes="placeholder"))
                return

            for item in items:
                if not isinstance(item, dict):
                    continue
                card_content = (
                    f"[b]🏥 {item.get('legal_entity_name', 'Не вказано')}[/b]\n"
                    f"🏢 {item.get('division_name', 'Не вказано')}\n"
                    f"📍 {item.get('division_addresses', 'Не вказано')}\n"
                    f"📞 {item.get('division_phone', 'Не вказано')}\n"
                    f"🏷 {item.get('division_type', 'Не вказано')}\n"
                    f"🌍 {item.get('division_settlement', 'Не вказано')}\n"
                    f"⭐ activity_score: {item.get('activity_score', 0)}"
                )
                results_container.mount(Static(card_content, classes="card"))

    async def on_unmount(self) -> None:
        await self.client.close()


if __name__ == "__main__":
    asyncio.run(SearchApp().run_async())
