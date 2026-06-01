import json
import subprocess
import sys
import unittest

from resume_agent import ResumeGrowthAdvisor, analyze_request


class ResumeGrowthAdvisorTests(unittest.TestCase):
    def test_analyze_detects_role_and_generates_sections(self):
        result = analyze_request(
            {
                "user_type": "fresh_graduate",
                "target_role": "用户运营",
                "experience_materials": "维护20个社群，每个约200人；试听课活动单场300人报名；写过15篇公众号。",
            }
        )

        self.assertEqual(result["profile_analysis"]["target_role"], "用户运营")
        self.assertEqual(result["profile_analysis"]["user_state"], "fresh_graduate")
        self.assertGreaterEqual(result["resume_diagnosis"]["score"], 0)
        self.assertIn("interview_coaching", result)
        self.assertTrue(result["rewritten_resume"]["work_experience"])

    def test_markdown_renderer_contains_required_headings(self):
        advisor = ResumeGrowthAdvisor()
        result = advisor.analyze({"target_role": "产品经理", "experience_materials": "用墨刀画原型，做用户调研80份。"})
        markdown = advisor.render_markdown(result)

        self.assertIn("## 一、整体判断", markdown)
        self.assertIn("## 四、优化后简历", markdown)
        self.assertIn("## 五、面试辅导包", markdown)

    def test_cli_json_output(self):
        payload = json.dumps({"target_role": "数据分析", "experience_materials": "使用Excel整理200条数据。"})
        completed = subprocess.run(
            [sys.executable, "-m", "resume_agent", "--format", "json"],
            input=payload,
            text=True,
            capture_output=True,
            check=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["profile_analysis"]["target_role"], "数据分析")

    def test_cli_openai_engine_without_key_exits_with_message(self):
        payload = json.dumps({"target_role": "用户运营", "experience_materials": "维护社群。"})
        completed = subprocess.run(
            [sys.executable, "-m", "resume_agent", "--engine", "openai"],
            input=payload,
            text=True,
            capture_output=True,
            env={"PYTHONPATH": "."},
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("OPENAI_API_KEY is not set", completed.stderr)


if __name__ == "__main__":
    unittest.main()
