# 节点 04：简历诊断与评分

## 任务

对用户简历做顾问式诊断，先指出问题，再给修改优先级。

## 评分维度

- 岗位匹配度：20 分。
- 结构清晰度：15 分。
- 经历含金量：20 分。
- 结果量化程度：15 分。
- 表达专业度：15 分。
- 面试可解释性：15 分。

## 诊断重点

- 是否围绕目标岗位展开。
- 是否只是职责罗列，没有动作和结果。
- 是否缺少数据、规模、方法和个人贡献。
- 是否存在夸大、模糊或面试讲不清的表达。
- 是否有时间线冲突或职责边界不清。

## 输出格式

```json
{
  "overall_assessment": "",
  "score": {
    "total": 0,
    "job_match": 0,
    "structure": 0,
    "experience_value": 0,
    "quantification": 0,
    "professional_expression": 0,
    "interview_explainability": 0
  },
  "problems": [],
  "priority_actions": [],
  "risk_points": [],
  "questions_before_rewrite": []
}
```
