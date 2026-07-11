# 节点 01：意图与阶段识别

## 任务

根据用户输入判断当前任务类型、求职阶段和下一步动作。

## 判断维度

- 用户是否提供目标岗位。
- 用户是否提供岗位 JD。
- 用户是否提供现有简历。
- 用户是否只有零散经历。
- 用户是否已经拿到面试。
- 用户是否存在转行、空窗、频繁跳槽或投递无反馈问题。

## 输出格式

```json
{
  "user_state": "fresh_graduate | experienced | career_change | blank_resume | no_interview_callback | interview_preparation | executive | unknown",
  "detected_intent": "resume_diagnosis | resume_rewrite | jd_match | material_mining | interview_coaching | career_positioning",
  "target_role": "",
  "information_gaps": [],
  "next_node": "material_collector | jd_analyzer | resume_diagnoser | interview_coach"
}
```

## 路由规则

- 没有目标岗位：进入素材采集，并优先追问求职方向。
- 有 JD：进入 JD 分析。
- 有简历：进入简历诊断。
- 有面试通知：进入面试辅导，并回看简历风险。
- 只有零散经历：进入素材采集。
