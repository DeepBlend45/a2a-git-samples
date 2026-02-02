import asyncio
import logging
from langchain.agents import create_agent
from .a2a_client import A2AClientToolProvider
from langgraph.checkpoint.memory import InMemorySaver

from ..middleware.content_filter_middleware import ContentFilterMiddleware

from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create A2A client tool provider with known agent URLs
provider = A2AClientToolProvider(known_agent_urls=[
    "http://127.0.0.1:9000", # Currency Expert
    "http://127.0.0.1:9001", # Weather Expert
])

system_prompt = """
You are a team supervisor. Use A2A tools to delegate tasks.

IMPORTANT:
- When calling `a2a_send_message`, `target_agent_url` MUST be a full URL including scheme.
- Currency Agent URL is: "http://127.0.0.1:9000"
- Weather Agent URL is: "http://127.0.0.1:9001",
- Do NOT pass agent names like "currency agent" as `target_agent_url`.
- If a tool call is rejected, do NOT propose the same tool call again in this conversation.
- If all relevant tool calls are rejected, respond clearly that you cannot retrieve the information without tool execution.
"""

# Create agent with A2A client tools
supervisor = create_agent(
    model="openai:gpt-4o-mini",
    tools=provider.tools,
    system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
    middleware=[
        ContentFilterMiddleware(
            banned_keywords=["hack", "exploit", "malware","東京"]
        ),
    ],
)

async def main():

    thread_id = "langgraph-a2a-demo"

    config = {"configurable": {"thread_id": thread_id}}



    while True:
        query = input("You> ").strip()
        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            break

        response = await supervisor.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": query, 
                }
            ]
        },config)

        for message in response["messages"]:
            if getattr(message, "content", None):
                print(f"AI> {message.content}")

if __name__ == "__main__":
    asyncio.run(main())

# cd /Users/atsuyayamada/workspace/a2a-langgraph
# uv run python -m no_library.supervisor_agent