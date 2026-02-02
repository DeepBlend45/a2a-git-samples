.envファイルに以下の内容をセットする

```
OPENAI_API_KEY = "YOUR_API_KEY"
LANGFUSE_SECRET_KEY = "YOUR_LANGFUSE_SECRET_KEY"
LANGFUSE_PUBLIC_KEY = "YOUR_LANGFUSE_PUBLIC_KEY"
LANGFUSE_BASE_URL = "https://us.cloud.langfuse.com"
```

以下を別のターミナルでそれぞれ実行する

```
uv run 01_remote_agent.py
uv run 02_remote_agent.py
uv run 03_remote_agent.py
uv run clent.py
```