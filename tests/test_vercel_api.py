import unittest

from api.analyze import analyze_payload


class VercelApiTests(unittest.TestCase):
    def test_analyze_payload_returns_markdown_and_result(self):
        response = analyze_payload({"target_role": "用户运营", "experience_materials": "维护20个社群。"})

        self.assertIn("markdown", response)
        self.assertIn("result", response)
        self.assertIn("## 一、整体判断", response["markdown"])
        self.assertEqual(response["result"]["profile_analysis"]["target_role"], "用户运营")


if __name__ == "__main__":
    unittest.main()
