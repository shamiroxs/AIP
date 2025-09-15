import requests, socket, ssl
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

def first_search_result(query: str) -> str | None:
    url = "https://duckduckgo.com/html/"
    r = requests.get(url, params={"q": query}, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    result = soup.select_one(".result__a")
    if not result:
        return None

    href = result.get("href")
    if not href:
        return None

    # DuckDuckGo result links often look like: /l/?uddg=<encoded_target>
    parsed = urlparse(href)
    qs = parse_qs(parsed.query)
    if "uddg" in qs:
        return unquote(qs["uddg"][0])  # real target URL
    return href  # if it's already a direct link

def has_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False

def check_network(pkg):
    try:
        if not has_internet():
            return f"No internet connection. Cannot search for {pkg}. Try checking your package manager."
        # Try a real HTTPS request to detect SSL issues
        import requests
        requests.get("https://pypi.org", timeout=3)
        return True
    except (requests.exceptions.RequestException, ssl.SSLError):
        return f"No internet connection. Cannot search for {pkg}. Try checking your package manager."