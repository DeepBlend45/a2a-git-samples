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
PORT = 9003

agent_card = AgentCard(
    name="Yen2Won Agent",
    description="Convert Japanese Yen to South Korean Won using a fixed 1円=10ウォン rate.",
    url=f"http://{PUBLIC_HOST}:{PORT}",
    version="0.0.1",
    protocol_version="0.3.0",
    preferred_transport="JSONRPC",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(
            id="convert_yen_to_won",
            name="convert_yen_to_won",
            description="Convert an amount in Japanese Yen to Korean Won using the fixed rate 1円=10ウォン (100円=1000ウォン).",
            tags=["currency", "conversion", "JPY", "KRW"],
            examples=["1000円は何ウォン？", "Convert 2500 yen to won"],
            input_modes=["text"],
            output_modes=["text"],
        )
    ],
)


@tool
def convert_yen_to_won(amount_yen: float) -> str:
    """Convert Japanese Yen to Korean Won using the fixed rate 1円=10ウォン."""
    amount_won = float(amount_yen) * 10
    return f"{amount_yen}円は{amount_won}ウォンです（固定レート: 1円=10ウォン）"


# Create LangGraph agent
agent = create_agent(
    model="openai:gpt-4.1-nano",
    tools=[convert_yen_to_won],
    checkpointer=InMemorySaver(),
)

# Create A2A server with the agent
server = A2AServer(
    graph=agent,
    agent_card=agent_card,
    port=PORT,
)

# Start the server
if __name__ == '__main__':
    server.serve()
