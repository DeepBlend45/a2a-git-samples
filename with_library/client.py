import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from langfuse.langchain import CallbackHandler

 
# a2a-with-library/supervisor/__main__.py
import logging

import asyncio

# LangGraph A2A Client
from langgraph_a2a_client import A2AClientToolProvider

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create A2A client tool provider with known agent URLs
provider = A2AClientToolProvider(
    known_agent_urls=[
        "http://127.0.0.1:9000",
        "http://127.0.0.1:9001",
        "http://127.0.0.1:9002",
    ]
)

langfuse_handler = CallbackHandler()

system_prompt = """
You are a team supervisor. Use A2A tools to delegate tasks.

IMPORTANT:
- When calling `a2a_send_message`, `target_agent_url` MUST be a full URL including scheme.
- Currency Agent URL is: "http://127.0.0.1:9000"
- Weather Agent URL is: "http://127.0.0.1:9001",
- Temperature Agent URL is: "http://127.0.0.1:9002",
- Do NOT pass agent names like "currency agent" as `target_agent_url`.
- If a tool call is rejected, do NOT propose the same tool call again in this conversation.
- If all relevant tool calls are rejected, respond clearly that you cannot retrieve the information without tool execution.
"""

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=provider.tools,
    system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "a2a_send_message": {
                    "allowed_decisions": ["approve", "reject"]
                },
                "search_web": False,
            }
        ),
    ]
)

print([tool.name for tool in provider.tools])

async def main():
    thread_id = "techorus-demo"
    user_input = input("メッセージを入力してください: ")
    config = {"configurable": {"thread_id": thread_id},"callbacks": [langfuse_handler]}

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config
    )

    print(f"result:{result}")

    while result.get("__interrupt__"):
        interrupts = result["__interrupt__"]
        print("\n=== ツール実行の承認が必要です ===")

        pending_actions = []
        for interrupt in interrupts:
            pending_actions.extend(interrupt.value.get("action_requests", []))

        decisions = []
        for i, action in enumerate(pending_actions, start=1):
            print(f"\n[{i}] ツール: {action['name']}")
            print(f"引数: {action['args']}")
            d = input("このツールを承認？ (approve/reject): ").strip().lower()
            if d not in ("approve", "reject"):
                raise ValueError("approve/reject 以外が入力されました")
            decisions.append({"type": d, "message": f"ユーザーが{action['name']}の実行を{d}しました"})

        result = await agent.ainvoke(
            Command(resume={"decisions": decisions}),
            config
        )

    print("\n=== 応答 ===")
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())