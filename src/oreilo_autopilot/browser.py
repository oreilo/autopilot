from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from .models import Action, Observation
from .security import validate_url, PolicyError
from .extraction import extract_html

class Browser:
    def __init__(self, allowed_domains: tuple[str, ...], headed: bool = False, artifact_dir: str = "artifacts"):
        self.allowed_domains = allowed_domains
        self.headed = headed
        self.artifact_dir = Path(artifact_dir)
        self._pw = self._browser = self.context = self.page = None
        self.pages = []

    async def __aenter__(self):
        self._pw = await async_playwright().start()
        try:
            self._browser = await self._pw.chromium.launch(headless=not self.headed)
            self.context = await self._browser.new_context(accept_downloads=False, service_workers="block")
            self.page = await self.context.new_page()
            self.pages = [self.page]
            self.context.on("page", lambda page: self.pages.append(page))
            async def guard(route):
                request = route.request
                if request.resource_type in ("websocket", "eventsource"):
                    await route.abort(); return
                try:
                    validate_url(request.url, self.allowed_domains)
                except PolicyError:
                    await route.abort(); return
                await route.continue_()
            await self.context.route("**/*", guard)
            return self
        except Exception:
            await self.__aexit__(None,None,None)
            raise

    async def __aexit__(self, *args):
        if self.context: await self.context.close()
        if self._browser: await self._browser.close()
        if self._pw: await self._pw.stop()

    async def observe(self, step: int) -> Observation:
        page = self.page
        text = (await page.locator("body").inner_text(timeout=10000))[:10000] if await page.locator("body").count() else ""
        elements = await page.locator("a, button, input, textarea, select").evaluate_all("""els => els.slice(0, 80).map((e, i) => ({index:i,tag:e.tagName.toLowerCase(),text:(e.innerText||e.getAttribute('aria-label')||'').slice(0,100),name:e.getAttribute('name'),placeholder:e.getAttribute('placeholder'),href:e.getAttribute('href'),type:e.getAttribute('type')}))""")
        return Observation(url=page.url, title=await page.title(), text=text, elements=elements, step=step)

    async def execute(self, action: Action, step: int) -> str:
        page = self.page
        if action.kind == "navigate":
            if not action.url: raise ValueError("navigate requires url")
            validate_url(action.url, self.allowed_domains)
            await page.goto(action.url, wait_until="domcontentloaded", timeout=30000)
            validate_url(page.url, self.allowed_domains)
            return "Navigated"
        if action.kind in ("click", "fill", "press", "select"):
            if not action.selector: raise ValueError("Action requires selector")
            locator = page.locator(action.selector).first
            if action.kind == "click": await locator.click(timeout=10000)
            elif action.kind == "fill": await locator.fill(action.value or "", timeout=10000)
            elif action.kind == "press": await locator.press(action.value or "Enter", timeout=10000)
            elif action.kind == "select": await locator.select_option(action.value or "", timeout=10000)
            validate_url(page.url, self.allowed_domains)
            return "Action completed"
        if action.kind == "wait":
            await page.wait_for_timeout(min(int(action.value or "500"), 10000))
            return "Waited"
        if action.kind == "back":
            await page.go_back(wait_until="domcontentloaded")
            validate_url(page.url, self.allowed_domains)
            return "Went back"
        if action.kind == "tab_new":
            if not action.url: raise ValueError("tab_new requires url")
            validate_url(action.url, self.allowed_domains)
            self.page = await self.context.new_page()
            await self.page.goto(action.url,wait_until="domcontentloaded",timeout=30000)
            validate_url(self.page.url, self.allowed_domains)
            return "Opened tab"
        if action.kind == "tab_switch":
            index=int(action.value or "0")
            active=[p for p in self.pages if not p.is_closed()]
            if index<0 or index>=len(active): raise ValueError("Tab index out of range")
            self.page=active[index]
            return "Switched tab"
        if action.kind == "extract_structured":
            data=extract_html(await page.content(),page.url)
            import json
            return json.dumps(data,ensure_ascii=False)[:30000]
        if action.kind == "scroll":
            await page.mouse.wheel(0, int(action.value or "600"))
            return "Scrolled"
        if action.kind == "extract":
            return (await page.locator(action.selector or "body").first.inner_text(timeout=10000))[:15000]
        if action.kind == "screenshot":
            self.artifact_dir.mkdir(parents=True, exist_ok=True)
            target = self.artifact_dir / f"step-{step:03d}.png"
            await page.screenshot(path=str(target), full_page=True)
            return str(target)
        if action.kind == "finish": return action.answer or "Completed"
        raise ValueError("Unsupported action")
