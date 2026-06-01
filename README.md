# 简历增长顾问 Agent

这是一个“简历撰写 + 面试辅导”智能体配置包，适合接入 Dify、Coze/扣子、FastGPT、LangChain、自研 Agent 编排系统或任何支持系统提示词与多节点工作流的平台。

## Agent 定位

简历增长顾问 Agent 面向求职者，提供从求职定位、素材采集、JD 分析、简历诊断、简历重写到面试辅导的完整闭环。它的核心不是简单润色，而是把用户真实经历转化为岗位相关、成果明确、面试可解释的职业表达。

## 目录结构

```text
agent/resume_interview_agent.json   # Agent 主配置
agent/prompts/system.md             # 总系统提示词
agent/prompts/nodes/                # 工作流节点提示词
agent/schemas/                      # 输入/输出 JSON Schema
tools/validate_agent.py             # 本地配置校验脚本
agent/examples/sample_session.md    # 示例会话
```

## 工作流

1. **意图与阶段识别**：判断用户是简历诊断、JD 匹配、素材挖掘还是面试准备。
2. **素材采集与追问**：补齐背景、目标、行动、方法、结果、数据和个人贡献。
3. **岗位 JD 分析**：提取核心职责、核心能力、关键词、隐性要求和证据需求。
4. **简历诊断与评分**：按 100 分制评估岗位匹配度、结构、经历含金量、量化程度、表达和面试可解释性。
5. **简历重构与改写**：使用“动作 + 对象 + 方法 + 结果”等公式生成可直接使用的 bullet。
6. **面试辅导与追问训练**：生成自我介绍、项目 STAR 讲述、深挖问题和风险问题应对。
7. **真实性与质量检查**：检查虚构、夸大、数据口径、职责边界和面试风险。
8. **最终交付**：输出简历诊断报告、优化后简历、JD 匹配分析、面试辅导包和下一步建议。

## 核心安全边界

- 不编造学校、公司、岗位、项目、证书、工具或具体业绩数据。
- 不把“参与/协助”改成“主导/负责整体”，除非用户明确说明。
- 缺少数据时优先追问；无法确认时使用保守表达。
- 每个简历亮点都必须能转化为可解释的面试回答。

## 快速使用

1. 将 `agent/prompts/system.md` 配置为 Agent 的系统提示词。
2. 将 `agent/resume_interview_agent.json` 中的 `workflow` 节点映射到你的编排平台。
3. 将 `agent/schemas/input.schema.json` 和 `agent/schemas/output.schema.json` 作为接口约束。
4. 使用 `agent/examples/sample_session.md` 进行首轮验证。


## 可运行本地 Agent

除了提示词和工作流配置，本仓库还提供了一个无外部依赖的 Python 运行时，可用于本地演示、接口冒烟测试和平台接入前验证。

### 运行示例

```bash
cat > /tmp/resume_request.json <<'JSON'
{
  "user_type": "fresh_graduate",
  "target_role": "用户运营",
  "experience_materials": "维护20个社群，每个约200人；试听课活动单场300人报名；写过15篇公众号。"
}
JSON

python3 -m resume_agent --input /tmp/resume_request.json --format markdown
```

### JSON 输出

```bash
python3 -m resume_agent --input /tmp/resume_request.json --format json
```

运行时会输出求职定位、JD/能力分析、简历诊断、优化后简历、面试辅导包和下一步建议。它不是替代大模型的最终文案能力，而是把 Agent 的路由、诊断、风控和交付结构落成可执行基线。


## 接入 OpenAI GPT

> 说明：ChatGPT Plus 是 ChatGPT 网页/App 订阅，不等同于 API Key；本项目的程序化接入使用 OpenAI API。你可以继续使用 Plus 账号体验 ChatGPT，但本地 Agent 调用 GPT 需要在 OpenAI Platform 创建 API Key，并配置 `OPENAI_API_KEY`。

### 配置 API Key

```bash
export OPENAI_API_KEY="your_api_key_here"
# 可选：覆盖默认模型
export OPENAI_MODEL="gpt-5.2"
```

### 使用 GPT 生成最终报告

```bash
python3 -m resume_agent --input /tmp/resume_request.json --engine openai --format markdown
```

### 使用指定模型

```bash
python3 -m resume_agent --input /tmp/resume_request.json --engine openai --model gpt-5.2 --format json
```

OpenAI 模式会先运行本地确定性诊断，生成基线报告，再把用户输入、系统提示词和基线报告发送到 Responses API，让 GPT 在真实性边界内生成更自然的最终交付稿。

## 本地校验

运行以下命令检查配置文件、提示词路径和 JSON Schema 是否有效：

```bash
python3 tools/validate_agent.py
```
