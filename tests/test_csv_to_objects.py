import unittest

from bin.csv_to_objects import clean_csv, convert_csv_to_objects

def create_car(make, model, engine, hp):
    return {
        "Make": make,
        "Model": model,
        "Engine": engine,
        "HP": hp
    }


class TestCsvToObjects(unittest.TestCase):
    def test_standard_csv(self):
        filepath = 'tests/testdata/test_standard_csv.csv'
        expected_objects = [
            create_car("Ford", "Fusion", "1.5t", "181"),
            create_car("Mazda", "6", "2.5na", "184"),
            create_car("Subaru", "Forester", "2.5na", "170")
        ]

        # Get the file
        csv_parsed_objects = convert_csv_to_objects(filepath, clean=False)

        # Assert they're equal
        for i, csv_parsed_object in enumerate(csv_parsed_objects):
            self.assertDictEqual(csv_parsed_object, expected_objects[i])

    def test_clean_html_csv_simple(self):
        input_filepath = 'tests/testdata/test_clean_html_simple_input.csv'
        expected_ouput_filepath = 'tests/testdata/test_clean_html_simple_output.csv'

        # clean the CSV, which creates a temporary file
        cleaned_csv_filepath = clean_csv(input_filepath)

        try:
            # Try to open the expected (correct) file
            expected_file = open(expected_ouput_filepath, "r")
            try:
                # Try to open the actual (cleaned) file
                actual_file = open(cleaned_csv_filepath, "r")

                try:
                    # Get the text from each file to compare
                    expected_text = expected_file.read()
                    actual_text = actual_file.read()

                    # Assert that the text from each is
                    self.assertEqual(expected_text, actual_text)
                finally:
                    actual_file.close()

            except FileNotFoundError as e:
                print("File Not Found: " + e.__str__())
            finally:
                expected_file.close()

        except FileNotFoundError as e:
            print("File Not Found: " + e.__str__())
        


if __name__ == '__main__':
    unittest.main()