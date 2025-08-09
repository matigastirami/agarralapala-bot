import logging

from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.agents.agent import AgentExecutor

from pydantic import SecretStr

from agents.common.abstract_agent import Agent
from agents.common.tools.get_candidates import get_candidates
from agents.common.tools.google_search import serpapi_google_search
from agents.common.tools.json_tools import convert_to_json
from agents.common.tools.save_job_postings import save_job_postings
from agents.job_seeker.prompts import prompt
from common.config.config import OPENAI_API_KEY

class JobSeekerAgent(Agent):
    def __init__(self):
        tools = [serpapi_google_search, convert_to_json, get_candidates, save_job_postings]
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=SecretStr(OPENAI_API_KEY))
        agent = create_openai_functions_agent(
            tools=tools,
            llm=llm,
            prompt=prompt
        )
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    @property
    def name(self) -> str:
        return "job_seeker_agent"

    def exec(self, **kwargs):
        logging.info('[JobSeekerAgent] trying to execute LLM call')
        result = self.executor.invoke(
            kwargs.get("input", {}),
            config={
                "configurable": {
                    "max_steps": 25
                },
            }
        )
        output = result["output"]
        return output


if __name__ == '__main__':
    agent = JobSeekerAgent()
    agent.exec()