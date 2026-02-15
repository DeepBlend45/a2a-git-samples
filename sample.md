# a2a-git-samples メモ

## このリポジトリでできること（調査結果）
- A2A（Agent-to-Agent）で複数の専門エージェントを連携し、Supervisor から委譲して回答できます。
- 主なサンプルは以下です。
  - 為替エージェント（USD/JPY のレート回答）
  - 天気エージェント（都市名に対する天気回答）
  - 気温エージェント（都市名に対する気温回答）
  - 円→ウォン換算エージェント（固定レート）
- `with_library/` は `langgraph-a2a-client/server` を使う実装、`no_library/` は A2A を低レベルに組み立てる実装です。
- `no_library` 側には NG キーワードを弾く `ContentFilterMiddleware` も含まれます。

## 起動方法（簡潔）
1. `.env` を作成し、`OPENAI_API_KEY`（必要なら Langfuse のキー）を設定。
2. 依存関係をインストール。
   - `uv sync`
3. それぞれ別ターミナルでエージェントを起動（例: with_library 構成）。
   - `uv run with_library/01_remote_agent.py`  （:9000）
   - `uv run with_library/02_remote_agent.py`  （:9001）
   - `uv run with_library/03_remote_agent.py`  （:9002）
4. Supervisor（クライアント）を起動。
   - `uv run with_library/client.py`

必要に応じて `with_library/04_remote_agent.py`（:9003）や `no_library` 配下の同等サンプルも利用できます。
