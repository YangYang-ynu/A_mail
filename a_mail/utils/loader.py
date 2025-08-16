import tomli
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
import yaml
from langchain_qwq import ChatQwen


class PromptLoader:
    def __init__(self, prompt_path: str):
        """
        Initialize PromptLoader, load and parse TOML configuration file
        Args:
            prompt_path: Path to TOML configuration file
        """
        self.prompt_path = prompt_path
        self.config = self._load_config()
        self.entry_agent_name = self._find_entry_agent_name()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load TOML configuration file
        Returns:
            Parsed configuration dictionary
        """
        try:
            with open(self.prompt_path, "rb") as f:
                return tomli.load(f)
        except Exception as e:
            raise Exception(f"Failed to load prompt config: {str(e)}")

    def _find_entry_agent_name(self) -> str:
        """
        Find entry agent name

        Returns:
            Entry agent name
        """
        entry_agents = self.config.get("entry_agent", [])
        if not entry_agents:
            raise ValueError("No entry agent found in config")
        return entry_agents[0].get("name", "")

    def field_parsing(self) -> bool:
        """
        Check if all fields meet requirements

        Returns:
            bool: True if all fields meet requirements, False otherwise
        """
        agents = self.config.get("agents", [])

        required_fields = [
            "name", "name_zh", "description", "role_desc",
            "tools_desc", "collaboration_agents", "workflow_spec",
            "group", "llm_name"
        ]

        for agent in agents:
            # END agent is a special marker, can skip some field checks
            if agent.get("name") == "END":
                continue

            for field in required_fields:
                if field not in agent or agent[field] is None:
                    print(f"Missing required field '{field}' in agent '{agent.get('name', 'unknown')}'")
                    return False

                # Check if field content is empty (except for fields that can be empty)
                if field not in ["name_zh", "examples", "notes"] and not str(agent[field]).strip():
                    print(f"Empty required field '{field}' in agent '{agent.get('name', 'unknown')}'")
                    return False

        return True

    def get_agent_names(self) -> List[str]:
        """
        Get list of all agent names

        Returns:
            List[str]: List of agent names
        """
        agents = self.config.get("agents", [])
        return [agent["name"] for agent in agents if "name" in agent]

    def get_collaborative_agents_by_name(self, agent_name: str) -> List[str]:
        """
        Get collaborative agents list by agent name

        Args:
            agent_name: Agent name

        Returns:
            List[str]: List of collaborative agent names
        """
        agents = self.config.get("agents", [])
        for agent in agents:
            if agent.get("name") == agent_name:
                return agent.get("collaboration_agents", [])
        return []

    def get_prompt_by_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete prompt configuration by agent name

        Args:
            agent_name: Agent name

        Returns:
            Dict[str, Any]: Complete agent configuration information, None if not found
        """
        if agent_name not in self.get_agent_names():
            print(f"Agent: {agent_name}  does not exist")
            return None


        agents = self.config.get("agents", [])
        for agent in agents:
            if agent.get("name") == agent_name:
                return agent
        return None

    def entry_point_agent_name(self) -> str:
        """
        Get entry point agent name

        Returns:
            str: Entry point agent name
        """
        return self.entry_agent_name



class ModelLoader:
    """
    A class to load and configure language models based on a YAML configuration file.
    The models are expected to be compatible with the OpenAI API interface.
    """

    def __init__(self, model_path: str):
        self.model_path=model_path
        self.config=self.__get_config()

    def __get_config(self,):

        with open(self.model_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data

    def __get_model_detail_by_name(self,model_name:str):
        for model_type in self.config:
            # print(model_type)
            for model_dict in self.config[model_type]["models"]:
                # print(model_dict)
                if model_dict["name"]==model_name:
                    return {
                        "model_name":model_name,
                        "api_key":self.config[model_type]["api_key"],
                        "base_url":self.config[model_type]["base_url"],
                        "model_type":model_type
                    }

        print(f"model: {model_name} is unconfigured")
        return None

    def get_llm(self,model_name):
        model_info=self.__get_model_detail_by_name(model_name)
        if model_info["model_type"]=="Openai":
            llm = ChatOpenAI(
                model=model_info['model_name'],
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=model_info['api_key'],
                base_url=model_info['base_url'],

            )
            return llm
        elif model_info["model_type"]=="Qwen":
            llm = ChatQwen(
                api_key=model_info['api_key'],
                api_base=model_info['base_url'],
                model=model_info['model_name']

            )
            return llm
        # elif model_info["model_type"]=="Anthropic":
        #     llm = ChatAnthropic(
        #         model_name=model_info['model_name'],
        #         temperature=0,
        #         base_url=model_info['base_url'],
        #         api_key=model_info['api_key'],
        #         timeout=None,
        #         max_retries=2,
        #         stop=["_84552"]
        #     )
        #     return llm
        else:
            llm = ChatOpenAI(
                model=model_info['model_name'],
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=model_info['api_key'],
                base_url=model_info['base_url'],

            )
            return llm



if __name__ == '__main__':
    modelloader=ModelLoader("/user_examples/four_basic_operations/model_config.yaml")
    print(modelloader.get_llm("kimi-k2-0711-preview").invoke("你好"))




