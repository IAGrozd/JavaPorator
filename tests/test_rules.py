import unittest
import re
from converter.rules import RULES


class TestJavaToPythonRules(unittest.TestCase):

    def apply_rules(self, java_code: str) -> str:
        """Helpers method to apply all rules to a given Java code snippet."""
        result = java_code
        for rule in RULES:
            result = re.sub(rule.pattern, rule.replacement, result)
        return result

    # COMMENTS
    def test_oneline_comment(self):
        self.assertEqual(self.apply_rules("// this is a comment"), "# this is a comment")

    def test_multiline_comment(self):
        self.assertEqual(self.apply_rules("/*\n * line 1\n * line 2\n */").strip(), "#\n# line 1\n# line 2\n#")

    # IMPORTS
    def test_package_removal(self):
        self.assertEqual(self.apply_rules("package com.example.app;").strip(), "")

    def test_import_declaration(self):
        self.assertEqual(self.apply_rules("import java.util.List;").strip(), "import List")

    # CLASSES
    def test_inheritance_class(self):
        self.assertEqual(self.apply_rules("public class Car extends Vehicle").strip(), "class Car(Vehicle):")

    def test_class_with_interface(self):
        self.assertEqual(self.apply_rules("private class Dog implements Animal").strip(), "class Dog(Animal):")

    def test_simple_class(self):
        self.assertEqual(self.apply_rules("protected class Player").strip(), "class Player:")

    # STANDARD LIBRARY
    def test_system_out_println(self):
        self.assertEqual(self.apply_rules('System.out.println("Hello");').strip(), 'print("Hello")')

    def test_system_out_print(self):
        self.assertEqual(self.apply_rules('System.out.print("Hi");').strip(), 'print("Hi", end="")')

    def test_equals_conversion(self):
        self.assertEqual(self.apply_rules('str1.equals(str2)').strip(), 'str1 == str2')

    def test_length_conversion(self):
        self.assertEqual(self.apply_rules('text.length()').strip(), 'len(text)')

    def test_size_conversion(self):
        self.assertEqual(self.apply_rules('items.size()').strip(), 'len(items)')

    # METHODS AND INITIALIZERS
    def test_method_declaration(self):
        self.assertEqual(self.apply_rules('public void sampleMethod(int a)').strip(), 'def sampleMethod(a):')

    def test_constructor_init(self):
        self.assertEqual(self.apply_rules('public Player(String name)').strip(), 'def __init__(self, name):')

    # DETYPIFICATION
    def test_base_type_removal(self):
        self.assertEqual(self.apply_rules("int count = 10;").strip(), "count = 10")

    def test_generics_removal(self):
        self.assertEqual(self.apply_rules("List<String> names;").strip(), "names")

    def test_array_removal(self):
        self.assertEqual(self.apply_rules("int[] scores;").strip(), "scores")

    # MODIFIERS
    def test_new_keyword_removal(self):
        self.assertEqual(self.apply_rules("new Player()").strip(), "Player()")

    # CONTROL FLOW
    def test_standard_for_loop_to_range(self):
        self.assertEqual(self.apply_rules("for (int i = 0; i < 10; i++)").strip(), "for i in range(10):")

    def test_if_statement_syntax(self):
        self.assertEqual(self.apply_rules("if (x > 5)").strip(), "if x > 5:")

    def test_foreach_loop(self):
        self.assertEqual(self.apply_rules("for (String item : items)").strip(), "for item in items:")

    def test_else_if_conversion(self):
        self.assertEqual(self.apply_rules("else if (score >= 90)").strip(), "elif score >= 90:")

    def test_else_conversion(self):
        self.assertEqual(self.apply_rules("else").strip(), "else:")

    def test_while_loop(self):
        self.assertEqual(self.apply_rules("while (isRunning)").strip(), "while isRunning:")

    # BOOL OPERATORS
    def test_and_operator(self):
        self.assertEqual(self.apply_rules("a && b").strip(), "a and b")

    def test_or_operator(self):
        self.assertEqual(self.apply_rules("a || b").strip(), "a or b")

    def test_not_operator(self):
        self.assertEqual(self.apply_rules("!flag").strip(), "not flag")

    def test_true_literal(self):
        self.assertEqual(self.apply_rules("true").strip(), "True")

    def test_false_literal(self):
        self.assertEqual(self.apply_rules("false").strip(), "False")

    def test_null_literal(self):
        self.assertEqual(self.apply_rules("null").strip(), "None")


if __name__ == "__main__":
    unittest.main()