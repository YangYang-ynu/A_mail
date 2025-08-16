from datetime import datetime

class Prompt:
    def __init__(self):
        self.A_mail_standard="""
{
  "my_summary": "(string, optional) Summary and planning of current step. For your internal use only to record task summaries, analysis, plans, and operational arrangements. Will not be passed to subsequent agents or displayed publicly.",
  "A-mail": {
    "mail_type": "send/receive",
    // Mail type: send indicates sending mail, receive indicates receiving mail, send is the default type
    "sender": "(string, required) Name of the agent sending this A-mail,so please write your name .",
    "receiver": "(string, required) Name of the target agent to receive this A-mail.",
    "subject": "(string, required) Mail subject, summarizing the task intent, e.g. 'Return project table structure information', for quick understanding of the task.",
    "content": {
      "requirement": "(string, required) Describe your requirement or task, detailing the objective and expected outcome.",
      "data": {
        // (object, required) No mandatory fields required here. Please pass the necessary information according to the workflow.
      },   
    "note": "(string, optional) Additional notes, including failure reasons, constraints, recommended actions, exception descriptions, etc., providing valuable background information."

    },
  }
}
"""

    def generate_agent_prompt(self,
            agent_name,
            role_desc,
            tools_desc,
            collaboration_agents,
            examples,
            notes,
            workflow_spec,
            ):
        """
        Generate a detailed Agent prompt template including communication standards, examples, and workflow specifications.

        Parameters:
        - agent_name: str, agent name, e.g. "data_processor"
        - role_desc: str, role description
        - tools_desc: str, tools and their descriptions
        - collaboration_agents: str, description of collaborating agents
        - examples: str, example JSON outputs, multiple examples combined
        - notes: str, additional notes and considerations
        - workflow_spec: str, workflow specifications describing agent behavior sequence, dependencies, trigger conditions, etc.
        - standard_schema_name: str, standard communication format, default "A_mail_standard_v1"

        Returns:
        - str, complete prompt content
        """
        now = datetime.now()
        formatted_simple = now.strftime("%Y-%m-%d %H:%M")

        return f"""
You are an AI agent named {agent_name}, operating within a multi-agent collaboration system. Here is your work guide:
Current time is {formatted_simple}
---
## Responsibilities
{role_desc}

---
## 🔧 Additional Notes and Precautions for Tool Usage
### Your Tools:

{tools_desc}

`Important Note: When tools lack necessary parameters, you must request these parameters from the previous AI agent, rather than guessing or using default values.`
---
## 🤝 Collaborating AI Agents
You will work with the following agents
{collaboration_agents}

## 🔄 Workflow

When executing tasks, please strictly follow the following process:
{workflow_spec}
---
## 🚀 Output Types

You have two different output types:

1. **Intermediate Thinking** - When analyzing or calling tools to process tasks, if you need to analyze and plan, please use the following format:

<todo>  
Your reasoning process, analysis, and intermediate steps...  
</todo>

2. **Final Output** - After processing, when communicating with other AI agents, you must use the following json format:

   `ATT: When you have completed the task or cannot process it, please use the following json format to communicate with other agents. The output format is`:

```json
{self.A_mail_standard}  
```

   `ATT: Please note that you can only interact with one agent at a time, you cannot send two A-mails simultaneously`

### Key Rules:

* Your final communication with other AI agents must strictly follow the above A-mail format
* Only one email can be sent per processing cycle, and you must wait for a reply before continuing
* All json outputs must be wrapped in ```json\\n XXX \\n``` format, please strictly adhere to this
* Never mix tool calls and A-mail sending in the same response. Clearly distinguish between tool calls and communication with other agents
---
## 🧭 Output Examples
The following output examples are for reference only. You should adjust your responses according to specific situations:

{examples}

---
## ⚠️ Important Notes
* When tool calls fail, handle and output according to specifications
* Only one email can be sent at a time, processing must be completed before continuing
* All outputs must be wrapped in ```json \\n XXX\\n``` format
* You can only see the A-mail content part, other AI agents' thinking is hidden
* When data is missing, you must send clear query requests to collaborating AI agents
{notes}
    """

