import unittest

from bin.xlsx_to_objects import convert_xlsx_to_objects, clean_json


def create_car(make, model, engine, hp):
    return {
        "Make": make,
        "Model": model,
        "Engine": engine,
        "HP": hp
    }


class TestXlsxToObjects(unittest.TestCase):
    def test_standard_xlsx(self):
        filepath = 'tests/testdata/test_standard_xlsx.xlsx'
        expected_objects = [
            create_car("Ford", "Fusion", "1.5t", 181),
            create_car("Mazda", 6, "2.5na", 184),
            create_car("Subaru", "Forester", "2.5na", 170)
        ]

        # Get the file
        xlsx_parsed_objects = convert_xlsx_to_objects(filepath)

        # Assert they're equal
        for i, xlsx_parsed_object in enumerate(xlsx_parsed_objects):
            self.assertDictEqual(xlsx_parsed_object, expected_objects[i])

    def test_empty_cells_xlsx(self):
        filepath = 'tests/testdata/test_empty_cells_xlsx.xlsx'
        expected_objects = [
            create_car("Ford", "Fusion", "1.5t", ""),
            create_car("Mazda", 6, "2.5na", 184),
            create_car("Subaru", "", "2.5na", 170)
        ]

        # Get the file
        xlsx_parsed_objects = convert_xlsx_to_objects(filepath)

        # Assert they're equal
        for i, xlsx_parsed_object in enumerate(xlsx_parsed_objects):
            self.assertDictEqual(xlsx_parsed_object, expected_objects[i])

    def test_clean_html_xlsx_simple(self):
        input_filepath = 'tests/testdata/test_clean_html_simple_input.xlsx'
        expected_objects = [
            create_car("Ford", "Fusion", "1.5t", 181),
            create_car("Mazda", 6, "2.5na", 184),
            create_car("Subaru", "Forester", "2.5na", 170)
        ]

        # Convert the XLSX
        xlsx_parsed_objects = convert_xlsx_to_objects(
            input_filepath)

        # Clean the parsed JSON
        cleaned_xlsx_parsed_objects = clean_json(xlsx_parsed_objects)

        # Assert they're equal
        for i, cleaned_xlsx_parsed_object in enumerate(cleaned_xlsx_parsed_objects):
            self.assertDictEqual(
                cleaned_xlsx_parsed_object, expected_objects[i])

    def test_clean_html_xlsx_complex(self):
        input_filepath = 'tests/testdata/test_clean_html_complex_input.xlsx'

        expected_objects = [
            create_car("Ford", "Fusion", "1.5t", 181),
            create_car("Mazda", 6, "2.5na", 184),
            create_car("Subaru", "Forester   ", "2.5na", 170)
        ]

        # Convert the XLSX
        xlsx_parsed_objects = convert_xlsx_to_objects(
            input_filepath)

        # Clean parsed JSON
        cleaned_xlsx_parsed_objects = clean_json(xlsx_parsed_objects)

        # Assert they're equal
        for i, cleaned_xlsx_parsed_object in enumerate(cleaned_xlsx_parsed_objects):
            self.assertDictEqual(
                cleaned_xlsx_parsed_object, expected_objects[i])


if __name__ == '__main__':
    unittest.main()