from langgraph.prebuilt import create_react_agent
from a_mail.core.agent_tool import AgentTool
from a_mail.core.sys_prompt import Prompt
from a_mail.utils.loader import PromptLoader, ModelLoader


class Agent():
    def __init__(self, agent_name, prompt_path, model_path, tool_dict):
        self.agent_name = agent_name
        self.prompt_path = prompt_path
        self.model_path = model_path
        self.tool_dict = tool_dict
        self.config = PromptLoader(prompt_path=self.prompt_path).get_prompt_by_name(self.agent_name)


        # load prompt
        self.prompt = self.__get_prompt()



    def __get_prompt(self):
        prompt_loader = PromptLoader(self.prompt_path)
        # config=
        collaboration_agents_info = ""

        for agent in self.config["collaboration_agents"]:
            if "END" == agent.upper():
                collaboration_agents_info += "- END : to end."
                continue
            collaboration_agents_info += "- " + agent + " : " + prompt_loader.get_prompt_by_name(agent)[
                "description"] + "\n"

        prompt = Prompt().generate_agent_prompt(
            agent_name=self.config["name"],
            role_desc=self.config["role_desc"],
            tools_desc=self.config["tools_desc"],
            collaboration_agents=collaboration_agents_info,
            examples=self.config["examples"],
            notes=self.config["notes"],
            workflow_spec=self.config["workflow_spec"],
        )
        return prompt

    def create_agent(self):
        modelloader = ModelLoader(self.model_path)
        llm = modelloader.get_llm(self.config['llm_name'])
        agent_tool = AgentTool(self.tool_dict, self.prompt_path)

        return create_react_agent(
            model=llm,
            tools=agent_tool.get_tools_by_name(self.agent_name),
            prompt=self.prompt,
            name=self.agent_name,
        )



