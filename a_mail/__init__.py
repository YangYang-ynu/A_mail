"""
a_mail - A multi-agent system for email automation
"""

__version__ = "0.1.0"
__author__ = "dev-yang "

from .core.agent import Agent
from .core.agent_tool import AgentTool
from .core.graph import MultiAgentSystem
from .core.printer import MessageStreamer
from .core.state import StateCreator
from .core.sys_prompt import Prompt

from .utils.loader import PromptLoader, ModelLoader
from .utils.parse_output import parse_output_to_dict, replace_mail_type_with_receive

__all__ = [
    'Agent', 'AgentTool', 'MultiAgentSystem', 'MessageStreamer',
    'StateCreator', 'Prompt', 'PromptLoader', 'ModelLoader',
    'parse_output_to_dict', 'replace_mail_type_with_receive'
]