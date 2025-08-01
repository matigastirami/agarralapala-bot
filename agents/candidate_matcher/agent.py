from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.messages.human import HumanMessage

from pydantic import SecretStr

from agents.candidate_matcher.prompts import prompt
from agents.common.tools.get_candidates import get_candidates
from agents.common.tools.get_job_postings import get_job_postings
from agents.common.tools.json_tools import return_as_json
from agents.common.tools.save_matches import save_job_matches
from common.config.config import OPENAI_API_KEY

# TODO: missing add candidates table and a tool to retrieve all
tools = [
    get_job_postings,
    return_as_json,
    get_candidates,
    save_job_matches
]
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=SecretStr(OPENAI_API_KEY))

agent = create_openai_functions_agent(
    tools=tools,
    llm=llm,
    prompt=prompt,
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def exec_matching_agent():
    result = agent_executor.invoke({
        # "input": [HumanMessage(content=user_input)],
    }, config={
        "configurable": {
            "max_steps": 25
        },
    })
    output = result["output"]
    print(output, isinstance(output, list))
    return output

if __name__ == '__main__':
    print(exec_matching_agent())


