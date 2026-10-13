import tempfile
import unittest
from pathlib import Path

from score import score
from validate import validate


class ToolTests(unittest.TestCase):
    def test_invalid_fragment_is_located(self):
        record = {"claim_id": "x", "label": "supported", "source_id": "S",
                  "fragment_id": "missing", "rationale": "r", "limitation": "l", "suggested_wording": "w"}
        self.assertIn("fragment_id: not in indicated source", validate(record, {"x"}, {"S": {"real"}}))

    def test_false_release_and_missing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = Path(temp)
            (outputs / "a.json").write_text(
                '{"claim_id":"a","label":"supported","source_id":"S","fragment_id":"f",'
                '"rationale":"r","limitation":"l","suggested_wording":"w"}', encoding="utf-8")
            result = score([{"claim_id": "a"}, {"claim_id": "b"}],
                           {"a": "overstated", "b": "supported"}, outputs, {"S": {"f"}})
            self.assertEqual(result["false_release"], 1)
            self.assertEqual(result["valid_outputs"], 1)
            self.assertEqual(result["label_correct"], 0)
            self.assertEqual(result["rows"][1]["predicted"], "INVALID")
            self.assertIsNone(result["location_correct"])


if __name__ == "__main__":
    unittest.main()
