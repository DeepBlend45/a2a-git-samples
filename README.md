.envファイルに以下の内容をセットする

```
OPENAI_API_KEY = "YOUR_API_KEY"
LANGFUSE_SECRET_KEY = "YOUR_LANGFUSE_SECRET_KEY"
LANGFUSE_PUBLIC_KEY = "YOUR_LANGFUSE_PUBLIC_KEY"
LANGFUSE_BASE_URL = "https://us.cloud.langfuse.com"
```

Docker Compose でコンテナ間通信する場合は、Supervisor 側の URL をサービス名ベースで指定してください。

```
KNOWN_AGENT_URLS = "http://currency-agent:9000,http://weather-agent:9001,http://temperature-agent:9002"
```

各 Agent は必要に応じて次の環境変数で上書きできます。

```
PUBLIC_HOST = "<agent-cardに載せるホスト名>"
PORT = "<listenポート>"
BIND_HOST = "0.0.0.0"
```

以下を別のターミナルでそれぞれ実行する

```
uv run 01_remote_agent.py
uv run 02_remote_agent.py
uv run 03_remote_agent.py
uv run clent.py
```
