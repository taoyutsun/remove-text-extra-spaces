import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parent.parent / "remove_text_extra_spaces_v3.py"
)
SPEC = importlib.util.spec_from_file_location("remove_text_extra_spaces_v3", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CleanTextUltimateTests(unittest.TestCase):
    def test_remove_spaces_between_chinese_characters(self) -> None:
        self.assertEqual(MODULE.clean_text_ultimate("我 是 一 個 學 生"), "我是一個學生")

    def test_fix_full_width_punctuation_spacing(self) -> None:
        self.assertEqual(
            MODULE.clean_text_ultimate("這 是 ， 一個 測試 ！"),
            "這是，一個測試！",
        )

    def test_fix_half_width_punctuation_in_english_text(self) -> None:
        self.assertEqual(
            MODULE.clean_text_ultimate("Hello,world"),
            "Hello, world",
        )

    def test_fix_ne_particle_without_breaking_question_mark(self) -> None:
        self.assertEqual(MODULE.clean_text_ultimate("他說呢他會來"), "他說呢，他會來")
        self.assertEqual(MODULE.clean_text_ultimate("你呢？"), "你呢？")

    def test_keep_decimal_and_abbreviation_intact(self) -> None:
        self.assertEqual(
            MODULE.clean_text_ultimate("版本 3.14 很穩定"),
            "版本 3.14 很穩定",
        )
        self.assertEqual(
            MODULE.clean_text_ultimate("U.S.A. is a country."),
            "U.S.A. is a country.",
        )

    def test_preserve_paragraph_breaks(self) -> None:
        options = MODULE.CleanOptions(preserve_paragraph_breaks=True)
        self.assertEqual(
            MODULE.clean_text_ultimate("第一段 \n內容\n\n第二段 文字", options),
            "第一段內容\n\n第二段文字",
        )

    def test_disable_ascii_punctuation_rule(self) -> None:
        options = MODULE.CleanOptions(fix_ascii_punctuation=False)
        self.assertEqual(
            MODULE.clean_text_ultimate("Hello,world", options),
            "Hello,world",
        )

    def test_build_output_path(self) -> None:
        output_path = MODULE.build_output_path(Path("sample.txt"))
        self.assertEqual(str(output_path), "sample_cleaned.txt")


if __name__ == "__main__":
    unittest.main()
