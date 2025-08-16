import os

import serpapi

from langchain_core.tools import tool
from pydantic import BaseModel, Field

class GoogleSearchInput(BaseModel):
    search_q: str = Field(description="The search query sent to serpapi")
    results_per_page: int = Field(description="The total results per page, defaults to 100", default=100)
    country: str = Field(description="Country code for location-specific results (e.g., 'us', 'uk', 'ar', 'br', 'mx')", default="us")
    language: str = Field(description="Language code for search results (e.g., 'en', 'es', 'pt')", default="en")

@tool("serpapi_google_search", args_schema=GoogleSearchInput)
def serpapi_google_search(search_q: str, results_per_page: int = 100, country: str = "us", language: str = "en"):
    """
    Call serp api Google search with a search query
    """
    serp_api_key = os.getenv("SERPAPI_KEY")
    serp_api_client = serpapi.Client(api_key=serp_api_key)
    if not serp_api_key:
        raise Exception("Missing SERPAPI_KEY variable")

    try:
        params = {
            "engine": "google",
            "q": search_q,
            "num": results_per_page,
            "gl": country,  # Country parameter for location-specific results
            "hl": language  # Language parameter for localized results
        }
        results = serp_api_client.search(params)
        organic = results.get("organic_results", [])
        return [{"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")} for r in organic]
    except Exception as e:
        print('Exception at serp_api google search call', e)
