from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.messages.human import HumanMessage

from pydantic import SecretStr

from agents.common.tools.google_search import serpapi_google_search
from agents.common.tools.json_tools import return_as_json
from agents.job_seeker.prompts import prompt
from common.config.config import OPENAI_API_KEY

tools = [serpapi_google_search, return_as_json]
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=SecretStr(OPENAI_API_KEY))

agent = create_openai_functions_agent(
    tools=tools,
    llm=llm,
    prompt=prompt
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def exec_jobs_agent(user_input):
    result = agent_executor.invoke({
        "input": [HumanMessage(content=user_input)],
    })
    output = result["output"]
    print(output, isinstance(output, list))
    return output
