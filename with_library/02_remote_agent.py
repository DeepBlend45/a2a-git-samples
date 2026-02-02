import os
from strands import Agent, tool
from fastapi import FastAPI
import uvicorn
import logging
from strands.multiagent.a2a import A2AServer
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv

import base64
from strands.telemetry import StrandsTelemetry
import uuid


load_dotenv()
logging.basicConfig(level=logging.INFO)

# Langfuseの認証情報をBase64エンコード
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

LANGFUSE_AUTH = base64.b64encode(
    f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()
).decode()  

# OpenTelemetry のエンドポイントと認証ヘッダーを設定
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LANGFUSE_BASE_URL + "/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

# OpenTelemetry エクスポーターをセットアップ
strands_telemetry = StrandsTelemetry().setup_otlp_exporter()


model = OpenAIModel(
    client_args={"api_key": os.environ["OPENAI_API_KEY"]},
    model_id="gpt-4o-mini",
    params={"temperature": 0.2},
)


@tool
def get_weather(city_name: str) -> str:
    """Get the current weather."""
    return f"{city_name} is Sunny"

session_id = str(uuid.uuid4())  
# Create a Strands agent
strands_agent = Agent(
    name="Weather Agent",
    model=model,
    description="A weather agent that can search weather.",
    tools=[get_weather],
    trace_attributes={
        "session.id": session_id,                 # セッション識別
        "user.id": "test-user@example.com",       # ユーザー識別
        "langfuse.tags": ["シングルエージェント"],  # タグ付け
    },
    callback_handler=None
)

host = "127.0.0.1"
port = 9001
# Create A2A server (streaming enabled by default)
a2a_server = A2AServer(
    agent=strands_agent,
    host=host,
    port=port,
    )

# # Start the server
# a2a_server.serve()

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)