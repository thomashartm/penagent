import requests

class WebSearchTool:
    """Tool for querying search engines and fetching results programmatically."""
    def search(self, query):
        """Search the web and return results."""
        try:
            resp = requests.get('https://duckduckgo.com/html/', params={'q': query}, timeout=10)
            if resp.status_code == 200:
                # Simple parse for result links
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                results = []
                for a in soup.select('.result__a')[:5]:
                    results.append({'title': a.get_text(), 'href': a['href']})
                return {'results': results}
            else:
                return {'error': f'Status {resp.status_code}'}
        except Exception as e:
            return {'error': str(e)} 