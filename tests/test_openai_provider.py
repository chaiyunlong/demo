import json
import unittest
from unittest.mock import MagicMock, patch

from resume_agent.openai_provider import OpenAIProviderError, OpenAIResponsesClient


class OpenAIProviderTests(unittest.TestCase):
    def test_requires_api_key(self):
        client = OpenAIResponsesClient(api_key=None)
        with self.assertRaises(OpenAIProviderError):
            client.generate_resume_report("system", {"target_role": "用户运营"}, "baseline")

    @patch("resume_agent.openai_provider.urllib.request.urlopen")
    def test_generate_resume_report_extracts_output_text(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"output_text": "生成报告"}).encode("utf-8")
        urlopen.return_value = response

        client = OpenAIResponsesClient(api_key="test-key", model="gpt-5.2")
        output = client.generate_resume_report("system", {"target_role": "用户运营"}, "baseline")

        self.assertEqual(output, "生成报告")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertIn("Bearer test-key", request.headers["Authorization"])
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-5.2")
        self.assertEqual(payload["input"][0]["role"], "system")


if __name__ == "__main__":
    unittest.main()
