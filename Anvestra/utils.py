SEARCH_ENGINES = {
    "Google": {
        "search": "https://www.google.com/search?q={query}",
        "home": "https://www.google.com"
    },
    "DuckDuckGo": {
        "search": "https://duckduckgo.com/?q={query}",
        "home": "https://duckduckgo.com"
    },
    "Bing": {
        "search": "https://www.bing.com/search?q={query}",
        "home": "https://www.bing.com"
    }
}

DEFAULT_ENGINE = "Google"

from urllib.parse import quote_plus
from PyQt6.QtCore import QUrl

def build_url_from_input(user_input=None, engine_name=DEFAULT_ENGINE):
    engine = SEARCH_ENGINES.get(engine_name, SEARCH_ENGINES[DEFAULT_ENGINE])

    if not user_input:
        return QUrl(engine["home"])

    if user_input.startswith("http://") or user_input.startswith("https://"):
        return QUrl(user_input)

    search_url = engine["search"].format(query=quote_plus(user_input))
    return QUrl(search_url)