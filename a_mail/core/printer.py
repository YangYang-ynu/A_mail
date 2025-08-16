
from colorama import init, Fore, Style
from typing import Annotated
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_qwq import ChatQwQ, ChatQwen

from langchain_core.messages import AIMessageChunk, ToolMessage, HumanMessage
from colorama import init, Fore, Style
# 初始化colorama
init(autoreset=True)


class MessageStreamer:
    def __init__(self):
        self.last_message_type = None
        self.current_color = None
        self.current_prefix = None

    def get_message_type(self, message):
        if isinstance(message, AIMessageChunk):
            has_content = bool(message.content)
            has_tool_calls = (hasattr(message, 'tool_call_chunks') and message.tool_call_chunks) or \
                             (hasattr(message, 'tool_calls') and message.tool_calls) or \
                             (hasattr(message, 'additional_kwargs') and message.additional_kwargs.get('tool_calls'))
            if has_tool_calls:
                return 'tool_call'
            elif has_content:
                return 'ai'
            else:
                return None
        elif isinstance(message, ToolMessage):
            return 'tool_response'
        elif isinstance(message, HumanMessage):
            return 'human'
        return None

    def get_color_and_prefix(self, msg_type):
        colors = {
            'ai': (Fore.GREEN, '[🤖 AI ] '),
            'tool_call': (Fore.BLUE, '[🔧 Tool Call] '),
            'tool_response': (Fore.YELLOW, '[✅ Tool Response] '),
            'human': (Fore.CYAN, '[👤 Human Message] ')
        }
        return colors.get(msg_type, (Fore.WHITE, '[❓ Unknown Type ] '))

    def print_with_color(self, text):
        if self.current_color:
            print(f"{self.current_color}{text}", end="", flush=True)
        else:
            print(text, end="", flush=True)

    def process_chunk(self, chunk):
        try:
            chunk_data, (message, metadata) = chunk
            msg_type = self.get_message_type(message)

            if not msg_type:
                return

            if msg_type != self.last_message_type:
                if self.last_message_type is not None:
                    print()
                self.last_message_type = msg_type
                self.current_color, self.current_prefix = self.get_color_and_prefix(msg_type)
                print(f"{self.current_color}{self.current_prefix}", end="", flush=True)

            if msg_type == 'ai':
                if hasattr(message, 'content') and message.content:
                    self.print_with_color(message.content)

            elif msg_type == 'tool_call':
                # 直接从chunk中提取并打印工具调用信息
                tool_info = ""

                # 尝试从不同位置获取工具调用信息
                if hasattr(message, 'tool_call_chunks') and message.tool_call_chunks:
                    for tool_call in message.tool_call_chunks:
                        func_name = tool_call.get('name', '')
                        args = tool_call.get('args', '')
                        if func_name or args:
                            tool_info += f"{func_name}({args})" if func_name else f"{args}"

                elif hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        func_name = tool_call.get('name', '')
                        args = tool_call.get('args', {})
                        if func_name:
                            tool_info += f"{func_name}({args})"

                elif hasattr(message, 'additional_kwargs') and message.additional_kwargs.get('tool_calls'):
                    tool_calls_raw = message.additional_kwargs.get('tool_calls', [])
                    for tc in tool_calls_raw:
                        func_data = tc.get('function', {})
                        func_name = func_data.get('name', '')
                        args = func_data.get('arguments', '')
                        if func_name or args:
                            tool_info += f"{func_name}({args})" if func_name else f"{args}"

                if tool_info:
                    self.print_with_color(tool_info)

            elif msg_type == 'tool_response':
                self.print_with_color(f"{message.name}: {message.content}")

            elif msg_type == 'human':
                self.print_with_color(message.content)

        except Exception as e:
            print(f"\n{Fore.RED}[⚠️ Error ] {e}{Style.RESET_ALL}")

    def finish(self):
        if self.last_message_type is not None:
            print(f"{Style.RESET_ALL}")
        print()