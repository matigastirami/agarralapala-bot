import os

import serpapi

from langchain_core.tools import tool
from pydantic import BaseModel, Field

class GoogleSearchInput(BaseModel):
    search_q: str = Field(description="The search query sent to serpapi")
    results_per_page: int = Field(description="The total results per page, defaults to 100", default=100)

@tool("serpapi_google_search", args_schema=GoogleSearchInput)
def serpapi_google_search(search_q: str, results_per_page: int = 100):
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
            "num": results_per_page
        }
        results = serp_api_client.search(params)
        # parsed_results = {}
        # if "organic_results" not in results:
        #     raise Exception("Could not find any result on serpapi")

        # # TODO: fetch at most 5 - 6 pages (env var to configures)
        # for item in results["organic_results"]:
        # return parsed_results
        organic = results.get("organic_results", [])[:5]
        return [{"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")} for r in organic]
    except Exception as e:
        print('Exception at serp_api google search call', e)
