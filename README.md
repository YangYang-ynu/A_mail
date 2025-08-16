<p align="center">
  <img src="./image/logo.png" alt="Logo" width="200">
</p>


# A_mail — A Multi-Agent Communication Protocol Solution Based on LangGraph

[简体中文](README_zh.md) | English Version

## Table of Contents

- [Acknowledgements](#acknowledgements)
- [Introduction](#introduction)
- [Problems Encountered](#problems-encountered)
- [Solution Approach](#solution-approach)
- [A_mail_demo System Features and Limitations](#a_mail_demo-system-features-and-limitations)
- [Quick Start Guide](#quick-start-guide)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure the Model](#3-configure-the-model)
  - [4. Design Prompts](#4-design-prompts)
  - [5. Develop Tools](#5-develop-tools)
  - [6. Run the System](#6-run-the-system)
- [Prompt Writing Instructions](#prompt-writing-instructions)
- [Tool Development Instructions](#tool-development-instructions)
- [Example Projects](#example-projects)
- [License](#license)
- [Final Notes](#final-notes)

---

## Acknowledgements

> 🙏 **Special Thanks to LangGraph** 
> 
> We would like to express our sincere gratitude to the **[LangGraph](https://github.com/langchain-ai/langgraph)** framework for providing powerful multi-agent architecture support and convenient API tools. The rich architectural patterns and robust functionality of LangGraph laid the foundation for A_mail's development. Without LangGraph's excellent framework support, this project would not have been possible.

---
 
## Introduction

LangGraph provides rich multi-agent architecture patterns (such as network architecture, Supervisor architecture, hierarchical architecture, etc.) along with convenient API tools, making it easy for developers to quickly build systems.

However, in actual development, **building complex multi-agent systems that integrate multiple architectural patterns still requires a lot of coding work**, especially when it comes to routing design. Prompt engineering also demands significant experience.

---

## Problems Encountered

In early development, I used the most direct approach to implement routing between Agents: using a large number of `if...else...` statements and command calls.

As the system scaled from 6 Agents to 14, then to 16 (because models are far less capable than we initially assumed, so tasks had to be more granular, leading to more agents), problems gradually emerged:

- Routing logic was hardcoded, making it difficult to extend — violating the **Open/Closed Principle**
- Routing logic was pre-created — violating the **Creator Principle**
- Routing rules were tightly coupled with prompts, causing cascading issues when changes were made

If continued this way, both system expansion and maintenance would become extremely difficult.

---

## Solution Approach

Is there a way to introduce an **intermediate layer** to solve this problem?

This intermediate layer defines a unified **output format** and **parsing rules**, responsible for forwarding messages between all Agents, eliminating direct dependencies between them.

![](./image/parse_forward_en.drawio.svg)

Thus, **A_mail** was born.

> **A_mail = Structured Output + Corresponding Parsing Rules**

See details in:

`sra_mail/core/sys_prompt.py`

It abstracts communication between agents into "mail"-like objects (inspired by the Command Pattern) and implements automatic routing, state saving/restoration, and fast prototyping via a mediator module:

- **Automatic Routing**
- **State Saving & Recovery**
- **Rapid Prototype Iteration**

This allows developers to focus on overall architecture design, prompt optimization, and tool development (with AI-assisted design support), without being slowed down by tedious routing code.


When the number of agents increases, the structure will look like this:



![](./image/al_en.drawio.svg)


---

## A_mail_demo System Features and Limitations

### ✅ What Our System Can Do

| Feature | Description |
|--------|-------------|
| **Rapid Multi-Agent System Construction** | Only requires **prompt design** and **tool coding**; the rest is handled by the framework |
| **Automatic Node Routing** | Automatically parses agent outputs and determines message destinations without complex routing logic |
| **Graph State Save & Restore** | Supports saving execution graph state and resuming after interruptions to avoid redundant operations |
| **Flexible & Extensible Message Format (A-mail)** | Customizable fields make it easy to prototype and extend multi-agent systems |
| **Auto Format Validation & Error Handling** | Parsing nodes detect output format errors and guide agents to regenerate, improving fault tolerance |
| **Unified Prompt Management for Multiple Agents** | Uses TOML for centralized prompt management, facilitating maintenance and consistent design |
| **Support for Multi-Agent Collaboration & Tool Calls** | Standardized message passing between agents and tool injection for complex task division and invocation |
| **Streaming Console Monitoring** | View streaming output results directly in the console |

### ❌ What Our System Cannot Do

| Feature | Description |
|--------|-------------|
| **Efficient Parallel Execution (MapReduce Functionality)** | Does not currently support LangGraph's `send()` concurrent execution, only serial task flow. Will be implemented in future versions |
| **Advanced Memory Management & Context Optimization** | Simple memory management, not deeply integrated with LangMem, lacks advanced context engineering and memory optimization |
| **Context & Token Consumption Optimization** | Due to verbose prompt templates and large context windows, token consumption is high, requiring strong model context capabilities |
| **Code Structure Standardization** | Current code mixes classes and functions with inconsistent styles. Will refactor in future versions |
| **Model Adaptation Issues** | Currently supports models with OpenAI API format. Other deployment formats not yet supported; will adapt in later versions |

---

## Quick Start Guide

### 1. Clone the Repository

Note: Python 3.12 was used during development. It is recommended to use Python 3.12.

```bash
git clone https://github.com/dev-yang-ai/A_mail.git
```

### 2. Install Dependencies

After entering the project directory, run the following command to install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Write Model Configuration File

The system currently supports models that use the OpenAI API Key format, including common OpenAI models, DeepSeek, Qwen series, and Moonshot's Kimi model.

Create a model configuration file in the following format:

```yaml
deepseek:
  api_key: sk-XXX
  base_url: https://api.deepseek.com  
  models:
    - name: deepseek-chat
      input_price: 0.000001
      output_price: 0.000004
```

(Note: Input/output fields are not yet functional. Any numbers can be filled in.)

Ensure that the model names in the configuration match those in the prompt TOML file.

### 4. Write Prompt Files

One of the cores of a multi-agent system is prompt design.

You can edit or add prompts at the following path and specify the entry agent:

You can create a TOML file and write prompts as shown here: [Prompt Writing Instructions](#prompt-writing-instructions)

### 5. Develop Tools

Tools are the interface for system interaction with the external environment.

According to the design documentation, implement or extend tool functionality in the following file:

Create a Python tool file and follow the method shown here: [Tool Development Instructions](#tool-development-instructions)

After completing tool development, make sure to maintain the dictionary mapping agents to their tools.

### 6. Run the System

Create a Python file to input the model configuration, prompt file path, and tool dictionary into the framework:

```python
from a_mail.core.graph import MultiAgentSystem
from user_examples.deep_research_brief.deep_reacher_tool import agent_tools_map

mas = MultiAgentSystem(
    prompt_path="prompts.toml",
    model_path="model_config.yaml",
    tool_dict=agent_tools_map
)

# Print mermaid diagram, which can be copied to a parser for viewing
mas.show_mermaid_graph()

# Run the system without rollback
mas.run_with_checkpoint(input_message="please follow the rules and run")

# Run the system with rollback, continuing from the previous breakpoint of thread ID XXX-XXX-XXX
mas.run_with_checkpoint(
    input_message="please follow the rules and run",
    continue_run=True,
    thread_id="XXX-XXX-XXX"
)
```

On first run, the system generates a UUID as the execution identifier.

If the run is manually terminated or interrupted due to network/server issues, you can resume execution by inputting this UUID and setting `is_continue` to `true`.

> ⚠️ Note: Ensure all agent names and tool names are consistently configured to avoid invocation errors.

---

## Prompt Writing Instructions

The basic requirements for prompts are as follows:

### 1. Entry Agent

```toml
[[entry_agent]]
name = "user_clarifier"
```

We need to specify the system's entry agent.

### 2. Agent Prompt Design

```toml
[[agents]]
name = "user_clarifier"
name_zh = "User Clarifier"
description = "Responsible for analyzing user messages, determining if clarification is needed, and notifying the research lead when sufficient information is available"
role_desc = """
Your core responsibility is to communicate with users and confirm their needs, determine whether to communicate with the user, and ask the user to clarify the question.
"""
tools_desc = """
- ask_human(): Call this tool when you need to ask the user a question.
- write_conversation(): Record your conversation with the user.
"""
collaboration_agents = ["research_topic_generator"]
examples = ""
notes = ""
workflow_spec = """
1. Use the tool ask_human to communicate with the user, clarify the research direction, ensure user explanation aligns with your understanding. You can call this tool multiple times to ask the user. Proceed when you feel there is no ambiguity.
2. Use the tool write_conversation to record your conversation with the user.
3. Contact research_topic_generator to inform them that communication is complete and they can proceed with work.
"""
group = "report_generation_process"
llm_name = "qwen3-coder-plus"
```

#### Field Descriptions

| Field Name | Required | Purpose |
|------------|----------|---------|
| `name` | ✅ Required | Unique identifier for the agent, used within the program |
| `name_zh` | ❌ Optional | Chinese readable name for easier understanding |
| `description` | ✅ Recommended | Functional summary, used to introduce the agent to other agents |
| `role_desc` | ✅ Required | Role definition for the LLM |
| `tools_desc` | ✅ Required | Tool usage instructions, focusing on additional usage notes; no need to specify exact call parameters |
| `collaboration_agents` | ✅ Recommended | Collaboration relationships, supporting automatic routing |
| `examples` | ❌ Optional | Few-shot examples to improve consistency. Use A-mail format to build the final output for agent interaction |
| `notes` | ❌ Optional | Additional notes, boundary handling |
| `workflow_spec` | ✅ Strongly Recommended | Clear execution process, supporting automated parsing |
| `group` | ❌ Optional | Extension field, under development |
| `llm_name` | ✅ Required | Specifies the model to run |

---

## Tool Development Instructions

Tools act as the sensory system for agents. We hope to build them in this way.

Here is an example of a tool that interacts with the user:

```python
def talk_with_user(
    question: Annotated[str, "The question to ask the user"]
) -> str:
    """Ask the user a question and get their response"""
    print(f"\n🤖 Question: {question}")
    try:
        return input("👤 Answer: ")
    except KeyboardInterrupt:
        return "User canceled operation"
```

> ⚠️ Be sure to use the function's docstring to explain the tool's purpose and recommend using `Annotated` to add annotations to tool parameters.

After developing and designing the tool, be sure to construct the agent-tool mapping dictionary in the following file:

```python
agent_tools = {
    "user_clarifier": [talk_with_user, write_conversation],
    "research_topic_generator": [get_conversations],
    "lead_researcher": [],
    "sub_researcher": [duckduckgo_search, write_report, fetch_page_content],
    "report_generation": [get_research_raw_info, write_final_report]
}
```

The system will automatically recognize and add them to the agents.

---

## Example Projects

```
user_examples/deep_research_brief
```

We roughly reproduced the `open_deep_research` project from the LangChain team to demonstrate how to build a multi-agent project.

Agent design is as follows:

![](./image/open_deep_research_en.drawio.svg)

Run the following command to experience our console streaming output:

```bash
python user_examples/deep_research_brief/run.py
```

```
user_examples/four_basic_operations
```

We also built a simple multi-agent system for basic arithmetic operations using the Supervisor architecture.

You can try running:

```bash
python user_examples/four_basic_operations/run.py
```

---

## License

This project is licensed under the permissive MIT License. Both individual developers and enterprises are free to use, modify, and develop it further.

This project aims to improve development efficiency and inspire new ideas.

If this project has been helpful to you, feel free to mention "A_mail" when introducing or sharing it. Thank you for your support!

---

## Final Notes

The current system was developed to solve a problem in my own project: writing routing logic was too cumbersome, requiring a lot of code and often failing to catch errors.

I found that no one (or perhaps I haven’t seen it) has shared a solution (possibly because LangGraph is a relatively new framework). So I’m offering my solution to everyone.

If this can inspire fellow developers, I’ll be very happy.

Regarding maintenance, I will definitely keep it up, as I find this approach quite interesting and capable of achieving some fun things.

If any developers want to join and help solve some of the issues ~~this project hasn’t addressed yet — like making it possible to boot up LangGraph, maybe we could rename it to `langgraphboot` — just kidding, hahaha — I’m very welcome to that.~~

You can contact me via email:

`developer_yang@qq.com`

This project still has some bugs. If you encounter any while using it, feel free to open an issue. I should respond and fix it within a week (as long as there aren’t too many bugs).

---
