import json
import os
from datetime import datetime

from a_mail.core.agent import Agent
from a_mail.core.printer import MessageStreamer
from a_mail.core.state import StateCreator
from a_mail.utils.loader import PromptLoader
import uuid
import logging
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from typing_extensions import  Literal
from a_mail.utils.parse_output import parse_output_to_dict, replace_mail_type_with_receive


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)
class MultiAgentSystem:
    def __init__(self,prompt_path,model_path,tool_dict):

        self.prompt_path=prompt_path
        self.model_path=model_path
        self.tool_dict=tool_dict
        self.state=StateCreator().create_state_class(self.prompt_path)
        self.agents=PromptLoader(self.prompt_path).get_agent_names()
        self.entry_agent_name=PromptLoader(self.prompt_path).entry_point_agent_name()



        self.graph_builder = StateGraph(self.state)



        for agent_name in self.agents:
            # logger.info(agent_name)

            self.graph_builder.add_node(agent_name, self.__create_agent_node(agent_name))
        # logger.info()
        self.graph_builder.add_node("parsing_and_forwarding_node", self.__parsing_and_forwarding_node)

        # entry

        self.graph_builder.add_edge(START, self.entry_agent_name)
        # add checkpoint
        memory = MemorySaver()
        # creat graph
        self.graph = self.graph_builder.compile(checkpointer=memory)
        # logger.info graph
    def show_mermaid_graph(self):
        logger.info(self.graph.get_graph().draw_mermaid())

    def __create_agent_node(self, agent_name):

        collaboration_agents =PromptLoader(self.prompt_path).get_collaborative_agents_by_name(agent_name)
        if "END" in collaboration_agents:
            collaboration_agents.remove("END")

        def agent_node(state) -> Command[Literal[*collaboration_agents]]:

            if state.get("is_resume", False):
                logger.info(f"[jump to node]: {state["current_agent"][-1].content} ")
                return Command(goto=state["current_agent"][-1].content, update={"is_resume": False})

            agent = Agent(agent_name,self.prompt_path,self.model_path,self.tool_dict).create_agent()

            agent_message_list = f"{agent_name}_messages"
            # logger.info(state)
            # plogger.info(state[agent_message_list][-1])
            response = agent.invoke({"messages": state[agent_message_list]})
            # logger.info(response)
            return Command(goto="parsing_and_forwarding_node", update={
                # stored the agent's messages history
                agent_message_list: response.get("messages", []),
                # add to public raw history
                "response_raw": response.get("messages", []),
                "current_agent": agent_name,  # stored current agent for resumption
            })

        return agent_node

    def __parsing_and_forwarding_node(self, state):
        parsed_message = parse_output_to_dict(state["response_raw"][-1].content)

        try:
            A_mail = replace_mail_type_with_receive(parsed_message["A-mail"])
            receiver = parsed_message["receiver"]
            sender = parsed_message["sender"]
            if receiver == "END":
                return Command(goto=END, update={
                    receiver + "_messages": [
                        HumanMessage(content=A_mail, name=f"{sender}")
                    ],
                    "current_agent": receiver  # END
                })

            # check if the collaboration agent exists
            collaboration_agents = PromptLoader(self.prompt_path).get_collaborative_agents_by_name(sender)

            if receiver in set(collaboration_agents):
                # exist
                return Command(goto=receiver, update={
                    receiver + "_messages": [
                        HumanMessage(content=A_mail, name=f"{sender}")
                    ],
                    "current_agent": receiver
                })
            else:
                # does not exist
                return Command(goto=sender, update={
                    sender + "_messages": [
                        HumanMessage(
                        content=f"[Output Error]: Agent '{receiver}' not found. Please verify  agent name. theAvailable agents: {str(collaboration_agents)}",
                        name="parsing_and_forwarding_node")
                    ],
                    "current_agent": sender  # return to sender agent
                })
        except:
            if len(parsed_message) == 0:
                return Command(goto=state["current_agent"][-1].content, update={
                    state["current_agent"][-1].content + "_messages": [
                        HumanMessage(
                            content=(
                                f"[Output Error]: The message does not meet system requirements: "
                                f"'{state['response_raw'][-1].content}'. "
                                f"Please ensure this is the final output for the current task step, "
                                f"not a tool call or internal reasoning message. "
                                f"If this is the final output, format it using A-mail. "
                                f"If the task is not complete, continue processing."
                            ),
                        name="parsing_and_forwarding_node")
                    ],
                    "current_agent": state["current_agent"][-1].content  # 回到上一个节点
                })

    def run(self, input_message):
        inputs = {
            f"{self.entry_agent_name}_messages": [
                HumanMessage(content=input_message)
            ],
        }
        config = {
            "recursion_limit": 15000,
            "configurable": {"thread_id": 1}
        }

        streamer = MessageStreamer()

        try:
            for chunk in self.graph.stream(input=inputs, config=config, stream_mode="messages", subgraphs=True):
                streamer.process_chunk(chunk)
                # logger.info()
        finally:
            streamer.finish()

    def run_with_checkpoint(self, input_message, continue_run=False, thread_id=None):

        with SqliteSaver.from_conn_string("workflow_state.db") as checkpointer:

            graph = self.graph_builder.compile(checkpointer=checkpointer)
            config = {"recursion_limit": 15000, "configurable": {"thread_id": thread_id}}
            prev_state = graph.get_state(config)

            if continue_run == False:
                thread_id = str(uuid.uuid4())
                logger.info(f"[System] : Generated new thread , Thread Id : {thread_id} ")
                self.__log_thread_id(thread_id)


            else:
                # get the previously stored state
                if prev_state is None:
                    logger.info(f"[System]: Thread ID {thread_id} not found. Please check and try again.")

                    return

                try:
                    current_agent = prev_state.values["current_agent"][-1].content
                    logger.info(f"[System]: Starting from Agent: {current_agent} ")
                except:
                    logger.info("[System]: the current thread didn't record the initial agent . Please start without a thread id to begin a new session.")
                    return
                prev_state.values["is_resume"] = True

                # logger.info(prev_state)

            inputs = {
                f"{self.entry_agent_name}_messages": [
                    HumanMessage(content=input_message)],
                "is_resume": continue_run,
            }
            config = {
                "recursion_limit": 15000,
                "configurable": {"thread_id": thread_id}
            }

            streamer = MessageStreamer()
            try:
                for chunk in graph.stream(input=inputs, config=config, stream_mode="messages", subgraphs=True):
                    streamer.process_chunk(chunk)
            finally:
                streamer.finish()



    def __log_thread_id(self,thread_id):
        # 获取调用脚本的目录（即当前工作目录）
        calling_directory = os.getcwd()
        log_file = os.path.join(calling_directory, "thread_log.json")

        # 获取当前时间
        current_time = datetime.now().isoformat()

        # 要写入的数据
        log_entry = {
            "thread_id": thread_id,
            "timestamp": current_time
        }

        # 如果日志文件存在，则读取现有内容并追加
        if os.path.exists(log_file):
            with open(log_file, "r+", encoding="utf-8") as f:
                try:
                    # 尝试加载已有数据
                    data = json.load(f)
                except json.JSONDecodeError:
                    # 如果文件为空或不是有效 JSON，则初始化为空列表
                    data = []

                # 追加新记录
                data.append(log_entry)

                # 回到文件开头并写入更新后的内容
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()  # 防止旧内容残留
        else:
            # 如果文件不存在，创建新文件并写入第一个条目
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump([log_entry], f, indent=4, ensure_ascii=False)







