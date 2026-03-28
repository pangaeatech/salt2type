# pylint: disable=C0303,C0301,C0114,C0413,W0611,C0116

import os
from xml.etree import ElementTree
from unittest.mock import patch, mock_open, MagicMock
import unittest

from src.types import *
from src.util import *


class TestUtil(unittest.TestCase):
    """Unit Tests for utils"""

    @patch("src.util.to_type")
    def test_clean_line(self, mock_to_type):
        # Mocking to_type to return a fixed type based on its input
        mock_to_type.side_effect = lambda x: f"TypeOf_{x}"

        # Arrange
        line = "someMethod(param1).call(null, param2)"
        line_generic_method = "anotherMethod(param3).call(param4)"

        # Act
        result1 = clean_line(line)
        result2 = clean_line(line_generic_method)

        # Assert
        # Verify that to_type is called with expected arguments
        mock_to_type.assert_any_call("param1")  # Called once with param1
        mock_to_type.assert_any_call("param3")  # Called once with param3

        # Verify transformed line output
        expected_result1 = "someMethod<TypeOf_param1>(param2)"
        expected_result2 = "anotherMethod<TypeOf_param3>(param4)"

        self.assertEqual(result1, expected_result1)
        self.assertEqual(result2, expected_result2)

    def test_basic_types(self):
        # Test simple type mappings
        self.assertEqual(to_type("bool"), "boolean")
        self.assertEqual(to_type("int"), "number")
        self.assertEqual(to_type("float"), "number")
        self.assertEqual(to_type("JsDate"), "Date")
        self.assertEqual(to_type("DateTime"), "Date")
        self.assertEqual(to_type("Object"), "any")
        self.assertEqual(to_type("jQueryObject"), "JQuery | undefined")
        self.assertEqual(to_type("dynamic"), "any")

    def test_collections(self):
        # Test collection type mappings
        self.assertEqual(to_type("IList<string>"), "Array<string>")
        self.assertEqual(to_type("ss.IEnumerable<int>"), "Array<number>")
        self.assertEqual(to_type("ss.JsDictionary<string, int>"), "Record<string, number>")
        self.assertEqual(to_type("JsDictionary"), "Record<string,unknown>")

    def test_optional_types(self):
        # Test types with optional symbol (?)
        self.assertEqual(to_type("int?"), "number | undefined")
        self.assertEqual(to_type("JsDate?"), "Date | undefined")

    def test_delegate_and_dynamic(self):
        # Test mappings for delegate and dynamic types
        self.assertEqual(to_type("Delegate"), "Action<void> | undefined")
        self.assertEqual(to_type("delegate int"), "Action<number> | undefined")
        self.assertEqual(to_type("dynamic"), "any")

    def test_complex_types(self):
        # Test types with complex structures
        self.assertEqual(to_type("List<DateTime[]>"), "Array<Date[]>")
        self.assertEqual(to_type("ss.Dictionary<string, List<Date>>"), "Record<string, Array<Date>>")

    def test_keywords(self):
        # Test types with TypeScript keywords
        self.assertEqual(to_type("readonly int"), "number")
        self.assertEqual(to_type("sealed override bool"), "boolean")

    def test_bypass_conditions(self):
        # Test types that should return as-is without modification
        self.assertEqual(to_type("any"), "any")
        self.assertEqual(to_type("unknown"), "unknown")
        self.assertEqual(to_type("boolean"), "boolean")
        self.assertEqual(to_type("Array<number>"), "Array<number>")
        self.assertEqual(to_type("Record<string, Date>"), "Record<string, Date>")

    @patch("src.util.clean_line")
    def test_to_body(self, mock_clean_line):
        # Arrange
        curr_class = ClassDef("ns", "MyClass", None, [], [], [], "currClassVar", None, [])
        lines = ["currClassVar.method1();", "otherMethod(currClassVar);"]

        # Mock clean_line to just return the line as-is for simplicity
        mock_clean_line.side_effect = lambda line: line

        # Act
        result = to_body(curr_class, lines)

        # Assert
        expected_result = ["MyClass.method1();", "otherMethod(MyClass);"]
        self.assertEqual(result, expected_result)

        # Verify clean_line was called with the correctly replaced lines
        mock_clean_line.assert_any_call("MyClass.method1();")
        mock_clean_line.assert_any_call("otherMethod(MyClass);")

    def test_re_find_index_found(self):
        # Arrange
        lines = ["line1", "line2 matching", "line3"]
        pattern = r".*matching"

        # Act
        result = re_find_index(pattern, lines, start=0)

        # Assert
        self.assertEqual(result, 1)  # "line2 matching" is at index 1

    def test_re_find_index_not_found(self):
        # Arrange
        lines = ["line1", "line2", "line3"]
        pattern = r"missing_pattern"

        # Act & Assert
        with self.assertRaises(Exception) as context:
            re_find_index(pattern, lines, start=0)

        self.assertIn("Could not find match for", str(context.exception))

    def test_to_text_with_text(self):
        # Arrange
        xml_string = "<root>   Some text   <tag>more text</tag>   </root>"
        node = ElementTree.fromstring(xml_string)

        # Act
        result = to_text(node)

        # Assert
        self.assertEqual(result, "Some text   more text")

    def test_to_text_empty_node(self):
        # Arrange
        node = ElementTree.Element("empty")

        # Act
        result = to_text(node)

        # Assert
        self.assertEqual(result, "")

    def test_to_text_none_node(self):
        # Act
        result = to_text(None)

        # Assert
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
