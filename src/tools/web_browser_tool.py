import subprocess
import uuid
import os
import re

class WebBrowserTool:
    """Tool for headless web browsing and screenshot capture using Playwright in a container."""
    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def browse(self, arg):
        # Extract the URL from the argument (handles 'browse <url>')
        match = re.search(r'(https?://\S+)', arg)
        if match:
            url = match.group(1)
        else:
            url = arg.strip()
        session_id = str(uuid.uuid4())
        output_file_host = os.path.join(self.output_dir, f'browser_output_{session_id}.html')
        output_file_container = f'/app/outputs/browser_output_{session_id}.html'
        # Run Playwright in the container to fetch the page content
        playwright_script = f"""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('{url}', timeout=30000)
        content = await page.content()
        with open('{output_file_container}', 'w') as f:
            f.write(content)
        await browser.close()
asyncio.run(main())
"""
        script_file_host = os.path.join(self.output_dir, f'playwright_script_{session_id}.py')
        with open(script_file_host, 'w') as f:
            f.write(playwright_script)
        # Copy script into container and execute
        subprocess.run([
            'docker', 'cp', script_file_host, f'pentest-playwright:/app/outputs/playwright_script_{session_id}.py'
        ], check=True)
        docker_cmd = [
            'docker', 'exec', 'pentest-playwright',
            'python', f'/app/outputs/playwright_script_{session_id}.py'
        ]
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=60)
        # Read the output file
        try:
            with open(output_file_host, 'r') as f:
                content = f.read()
        except Exception as e:
            content = f'[Error reading output file: {e}]'
        # Cleanup script file
        try:
            os.remove(script_file_host)
        except Exception:
            pass
        return {'content': content, 'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}

    def screenshot(self, url, output_path):
        # Similar logic can be implemented for screenshots if needed
        return {'error': 'Screenshot via container not yet implemented'}

    def spider(self, url, max_depth=2):
        session_id = str(uuid.uuid4())
        output_file_host = os.path.join(self.output_dir, f'spider_output_{session_id}.txt')
        output_file_container = f'/app/outputs/spider_output_{session_id}.txt'
        playwright_script = f"""
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
import sys
import os

visited = set()
found = set()

async def crawl(page, base_url, depth, max_depth):
    if depth > max_depth or base_url in visited:
        return
    visited.add(base_url)
    found.add(base_url)
    try:
        await page.goto(base_url, timeout=10000)
        links = await page.eval_on_selector_all('a', 'elements => elements.map(e => e.href)')
        for link in links:
            if link and urlparse(link).netloc == urlparse(base_url).netloc:
                await crawl(page, link, depth + 1, max_depth)
    except Exception as e:
        pass

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await crawl(page, '{url}', 0, {max_depth})
        with open('{output_file_container}', 'w') as f:
            for u in sorted(found):
                f.write(u + '\n')
        await browser.close()
asyncio.run(main())
"""
        script_file_host = os.path.join(self.output_dir, f'playwright_spider_{session_id}.py')
        with open(script_file_host, 'w') as f:
            f.write(playwright_script)
        subprocess.run([
            'docker', 'cp', script_file_host, f'pentest-playwright:/app/outputs/playwright_spider_{session_id}.py'
        ], check=True)
        docker_cmd = [
            'docker', 'exec', 'pentest-playwright',
            'python', f'/app/outputs/playwright_spider_{session_id}.py'
        ]
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=180)
        urls = []
        try:
            with open(output_file_host, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            urls = [f'[Error reading spider output: {e}]']
        try:
            os.remove(script_file_host)
        except Exception:
            pass
        return {'urls': urls, 'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode} 