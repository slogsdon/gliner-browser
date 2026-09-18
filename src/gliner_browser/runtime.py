from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright


OBSERVE_SCRIPT = r"""
() => {
  const selector = [
    'a[href]', 'button', 'input', 'textarea', 'select', 'summary',
    '[role]', '[contenteditable="true"]', '[tabindex]:not([tabindex="-1"])'
  ].join(',');
  const roleFor = (element) => element.getAttribute('role') || ({
    A: 'link', BUTTON: 'button', INPUT: element.type || 'textbox',
    TEXTAREA: 'textbox', SELECT: 'combobox', SUMMARY: 'button'
  }[element.tagName] || element.tagName.toLowerCase());
  const nameFor = (element) => (
    element.getAttribute('aria-label') || element.getAttribute('title') ||
    element.getAttribute('placeholder') || element.getAttribute('alt') ||
    element.innerText || element.value || element.name || ''
  ).replace(/\s+/g, ' ').trim().slice(0, 300);

  return [...document.querySelectorAll(selector)].flatMap((element, index) => {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    if (!rect.width || !rect.height || style.visibility === 'hidden' ||
        style.display === 'none' || element.disabled) return [];
    const id = `e${index + 1}`;
    element.setAttribute('data-gliner-browser-id', id);
    return [{
      id,
      role: roleFor(element),
      name: nameFor(element),
      tag: element.tagName.toLowerCase(),
      type: element.getAttribute('type') || '',
      href: element.href || ''
    }];
  });
}
"""


class BrowserRuntime:
    def __init__(self, profile_dir: Path, *, headless: bool = False) -> None:
        profile_dir.mkdir(parents=True, exist_ok=True)
        self._playwright: Playwright = sync_playwright().start()
        self._context: BrowserContext = self._playwright.chromium.launch_persistent_context(
            profile_dir,
            headless=headless,
            viewport={"width": 1440, "height": 1000},
        )
        self._page = self._context.pages[-1] if self._context.pages else self._context.new_page()

    @property
    def page(self) -> Page:
        if self._page.is_closed():
            self._page = self._context.pages[-1] if self._context.pages else self._context.new_page()
        return self._page

    def open(self, url: str) -> dict[str, Any]:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL must use http or https and include a host")
        response = self.page.goto(url, wait_until="domcontentloaded")
        return {
            "url": self.page.url,
            "title": self.page.title(),
            "status": response.status if response else None,
        }

    def observe(self, limit: int = 100) -> dict[str, Any]:
        elements = self.page.evaluate(OBSERVE_SCRIPT)
        return {
            "url": self.page.url,
            "title": self.page.title(),
            "elements": elements[:limit],
            "total": len(elements),
        }

    def _element(self, element_id: str):
        normalized = element_id.removeprefix("@").strip()
        locator = self.page.locator(f'[data-gliner-browser-id="{normalized}"]')
        if locator.count() != 1:
            raise LookupError(
                f"Element {element_id!r} is missing or stale; run observe again"
            )
        return locator

    def click(self, element_id: str) -> dict[str, Any]:
        self._element(element_id).click()
        return {"element_id": element_id.removeprefix("@"), "url": self.page.url}

    def fill(self, element_id: str, text: str) -> dict[str, Any]:
        self._element(element_id).fill(text)
        return {"element_id": element_id.removeprefix("@"), "filled": True}

    def select(self, element_id: str, value: str) -> dict[str, Any]:
        selected = self._element(element_id).select_option(value)
        return {"element_id": element_id.removeprefix("@"), "selected": selected}

    def press(self, key: str) -> dict[str, Any]:
        self.page.keyboard.press(key)
        return {"key": key, "url": self.page.url}

    def scroll(self, pixels: int) -> dict[str, Any]:
        self.page.mouse.wheel(0, pixels)
        return {"pixels": pixels}

    def screenshot(self, output: Path) -> dict[str, Any]:
        output = output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=output, full_page=True)
        if not output.is_file() or output.stat().st_size == 0:
            raise OSError(f"Screenshot was not written to {output}")
        return {"path": str(output), "bytes": output.stat().st_size}

    def tabs(self) -> dict[str, Any]:
        return {
            "tabs": [
                {"index": index, "url": page.url, "title": page.title()}
                for index, page in enumerate(self._context.pages)
            ]
        }

    def use_tab(self, index: int) -> dict[str, Any]:
        pages = self._context.pages
        if index < 0 or index >= len(pages):
            raise IndexError(f"Tab index {index} does not exist")
        self._page = pages[index]
        self._page.bring_to_front()
        return {"index": index, "url": self._page.url}

    def close(self) -> None:
        self._context.close()
        self._playwright.stop()
