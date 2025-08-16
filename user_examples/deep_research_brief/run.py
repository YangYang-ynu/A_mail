from a_mail.core.graph import MultiAgentSystem
from user_examples.deep_research_brief.deep_reacher_tool import agent_tools_map

mas=MultiAgentSystem(prompt_path="prompts.toml",
                     model_path="model_config.yaml",
                     tool_dict=agent_tools_map
                     )



# mas.show_mermaid_graph()

mas.run_with_checkpoint(input_message="please follow the rules and run")
# mas.run_with_checkpoint(input_message="please follow the rules and run",continue_run=False,thread_id="c1c6a445-543a-48ac-8ecc-c6ed5b834432")