from a_mail.core.graph import MultiAgentSystem
from user_examples.four_basic_operations.four_basic_operations_tool import agent_tools

mas=MultiAgentSystem(prompt_path="prompts.toml",
                     model_path="model_config.yaml",
                     tool_dict=agent_tools
                     )

# mas.show_mermaid_graph()
mas.run_with_checkpoint(input_message="please follow the rules and run")