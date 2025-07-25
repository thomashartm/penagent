from playwright.sync_api import sync_playwright

class WebBrowserTool:
    """Tool for headless web browsing and screenshot capture."""
    def browse(self, url):
        """Automate browsing to a URL and return page content."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                content = page.content()
                browser.close()
                return {'content': content}
        except Exception as e:
            return {'error': str(e)}

    def screenshot(self, url, output_path):
        """Capture a screenshot of the URL to output_path."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.screenshot(path=output_path)
                browser.close()
                return {'screenshot': output_path}
        except Exception as e:
            return {'error': str(e)} 