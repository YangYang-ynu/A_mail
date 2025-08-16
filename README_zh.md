# A_mail — 基于 LangGraph 的多智能体通信协议解决方案

中文版 | [English Version](README.md)

## 目录
- [特别致谢](#特别致谢)
- [背景介绍](#背景介绍)
- [遇到的问题](#遇到的问题)
- [解决思路](#解决思路)
- [A_mail_demo 系统功能和限制](#a_mail_demo-系统功能和限制)
- [快速使用指南](#快速使用指南)
  - [1. 克隆项目](#1-克隆项目)
  - [2. 安装依赖](#2-安装依赖)
  - [3. 配置模型](#3-配置模型)
  - [4. 设计提示词](#4-设计提示词)
  - [5. 开发工具](#5-开发工具)
  - [6. 运行系统](#6-运行系统)
- [提示词编写说明](#提示词编写说明)
- [工具辅助说明](#工具辅助说明)
- [示例项目](#示例项目)
- [开源协议](#开源协议)
- [写到最后](#写到最后)
---

---

## 特别致谢

> 🙏 **感谢 LangGraph 框架**
> 
> 我们要特别感谢 **[LangGraph](https://github.com/langchain-ai/langgraph)** 框架提供的强大支持。LangGraph 丰富的多智能体架构模式和便捷的 API 工具为 A_mail 的开发奠定了坚实基础。正是得益于 LangGraph 优秀的框架支持，这个项目才得以实现。

---


## 背景介绍

LangGraph 提供了丰富的多智能体架构模式（如网络架构、Supervisor 架构、分层架构等），并且配套了便捷的 API 工具，方便开发者快速搭建系统。

然而，在实际构建中，**需要融合多种架构模式、构建复杂的多智能体系统，仍然需要大量编码工作，尤其是路由设计方面，提示词编写也很考验经验。**

---

## 遇到的问题

在早期的开发中，我用最直接的方式实现 Agent 之间的路由：通过一大堆 `if...else...` 语句和命令调用。

当系统从 6 个 Agent 扩展到 14 个、再到 16 个时（模型能力远没有我们设想的那么强，所以将任务分配的更加具体，agent数目变得越来越多），问题逐渐显现：

- 路由逻辑写死，难以扩展，违背了 **开闭原则**
- 路由逻辑提前创建，违背了 **创建者原则**
- 路由规则与提示词紧耦合，一处修改可能引发连锁反应

继续这样下去，当系统扩展和维护都是非常困难的。

---

## 解决思路

有没有可能引入一个**中间层**来化解这个问题？

这个中间层定义了统一的**输出格式**和**解析规则**，负责所有 Agent 之间的消息转发，消除了 Agent 之间的直接依赖。

![](./image/parse_forward_zh.drawio.svg)

于是，**A_mail** 应运而生。

> **A_mail = 一个结构化输出 + 对应的解析规则**

详见：

`sra_mail/core/sys_prompt.py`

它将 Agent 间的通信抽象成类似“邮件”的对象（借鉴命令模式），并通过一个负责解析和转发的中介者模块实现：

- **自动路由**
- **状态保存与恢复**
- **快速原型迭代**

这样，开发者可以更专注于整体架构设计、提示词的优化和工具的开发（这里我们就可以借助 AI 辅助设计），而不必被繁琐的路由编码拖慢进度。

当智能体数量变多时，结构就会是这样的：

![](./image/al_zh.drawio.svg)


---

## A_mail_demo 系统功能和限制

### ✅ 我们系统能做什么

| 功能                     | 说明                                  |
|------------------------|-------------------------------------|
| **快速构建多智能体系统**         | 只需**构建提示词**和**编写工具代码**即可，其余由框架执行    |
| **节点自动路由**             | 根据 agent 输出自动解析并决定消息发送目标，无需手写复杂路由逻辑 |
| **图状态保存与恢复**           | 支持保存执行图状态，异常中断后可恢复继续执行，避免重复操作       |
| **灵活可扩展的消息格式（A-mail）** | 自定义字段丰富，便于开发者快速搭建多智能体系统原型及二次开发      |
| **自动格式校验与错误处理**        | 解析节点自动检测输出格式错误，引导 agent 重新生成，提升容错性  |
| **统一的多 agent 提示词管理**   | 使用 TOML 集中管理提示词，方便维护和统一设计           |
| **支持多 agent 协作和工具调用**  | agent 之间消息传递规范化，工具注入支持，便于复杂任务分工和调用  |
| **控制台流式监控打印信息**        | 可以在控制台观看流式输出的结果                     |


### ❌ 我们系统不能做什么

| 功能                                | 说明                                                                 |
|-------------------------------------|----------------------------------------------------------------------|
| **高效的并行执行（MapReduce功能）** | 当前不支持 LangGraph 的 send() 并发执行，仅支持串行任务流转，效率有限。后续版本将重点实现         |
| **高级记忆管理与上下文优化**         | 记忆管理较为简单，未深度结合 LangMem，缺乏复杂上下文工程和记忆优化                              |
| **上下文和 Token 消耗优化**         | 由于提示词模板冗长及上下文窗口大，token 消耗高，对模型上下文长度要求高                          |
| **代码结构规范化**                   | 目前代码结构混合类和函数，风格不统一，缺乏严格的编码规范，后续版本计划重构                        |
| **模型适配问题**                    | 当前支持 OpenAI API 格式调用的模型，其余形式部署的模型无法使用，后续将依次适配                    |

---

## 快速使用指南

### 1. 克隆项目

注意：项目开发时候使用的python是3.12，建议使用python3.12

```bash
git clone https://github.com/dev-yang-ai/A_mail.git
```

### 2. 安装依赖

进入项目目录后，运行以下命令安装所需依赖：

```bash
pip install -r requirements.txt
```

### 3. 写模型配置文件

目前系统支持基于 OpenAI API Key 格式的模型调用，包括常见的 OpenAI 模型、Deepseek、Qwen 系列、Moonshot 的 Kimi 模型等。

创建模型的配置文件，格式如下

```yaml
deepseek:
  api_key: sk-XXX
  base_url: https://api.deepseek.com
  models:
    - name: deepseek-chat
      input_price: 0.000001
      output_price: 0.000004
 ```

（输入输出字段目前还未实现功能，填写任意数字即可）

确保配置中的模型名称与提示词 TOML 文件中模型名称命名保持一致。

### 4. 编写提示词文件

多智能体系统的核心之一是提示词设计。

你可以在以下路径编辑或添加提示词，同时需要指定入口 agent：

你可以创建一个toml文件并且可以按照这里写提示词：- [提示词编写说明](#提示词编写说明)


### 5. 开发工具

工具是系统与外部环境交互的接口。

请根据设计文档，在以下文件中实现或扩展工具功能：

创建一个工具py文件，可以按照这里的方法：- [工具辅助说明](#工具辅助说明)

完成工具开发后，务必维护好 agent 与工具的对应关系字典。

### 6. 运行系统

创建一个python文件将之前的模型配置、提示词文件地址和工具字典输入框架：
```python
from a_mail.core.graph import MultiAgentSystem
from user_examples.deep_research_brief.deep_reacher_tool import agent_tools_map

mas=MultiAgentSystem(prompt_path="prompts.toml",
                     model_path="model_config.yaml",
                     tool_dict=agent_tools_map
                     )
#打印mermaid图，可以复制到相关解析器查看
mas.show_mermaid_graph()
#运行系统，无回滚
mas.run_with_checkpoint(input_message="please follow the rules and run")
#运行系统，有回滚，到线程id为XXX-XXX-XXX的上一个执行断点
mas.run_with_checkpoint(input_message="please follow the rules and run",continue_run=True,thread_id="XXX-XXX-XXX")
```

首次运行时，系统会生成一个 UUID 作为本次执行标识。

如果运行过程中被手动终止或因网络/服务器等不可抗力因素中断，你可以通过输入此 UUID 并将 `is_continue` 设置为 `true` 来恢复执行。

> ⚠️ 注意：请确保所有 agent 名称和工具名称配置一致，避免出现调用错误。

---

## 提示词编写说明

我们提示词的基本需要如下：

### 1. 入口智能体

```toml
[[entry_agent]]
name = "user_clarifier"
```

我们需要指定系统的入口智能体。

### 2. 智能体提示词设计

```toml
[[agents]]
name = "user_clarifier"
name_zh = "用户澄清器"
description = "负责分析用户消息，判断是否需要澄清，并在信息足够时通知研究主管"
role_desc = """
你的核心职责于用户沟通确定用户的需求，确定是否需要与用户沟通，让用户澄清问题。
"""
tools_desc = """
- ask_human() ：当你需要向用户提问时，调用此工具。
- write_conversation(): 将你与用户的对话写下来，做记录
"""
collaboration_agents = ["research_topic_generator"]
examples = ""
notes = ""
workflow_spec = """
1. 调用工具 ask_human 与用户沟通，明确研究方向，确保用户解释和你的理解一致，可以多次调用此工具询问用户，当你觉得无歧义时继续执行
2. 调用工具 write_conversation 将你和用户的对话记录下来
3. 联系 research_topic_generator 告知他已经完成沟通，可以进行工作
"""
group = "report_generation_process"
llm_name = "qwen3-coder-plus"
```

#### 字段说明

| 字段名              | 是否必需 | 用途                                                                 |
|---------------------|----------|----------------------------------------------------------------------|
| `name`              | ✅ 必需   | agent 唯一标识符，程序内使用                                           |
| `name_zh`           | ❌ 可选   | 中文可读名，便于理解                                                 |
| `description`       | ✅ 建议   | 功能摘要，用于向其他 agent 介绍该 agent 的用途                         |
| `role_desc`         | ✅ 必需   | LLM 的角色定义                                                       |
| `tools_desc`        | ✅ 必需   | 工具调用说明，注重工具的额外使用说明，不需要告诉模型的具体调用参数     |
| `collaboration_agents` | ✅ 建议 | 协作关系，支持自动路由                                               |
| `examples`          | ❌ 可选   | Few-shot 示例，提升一致性，请使用 A-mail 格式构建当前需要与其他 agent 交互的最终输出 |
| `notes`             | ❌ 可选   | 补充说明、边界处理                                                   |
| `workflow_spec`     | ✅ 强烈建议 | 明确执行流程，支持自动化解析                                         |
| `group`             | ❌ 可选   | 作为拓展字段，功能开发中                                             |
| `llm_name`          | ✅ 必需   | 指定运行模型                                                         |

---

## 工具辅助说明

工具作为智能体的感官系统，我们希望通过这个方式构建。

我们以这个与用户对话的工具为例：

```python
def talk_with_user(
    question: Annotated[str, "需要向用户提出的问题"]
) -> str:
    """向用户提问并获取回答"""
    print(f"\n🤖 问题: {question}")
    try:
        return input("👤 回答: ")
    except KeyboardInterrupt:
        return "用户取消操作"
```

> ⚠️ 请务必使用函数的文档字符串说明该工具方法的用途，并推荐使用 `Annotated` 给工具参数添加注解。

当开发并且设计完成了这个工具，请务必在以下文件中以如下方式构建 agent 和工具对应的字典：

```python
agent_tools = {
    "user_clarifier": [talk_with_user, write_conversation],
    "research_topic_generator": [get_conversations],
    "lead_researcher": [],
    "sub_researcher": [duckduckgo_search, write_report, fetch_page_content],
    "report_generation": [get_research_raw_info, write_final_report]
}
```

之后系统会自动识别并添加到 agent 中。

---

## 示例项目


```
user_examples/deep_research_brief
```

我们粗略复现了 langchain 团队的 open_deep_research 项目，用来展示如何构建一个多智能体项目。

Agent 设计如下：

![](./image/open_deep_research_zh.drawio.svg)

运行如下命令体验我们的控制台流式输出功能：

```bash
python user_examples/deep_research_brief/run.py
```


```
user_examples/four_basic_operations
```
同时写了一个简单的加减乘除运算的多智能体，是使用supervisor架构实现的

可以尝试运行：
```bash
python user_examples/four_basic_operations/run.py
```

---

## 开源协议

本项目遵循宽松的 MIT 许可证，个人开发者和企业均可自由使用、修改和二次开发。

本项目旨在提升开发效率，启发新的思路。

如果本项目对您有所帮助，欢迎在介绍或传播时注明出处，简单提及 “A_mail” 即可，感谢支持！

---

## 写到最后

目前的这个系统是为了解决我的项目中的一个问题：写路由实在是太麻烦了，路由代码要写很多，而且经常检查不出错误。

然后发现好像没有人（或许是我了解的少）发出来解决方案（也可能是 langgraph 框架是一个新兴的框架），那我给大家提供一个我的解决方案。

如果能够给各位开发者带来启发，那我也是非常开心的。

关于维护问题，我肯定是会维护的，毕竟我还是觉得这个方法很有趣，能够实现一些好玩的事情。

如果有同学或者开发者想要加入，和我一起做一些这个项目没有解决的问题。~~比如可以将这个项目完善到可以 boot 起来 langgraph，或许我们就可以改名叫 langgraphboot —— 幻想一下，哈哈哈~~

我也十分欢迎，可以通过这个邮箱联系我：

`developer_yang@qq.com`

这个项目还是有一些 bug 的，当你在使用过程中遇到，你可以给我提出 issue，我应该会在一周内回复并且解决（当 bug 不太多时）。

---

