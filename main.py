import os
from langchain.agents.agent import AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import initialize_agent, AgentType
from langchain_openai.chat_models.base import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import serpapi
from pprint import pprint
import json
import re

load_dotenv()

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

@tool(return_direct=True)
def return_as_json(data: str) -> dict:
    """
    Takes a description or structured list and converts it into valid JSON.
    """
    import json
    try:
        return json.loads(data)
    except Exception:
        return {"error": "Invalid JSON, here is the raw data", "raw": data}

def extract_json_from_text(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return None

tools = [serpapi_google_search, return_as_json]
llm = ChatOpenAI(model="gpt-4o", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(
        content="""
        You are a tech recruiter that matches jobs to candidates.
        You use Google Search via serpapi_google_search tool with a query like this: '(ashby OR lever OR greenhouse) {role} {location}'.
        Roles can be backend, data or frontend.
        The serpapi_google_search will return a list of JSONs like this:
        [
            {
                "position": 81,
                "title": "Software Engineer (Remote, LATAM) @ Rutter",
                "link": "https://jobs.ashbyhq.com/rutter/80f95cac-3a18-4633-85fd-a571142507d8",
                "redirect_link": "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://jobs.ashbyhq.com/rutter/80f95cac-3a18-4633-85fd-a571142507d8&ved=2ahUKEwj8mf2Yz8qOAxWGJNAFHYedAucQFnoFCIQBEAE",
                "displayed_link": "https://jobs.ashbyhq.com \u203a rutter",
                "favicon": "https://serpapi.com/searches/687c7316271332851ddb89a0/images/96f9803d34170abebd99559daa4ae608c8ddb6c7c4480c84da6ec1c86e57162b.png",
                "snippet": "... Backend (Fullstack) Engineer from Brazil to join our Integrations Engineering team. In this role, you'll design, build, and maintain integrations with key ...",
                "snippet_highlighted_words": [
                    "Backend"
                ],
                "source": "Ashby"
            }
        ]
        For the location, try to make the search wider, for example, if a given candidate is from Argentina, try looking for Latin America or LATAM instead.
        So candidates will provide their role and location and you'll replace that values into the query and do the following:
        1. Analyze all the results to get only those that are a job posting from the ATS.
        2. For each job, you'll visit the link and will analyze the job description and also will visit the company page to get some info about the product, and crunch base to check the financial details.
        3. For each job, create a JSON containing:
            * job_link,
            * quick_description,
            * job_title,
            * tech_stack,
            * company_name,
            * company_type (startup or consulting),
            * industry (Just is company is startup),
            * Stage (meaning that if the company is series seed, A, etc)
        4. The result must be an array of json

        When you're done, output only the final result as valid JSON using the return_as_json tool. Do not include any explanation or formatting.
        """
    ),
    MessagesPlaceholder("agent_scratchpad"),
    MessagesPlaceholder("input")
])
agent = create_openai_functions_agent(
    tools=tools,
    llm=llm,
    prompt=prompt
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def main():
    user_input = "Hi, I'm a backend engineer from Colombia looking for jobs"
    result = agent_executor.invoke({
        "input": [HumanMessage(content=user_input)],
    })
    pprint(result["output"])
    # raw_output = result["output"]
    # parsed = extract_json_from_text(raw_output)
    # print(parsed)

if __name__ == '__main__':
    main()
