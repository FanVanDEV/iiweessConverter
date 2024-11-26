import unittest

from main import translate, main


class MainTest(unittest.TestCase):

    def test_basic_variable(self):
        toml_data = "a = 10"
        expected_output = "10 -> a"
        
        result = translate(toml_data)
        self.assertIn(expected_output, result)

    def test_comment_handling(self):
        toml_data = "# Это комментарий\na = 10"
        expected_output = '" Это комментарий\n10 -> a'
        result = translate(toml_data)
        self.assertIn(expected_output, result)

    def test_inline_table(self):
        toml_data = "inlineTable = { a = 0 }"
        expected_output = "([\n    a : 0,\n]) -> inlineTable"
        result = translate(toml_data)
        self.assertIn(expected_output, result)

    def test_nested_dict(self):
        toml_data = "[dog.\"tamer_man\".cat]\ntype = 42"
        expected_output = ("([\n    tamer_man : ([\n        cat : ([\n            type : 42,\n        ]),\n    ]),"
                           "\n]) -> dog")
        result = translate(toml_data)
        self.assertIn(expected_output, result)

    def test_invalid_variable_name(self):
        toml_data = "1a = 10"
        with self.assertRaises(SyntaxError):
            translate(toml_data)

    def test_variable_link(self):
        toml_data = "a = 10\nb = \"?(a)\""
        expected_output = "10 -> a\n10 -> b"

        result = translate(toml_data)
        self.assertIn(expected_output, result)


if __name__ == "__main__":
    unittest.main()
