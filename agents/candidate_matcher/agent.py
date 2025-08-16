import logging

from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.agents.agent import AgentExecutor

from pydantic import SecretStr

from agents.candidate_matcher.prompts import prompt
from agents.common.abstract_agent import Agent
from agents.common.tools.get_candidates import get_candidates
from agents.common.tools.get_job_postings import get_job_postings
from agents.common.tools.enrich_job_postings import enrich_job_postings
from agents.common.tools.json_tools import convert_to_json
from agents.common.tools.save_matches import save_job_matches
from common.config.config import OPENAI_API_KEY

class CandidateMatcherAgent(Agent):
    def __init__(self):
        tools = [
            get_job_postings,
            enrich_job_postings,
            convert_to_json,
            get_candidates,
            save_job_matches
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
        return 'candidate_matcher_agent'

    def exec(self, **kwargs):
        logging.info('[CandidateMatcherAgent] trying to execute LLM call')
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
    agent = CandidateMatcherAgent()
    agent.exec()



