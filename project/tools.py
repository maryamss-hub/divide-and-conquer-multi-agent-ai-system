import urllib.request
import urllib.parse
import json

def get_wikipedia_summary(query):
    """
    Dummy API Integration tool for fulfilling project requirements.
    Fetches the Wikipedia summary for a given query.
    """
    try:
        # Wikipedia requires User-Agent header and URL encoding
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AgenticSystemResearchTool/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("extract", "No summary found on Wikipedia.")
    except Exception as e:
        return f"Tool Error (Wikipedia API): {str(e)}"
