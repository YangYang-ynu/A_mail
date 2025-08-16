from typing import Dict, TypedDict, Annotated

from langgraph.graph import add_messages

from a_mail.utils.loader import PromptLoader


# 创建 TokenUsage 类
class TokenUsage(TypedDict):
    input_tokens: int
    output_tokens: int
    total_tokens: int

class StateCreator:

    @staticmethod
    def create_state_class(prompt_path):
        # 获取 agent names

        agent_names = PromptLoader(prompt_path).get_agent_names()

        # 创建 State 类的基础结构
        state_fields = {
            "response_raw": Annotated[list, add_messages],
            "current_agent": Annotated[list, add_messages],
            "is_resume": bool,
            "token_usage": Dict[str, TokenUsage],
        }

        # 动态添加 agent 名称字段
        for agent in agent_names:
            field_name = f"{agent}_messages"
            state_fields[field_name] = Annotated[list, add_messages]

        # 创建 State 类
        return TypedDict('State', state_fields)

