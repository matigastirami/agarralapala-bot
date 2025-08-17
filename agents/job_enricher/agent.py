import logging

from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.agents.agent import AgentExecutor

from pydantic import SecretStr

from agents.job_enricher.prompts import prompt
from agents.common.abstract_agent import Agent
from agents.common.tools.enrich_job_postings import enrich_job_postings
from agents.common.tools.get_job_postings import get_job_postings
from agents.common.tools.json_tools import convert_to_json
from common.config.config import OPENAI_API_KEY

class JobEnricherAgent(Agent):
    def __init__(self):
        tools = [
            get_job_postings,
            enrich_job_postings,
            convert_to_json
        ]
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=SecretStr(OPENAI_API_KEY))
        agent = create_openai_functions_agent(
            tools=tools,
            llm=llm,
            prompt=prompt,
        )
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    @property
    def name(self) -> str:
        return 'job_enricher_agent'

    def exec(self, **kwargs):
        logging.info('[JobEnricherAgent] trying to execute LLM call')
        result = self.executor.invoke(
            kwargs.get('input', {}),
            config={
                "configurable": {
                    "max_steps": 250
                },
            }
        )
        output = result["output"]
        return output

if __name__ == '__main__':
    # Test LinkedIn job availability detection
    import logging
    from playwright.sync_api import sync_playwright
    from agents.common.tools.enrich_job_postings import check_job_availability
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test URLs
    test_urls = [
        "https://ar.linkedin.com/jobs/backend-developer-empleos",  # Search results page
        "https://www.linkedin.com/jobs/view/back-end-developer-at-sur-latam-4149955398/?originalSubdomain=ar"  # Specific job
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for url in test_urls:
            try:
                print(f"\nTesting URL: {url}")
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Check job availability
                result = check_job_availability(page, url)
                print(f"Result: {result}")
                
                # Get page title for debugging
                title = page.title()
                print(f"Page title: {title}")
                
            except Exception as e:
                print(f"Error testing {url}: {str(e)}")
        
        browser.close()
    
    # Run the actual agent
    agent = JobEnricherAgent()
    agent.exec()
