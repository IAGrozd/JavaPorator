import unittest
from converter.scanner import JavaScanner  # Предполагаме, че скенерът живее в src/scanner.py

class TestJavaScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = JavaScanner()

    # EXTRACT CLASS VARIABLES

    def test_extract_class_variables_valid(self):
        code = [
            "class Player {",
            "hp = 100",
            "name",
            "def attack(self): {",
            "damage = 10",
            "}",
            "}"
        ]
        self.scanner._extract_class_variables(code)
        self.assertEqual(self.scanner.class_vars, {"hp", "name"})

    def test_extract_class_variables_invalid_identifier(self):
        code = [
            "class Player {",
            "123invalid = 5",
            "}"
        ]
        with self.assertRaises(ValueError):
            self.scanner._extract_class_variables(code)

# OPEN AND CLOSE SCOPE MANAGEMENT

    def test_manage_scope_closing_success(self):
        local_scopes = [{"a"}, {"b"}]
        self.scanner._manage_scope_closing(1, local_scopes)
        self.assertEqual(local_scopes, [{"a"}])

    def test_manage_scope_closing_unmatched_brace(self):
        local_scopes = []
        with self.assertRaises(ValueError) as context:
            self.scanner._manage_scope_closing(1, local_scopes)
        self.assertIn("Unmatched closing brace", str(context.exception))

    def test_collect_current_locals(self):
        local_scopes = [{"damage", "hp"}, {"bonus"}, {"x"}]
        result = self.scanner._collect_current_locals(local_scopes)
        self.assertEqual(result, {"damage", "hp", "bonus", "x"})

    # EXTRACT NEW LOCALS AND PARAMETERS

    def test_extract_new_locals_from_def(self):
        clean_line = "def attack(self, damage, target):"
        result = self.scanner._extract_new_locals(clean_line, inside_method=False, original_line=clean_line)
        self.assertEqual(result, {"damage", "target"})

    def test_extract_new_locals_from_assignment_inside_method(self):
        clean_line = "x = 5"
        result = self.scanner._extract_new_locals(clean_line, inside_method=True, original_line=clean_line)
        self.assertEqual(result, {"x"})

    def test_extract_new_locals_ignore_outside_method(self):
        clean_line = "hp = 100"
        result = self.scanner._extract_new_locals(clean_line, inside_method=False, original_line=clean_line)
        self.assertEqual(result, set())
        
    # PUTTING SELF IN FRONT OF CLASS VARIABLES

    def test_transform_variables_this_to_self(self):
        self.scanner.class_vars = {"hp"}
        clean_line = "this.hp = hp"
        result = self.scanner._transform_variables(clean_line, inside_method=True, current_locals=set(), new_locals={"hp"})
        self.assertEqual(result, "self.hp = hp")

    def test_transform_variables_auto_self_injection(self):
        self.scanner.class_vars = {"hp"}
        clean_line = "hp -= 10"
        result = self.scanner._transform_variables(clean_line, inside_method=True, current_locals=set(), new_locals=set())
        self.assertEqual(result, "self.hp -= 10")

    def test_transform_variables_shadowed_by_local(self):
        self.scanner.class_vars = {"hp"}
        clean_line = "hp = 5"
        result = self.scanner._transform_variables(clean_line, inside_method=True, current_locals={"hp"}, new_locals=set())
        self.assertEqual(result, "hp = 5")

    def test_transform_variables_external_object_property(self):
        self.scanner.class_vars = {"hp"}
        clean_line = "enemy.hp -= 10"
        result = self.scanner._transform_variables(clean_line, inside_method=True, current_locals=set(), new_locals=set())
        self.assertEqual(result, "enemy.hp -= 10")

    # IDENTATION

    def test_compute_indentation_class_level(self):
        result = self.scanner._compute_indentation("class Player:", [])
        self.assertEqual(result, "class Player:")

    def test_compute_indentation_method_level(self):
        result = self.scanner._compute_indentation("def attack(self):", [set()])
        self.assertEqual(result, "    def attack(self):")

    def test_compute_indentation_inside_method(self):
        result = self.scanner._compute_indentation("x = 5", [set(), set()])
        self.assertEqual(result, "        x = 5")

    # INTEGRATION

    def test_full_transform_integration(self):
        input_code = (
            "class Player: {\n"
            "    hp = 100\n"
            "    def __init__(self, hp): {\n"
            "        this.hp = hp\n"
            "    }\n"
            "    def take_damage(self, damage): {\n"
            "        if damage > 0: {\n"
            "            hp -= damage\n"
            "        }\n"
            "    }\n"
            "}"
        )
        
        expected_output = (
            "class Player:\n"
            "    hp = 100\n"
            "    def __init__(self, hp):\n"
            "        self.hp = hp\n"
            "    def take_damage(self, damage):\n"
            "        if damage > 0:\n"
            "            self.hp -= damage"
        )
        
        result = self.scanner.transform(input_code)
        self.assertEqual(result.strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()