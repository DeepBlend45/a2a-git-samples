import logging

from a2a.types import AgentCard, AgentCapabilities, AgentSkill

# LangGraph A2A Server
from langgraph_a2a_server import A2AServer

# LangChain/LangGraph
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PUBLIC_HOST = "127.0.0.1"   # AgentCard に載せる “到達可能なホスト”
BIND_HOST = "0.0.0.0"       # サーバが listen するアドレス
PORT = 9002

agent_card = AgentCard(
    name="Temperature Agent",
    description="Fetch the current temperature for a location",
    url=f"http://{PUBLIC_HOST}:{PORT}",
    version="0.0.1",
    protocol_version="0.3.0",
    preferred_transport="JSONRPC",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(
            id="get_temperature",
            name="get_temperature",
            description="Get the current temperature for a given city name.",
            tags=["temperature"],
            examples=["東京の気温は？", "What is the temperature in Osaka?"],
            input_modes=["text"],
            output_modes=["text"],
        )
    ],
)


@tool
def get_temperature(city_name: str) -> str:
    """Get the current temperature."""
    return f"{city_name} is 15℃"


# Create LangGraph agent
agent = create_agent(
    model="openai:gpt-4.1-nano",
    tools=[get_temperature],
    checkpointer=InMemorySaver(),
)

# Create A2A server with the agent
server = A2AServer(
    graph=agent,
    agent_card=agent_card,
    port=9002,
)

# Start the server
if __name__ == '__main__':
    server.serve()