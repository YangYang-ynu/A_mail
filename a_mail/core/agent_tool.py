from a_mail.utils.loader import PromptLoader


class AgentTool:
    def __init__(self,tool_dict,prompt_path):
        self.tool_dict=tool_dict
        self.prompt_path=prompt_path
        self.__check()


    def __check(self):
        agents=PromptLoader(self.prompt_path).get_agent_names()
        for agent in agents:
            if agent not in self.tool_dict:
                self.tool_dict[agent]=[]
                print(f"Agent {agent} not initialized the tool list,adding it now.")

    def get_tools_by_name(self,agent_name):
        return self.tool_dict[agent_name]
