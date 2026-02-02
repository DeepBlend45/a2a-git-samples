from collections.abc import AsyncIterable
from typing import Any, Literal
from pydantic import BaseModel

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import Runnable

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FORMAT_INSTRUCTION = (
    'Set response status to input_required if the user needs to provide more information to complete the request.'
    'Set response status to error if there is an error while processing the request.'
    'Set response status to completed if the request is complete.'
)

class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'error'
    message: str


class LangGraphAgentAdapter:
    def __init__(self, agent: Runnable):
        self.graph = agent

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Calling a tool...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing tool result...',
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        print("STATE_KEYS:", list(current_state.values.keys()))
        print("STRUCTURED_RAW:", repr(current_state.values.get("structured_response")))
        print("STRUCTURED_TYPE:", type(current_state.values.get("structured_response")))
        logger.info("state keys=%s", list(current_state.values.keys()))
        logger.info("structured_response raw=%r", current_state.values.get("structured_response"))

        msgs = current_state.values.get("messages", [])

        # 末尾から「contentが空じゃない」ものを拾う
        final_text = None
        for m in reversed(msgs):
            content = getattr(m, "content", None)
            if content:
                final_text = content
                break

        if final_text:
            return {
                "is_task_complete": True,
                "require_user_input": False,
                "content": final_text,
            }

        # ToolMessageしか無い/AIMessageが空など、期待外のとき
        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": "Error: agent produced no final text.",
        }
        # structured_response = current_state.values.get('structured_response')
        # if structured_response and isinstance(
        #     structured_response, ResponseFormat
        # ):
        #     if structured_response.status == 'input_required':
        #         return {
        #             'is_task_complete': False,
        #             'require_user_input': True,
        #             'content': structured_response.message,
        #         }
        #     if structured_response.status == 'error':
        #         return {
        #             'is_task_complete': True,
        #             'require_user_input': False,
        #             'content': structured_response.message,
        #         }
        #     if structured_response.status == 'completed':
        #         return {
        #             'is_task_complete': True,
        #             'require_user_input': False,
        #             'content': structured_response.message,
        #         }

        # return {
        #     'is_task_complete': True,
        #     'require_user_input': False,
        #     'content': (
        #         'We are unable to process your request at the moment. '
        #         'Please try again.'
        #     ),
        # }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']