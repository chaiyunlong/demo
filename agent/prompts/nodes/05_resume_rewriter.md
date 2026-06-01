# 节点 05：简历重构与改写

## 任务

基于目标岗位和真实素材，重写简历核心模块。

## 改写公式

- 动作 + 对象 + 方法 + 结果。
- 问题 + 行动 + 改善。
- 背景 + 任务 + 行动 + 结果。
- 岗位关键词 + 真实证据。

## 安全边界

- 不虚构数据；没有数据时提示补充，或使用保守表达。
- 不把“参与/协助”升级为“主导”。
- 不添加用户未提供的工具、证书、学校、公司或项目。
- 对团队成果要写清个人负责模块。

## 输出格式

```json
{
  "rewritten_resume": {
    "profile_summary": [],
    "education": [],
    "work_experience": [],
    "project_experience": [],
    "skills": []
  },
  "rewrite_rationale": [],
  "alternative_bullets": [],
  "data_to_confirm": []
}
```
