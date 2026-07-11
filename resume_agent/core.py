"""Rule-based runtime for the Resume Growth Advisor agent.

The prompt package describes how an LLM agent should behave. This module adds a
small deterministic runtime that can be used in demos, tests, and orchestration
platform smoke checks without calling an external model.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "agent" / "resume_interview_agent.json"

ROLE_KEYWORDS: dict[str, list[str]] = {
    "用户运营": ["社群", "用户", "活动", "转化", "留存", "活跃", "私域", "增长"],
    "新媒体运营": ["公众号", "小红书", "抖音", "内容", "选题", "阅读量", "涨粉", "互动"],
    "产品经理": ["需求", "原型", "PRD", "竞品", "用户调研", "功能", "迭代", "上线"],
    "数据分析": ["SQL", "Python", "Excel", "看板", "指标", "漏斗", "留存", "可视化"],
    "市场营销": ["品牌", "市场", "活动", "渠道", "投放", "曝光", "KOL", "ROI"],
    "销售": ["客户", "线索", "成交", "回款", "续约", "商机", "谈判", "客单价"],
}

STATE_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("fresh_graduate", ("应届", "校招", "毕业", "学生")),
    ("career_change", ("转行", "转岗", "跨行", "换方向")),
    ("interview_preparation", ("面试", "一面", "二面", "终面", "面邀")),
    ("no_interview_callback", ("没反馈", "无反馈", "没有回复", "海投")),
    ("executive", ("总监", "负责人", "管理岗", "团队管理", "高管")),
]

LOW_VALUE_PHRASES = ("负责日常", "协助完成", "参与活动", "沟通能力", "学习能力强", "吃苦耐劳")


@dataclass
class AgentRequest:
    """Normalized request fields accepted by the runtime."""

    user_type: str = "unknown"
    target_role: str = ""
    target_industry: str = ""
    target_city: str = ""
    company_type: str = ""
    current_problem: list[str] = field(default_factory=list)
    resume_text: str = ""
    job_description: str = ""
    experience_materials: str = ""
    interview_notice: str = ""
    output_mode: str = "deep"

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "AgentRequest":
        allowed = cls.__dataclass_fields__.keys()
        values = {key: payload.get(key) for key in allowed if key in payload}
        if isinstance(values.get("current_problem"), str):
            values["current_problem"] = [values["current_problem"]]
        return cls(**values)

    @property
    def combined_text(self) -> str:
        parts = [
            self.target_role,
            self.target_industry,
            " ".join(self.current_problem),
            self.resume_text,
            self.job_description,
            self.experience_materials,
            self.interview_notice,
        ]
        return "\n".join(part for part in parts if part)


class ResumeGrowthAdvisor:
    """Deterministic helper that mirrors the configured agent workflow."""

    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH) -> None:
        self.config_path = Path(config_path)
        with self.config_path.open("r", encoding="utf-8") as file:
            self.config = json.load(file)

    def analyze(self, request: AgentRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AgentRequest) else AgentRequest.from_mapping(request)
        target_role = normalized.target_role or self._detect_role(normalized.combined_text)
        user_state = self._detect_state(normalized)
        jd_analysis = self._analyze_jd(normalized.job_description, target_role)
        diagnosis = self._diagnose(normalized, target_role, jd_analysis)
        rewritten_resume = self._rewrite_resume(normalized, target_role)
        interview_pack = self._coach_interview(normalized, target_role, rewritten_resume)
        next_steps = self._next_steps(normalized, diagnosis)

        return {
            "profile_analysis": {
                "user_state": user_state,
                "target_role": target_role or "待确认",
                "main_challenge": self._main_challenge(normalized, diagnosis),
                "optimization_strategy": self._strategy_for_state(user_state),
            },
            "jd_analysis": jd_analysis,
            "resume_diagnosis": diagnosis,
            "rewritten_resume": rewritten_resume,
            "interview_coaching": interview_pack,
            "next_steps": next_steps,
        }

    def render_markdown(self, result: dict[str, Any]) -> str:
        """Render a structured result as a user-facing Markdown report."""

        profile = result["profile_analysis"]
        diagnosis = result["resume_diagnosis"]
        resume = result["rewritten_resume"]
        interview = result["interview_coaching"]
        jd = result.get("jd_analysis", {})

        lines = [
            "## 一、整体判断",
            f"- 用户状态：{profile['user_state']}",
            f"- 目标岗位：{profile['target_role']}",
            f"- 当前主要问题：{profile['main_challenge']}",
            f"- 优化策略：{profile['optimization_strategy']}",
            "",
            "## 二、岗位 JD/能力匹配",
        ]
        lines.extend(_bullet_lines("核心能力", jd.get("core_skills", [])))
        lines.extend(_bullet_lines("关键词", jd.get("keywords", [])))
        lines.extend(_bullet_lines("隐性要求", jd.get("hidden_requirements", [])))
        lines.extend(
            [
                "",
                "## 三、简历诊断",
                f"- 综合评分：{diagnosis['score']}/100",
            ]
        )
        lines.extend(_bullet_lines("主要问题", diagnosis.get("problems", [])))
        lines.extend(_bullet_lines("优先动作", diagnosis.get("priority_actions", [])))
        lines.extend(_bullet_lines("风险提醒", diagnosis.get("risk_points", [])))
        lines.extend(["", "## 四、优化后简历"])
        for section, title in [
            ("profile_summary", "个人优势"),
            ("education", "教育背景"),
            ("work_experience", "工作/实习经历"),
            ("project_experience", "项目经历"),
            ("skills", "技能证书"),
        ]:
            lines.append(f"### {title}")
            lines.extend([f"- {item}" for item in resume.get(section, [])] or ["- 待补充"])
            lines.append("")
        lines.extend(
            [
                "## 五、面试辅导包",
                "### 1 分钟自我介绍",
                interview.get("self_introduction", "待补充"),
                "",
            ]
        )
        lines.extend(_bullet_lines("深挖问题", interview.get("deep_dive_questions", [])))
        lines.extend(_bullet_lines("回答框架", interview.get("answer_frameworks", [])))
        lines.extend(_bullet_lines("风险应对", interview.get("risk_responses", [])))
        lines.extend(["", "## 六、下一步建议"])
        lines.extend([f"- {step}" for step in result.get("next_steps", [])])
        return "\n".join(lines).strip() + "\n"

    def _detect_role(self, text: str) -> str:
        role_scores = {
            role: sum(1 for keyword in keywords if keyword.lower() in text.lower())
            for role, keywords in ROLE_KEYWORDS.items()
        }
        best_role, best_score = max(role_scores.items(), key=lambda item: item[1])
        return best_role if best_score > 0 else ""

    def _detect_state(self, request: AgentRequest) -> str:
        if request.user_type and request.user_type != "unknown":
            return request.user_type
        text = request.combined_text
        for state, patterns in STATE_PATTERNS:
            if any(pattern in text for pattern in patterns):
                return state
        if not request.resume_text and request.experience_materials:
            return "blank_resume"
        if request.resume_text:
            return "experienced"
        return "unknown"

    def _analyze_jd(self, jd_text: str, target_role: str) -> dict[str, list[str]]:
        base_keywords = ROLE_KEYWORDS.get(target_role, [])
        discovered = _extract_keywords(jd_text)
        keywords = _dedupe(base_keywords + discovered)[:12]
        core_skills = self._infer_core_skills(target_role, keywords)
        hidden_requirements = [
            "能够解释个人贡献与团队成果的边界",
            "能够用数据或事实证明结果",
            "能够复盘项目过程并提出改进方案",
        ]
        return {
            "core_skills": core_skills,
            "keywords": keywords,
            "hidden_requirements": hidden_requirements,
        }

    def _infer_core_skills(self, target_role: str, keywords: list[str]) -> list[str]:
        role_skills = {
            "用户运营": ["用户分层", "社群运营", "活动转化", "数据复盘"],
            "新媒体运营": ["内容选题", "平台运营", "数据复盘", "粉丝增长"],
            "产品经理": ["需求分析", "用户调研", "原型设计", "跨部门推进"],
            "数据分析": ["数据清洗", "指标体系", "可视化看板", "业务洞察"],
            "市场营销": ["市场调研", "活动策划", "渠道传播", "效果复盘"],
            "销售": ["客户开发", "需求挖掘", "方案呈现", "商务谈判"],
        }
        return role_skills.get(target_role) or keywords[:4] or ["目标岗位待确认", "经历素材待补充"]

    def _diagnose(self, request: AgentRequest, target_role: str, jd_analysis: dict[str, list[str]]) -> dict[str, Any]:
        text = request.resume_text or request.experience_materials
        problems: list[str] = []
        priority_actions: list[str] = []
        risk_points: list[str] = []
        score = 70

        if not target_role:
            score -= 15
            problems.append("目标岗位不清晰，简历难以围绕招聘筛选逻辑展开。")
            priority_actions.append("先确认目标岗位、行业和投递场景，再决定经历排序。")
        if not request.resume_text:
            score -= 10
            problems.append("缺少完整简历文本，目前只能基于素材生成初版。")
            priority_actions.append("补充教育、实习/工作、项目、技能证书等完整模块。")
        if not _has_number(text):
            score -= 12
            problems.append("经历缺少人数、次数、比例、金额、周期等量化证据。")
            priority_actions.append("为每段经历补充规模、动作频次、结果数据或可解释的事实证据。")
        if any(phrase in text for phrase in LOW_VALUE_PHRASES):
            score -= 8
            problems.append("存在职责罗列或空泛评价，未体现方法、贡献和结果。")
            priority_actions.append("将低价值表达改写为“动作 + 对象 + 方法 + 结果”。")
        matched_keywords = [keyword for keyword in jd_analysis.get("keywords", []) if keyword and keyword in text]
        if jd_analysis.get("keywords") and len(matched_keywords) < 2:
            score -= 8
            problems.append("目标岗位关键词覆盖不足，可能影响招聘方快速识别匹配度。")
            priority_actions.append("把 JD 中的核心关键词自然嵌入相关经历，而不是堆砌在技能栏。")
        if re.search(r"主导|负责整体|从0到1|千万级|百万级", text):
            risk_points.append("存在高强度成果或职责表述，需确认是否能说明个人贡献、团队分工和数据口径。")
        if not risk_points:
            risk_points.append("输出前仍需逐项确认数据真实性、统计口径和个人职责边界。")

        return {
            "score": max(0, min(100, score)),
            "problems": problems or ["基础信息可用，但仍需要围绕目标岗位进一步强化成果和关键词。"],
            "priority_actions": priority_actions or ["保留真实经历，强化岗位相关动作、方法、结果和面试解释。"],
            "risk_points": risk_points,
        }

    def _rewrite_resume(self, request: AgentRequest, target_role: str) -> dict[str, list[str]]:
        source = request.resume_text or request.experience_materials
        bullets = _sentence_candidates(source)
        role_keywords = ROLE_KEYWORDS.get(target_role, [])[:4]
        profile_summary = [
            f"具备{target_role or '目标岗位'}相关经历，能够围绕业务目标梳理任务、执行动作并复盘结果。",
            "能够将项目经历拆解为背景、目标、行动、结果，并在面试中说明个人贡献。",
        ]
        if role_keywords:
            profile_summary.append(f"简历建议重点突出：{'、'.join(role_keywords)}。")

        rewritten = [self._rewrite_bullet(bullet, target_role) for bullet in bullets[:5]]
        if not rewritten:
            rewritten = [
                f"围绕{target_role or '目标岗位'}补充 2-3 段最相关经历，每段写清目标、个人动作、使用方法和结果。"
            ]

        return {
            "profile_summary": profile_summary,
            "education": ["按“学校｜专业｜学历｜时间｜相关课程/奖项”补充，优先保留与目标岗位相关的信息。"],
            "work_experience": rewritten,
            "project_experience": [
                "项目经历建议按“项目背景｜个人角色｜关键行动｜结果数据｜复盘收获”重写。"
            ],
            "skills": [
                "仅填写真实掌握的工具、证书和语言能力；未使用过的技能不要为了匹配 JD 强行添加。"
            ],
        }

    def _rewrite_bullet(self, text: str, target_role: str) -> str:
        cleaned = text.strip(" -，。；;\n")
        if not cleaned:
            return ""
        if _has_number(cleaned):
            return f"围绕{target_role or '目标岗位'}要求，{cleaned}，建议进一步补充统计口径和个人贡献。"
        return f"围绕{target_role or '目标岗位'}目标，完成“{cleaned}”相关工作，建议补充对象规模、执行方法和结果数据。"

    def _coach_interview(
        self, request: AgentRequest, target_role: str, rewritten_resume: dict[str, list[str]]
    ) -> dict[str, list[str] | str]:
        role = target_role or "目标岗位"
        self_intro = (
            f"面试官您好，我的求职方向是{role}。我过往经历中与该岗位相关的部分，"
            "主要体现在任务拆解、执行推进和结果复盘上。接下来我会重点介绍最匹配的一段经历："
            "它的背景是什么、我负责哪一部分、采取了哪些动作，以及最终产生了什么结果。"
        )
        deep_dive_questions = [
            "这段经历的背景和目标是什么？",
            "你具体负责哪一部分，团队其他人负责什么？",
            "结果数据是如何统计的，统计周期是什么？",
            "哪个动作对结果影响最大，为什么？",
            "如果重新做一次，你会如何优化？",
        ]
        answer_frameworks = [
            "项目经历：背景 → 目标 → 我的职责 → 三个关键行动 → 结果 → 复盘。",
            "转行/岗位动机：过去能力不是放弃，而是迁移到目标岗位的具体场景。",
            "失败经历：真实问题 → 原因分析 → 补救动作 → 后续机制。",
        ]
        risk_responses = [
            "如果被追问数据，先说明统计口径，再说明个人动作与结果之间的关系。",
            "如果成果属于团队，不要说成个人独立完成，要明确自己负责的模块。",
        ]
        return {
            "self_introduction": self_intro,
            "deep_dive_questions": deep_dive_questions,
            "answer_frameworks": answer_frameworks,
            "risk_responses": risk_responses,
        }

    def _main_challenge(self, request: AgentRequest, diagnosis: dict[str, Any]) -> str:
        if request.current_problem:
            return "、".join(request.current_problem)
        return diagnosis.get("problems", ["待确认"])[0]

    def _strategy_for_state(self, state: str) -> str:
        strategies = {
            "fresh_graduate": "优先放大实习、项目、课程和工具能力，避免空泛自我评价。",
            "career_change": "先提炼可迁移能力，再用相关项目或作品证明新岗位匹配度。",
            "blank_resume": "先采集素材并生成初版结构，再逐段补充量化结果。",
            "no_interview_callback": "重点做 JD 匹配和关键词重排，强化招聘方能快速识别的证据。",
            "interview_preparation": "围绕简历逐段准备 STAR 讲述、数据口径和风险问题应对。",
            "executive": "从执行动作升级到业务结果、团队管理、资源协调和组织沉淀。",
            "experienced": "将岗位职责改写为项目成果，突出业务影响和个人贡献。",
        }
        return strategies.get(state, "先确认目标岗位和核心素材，再进入诊断与改写。")

    def _next_steps(self, request: AgentRequest, diagnosis: dict[str, Any]) -> list[str]:
        steps = [
            "确认目标岗位和目标行业，避免一份简历覆盖所有方向。",
            "逐条核对简历中的数据真实性、统计口径和个人职责边界。",
        ]
        if not request.resume_text:
            steps.insert(0, "补充完整简历文本，便于做逐段诊断和精修。")
        if diagnosis.get("score", 0) < 75:
            steps.append("优先处理诊断中的前三项问题，再生成最终投递版本。")
        steps.append("基于最终简历进行至少一轮面试深挖问答演练。")
        return steps


def analyze_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Convenience function for integrations."""

    return ResumeGrowthAdvisor().analyze(payload)


def _extract_keywords(text: str) -> list[str]:
    if not text:
        return []
    known_terms = sorted({term for terms in ROLE_KEYWORDS.values() for term in terms}, key=len, reverse=True)
    return [term for term in known_terms if term.lower() in text.lower()]


def _sentence_candidates(text: str) -> list[str]:
    if not text:
        return []
    pieces = re.split(r"[\n。；;]+", text)
    return [piece.strip(" -，,") for piece in pieces if len(piece.strip()) >= 4]


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d|一|二|三|四|五|六|七|八|九|十|百|千|万", text))


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _bullet_lines(title: str, items: list[str]) -> list[str]:
    lines = [f"### {title}"]
    lines.extend([f"- {item}" for item in items] or ["- 待补充"])
    return lines
