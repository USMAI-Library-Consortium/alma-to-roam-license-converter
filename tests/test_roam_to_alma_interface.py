import unittest

from bin.roam_to_alma_interface import RoamAlmaInterface
from bin.xlsx_to_objects import clean_json, convert_xlsx_to_objects
import json
from datetime import datetime
from pandas import Timestamp
from config.config_test import Mappings, Settings


class TestConvertRoamTermToAlma(unittest.TestCase):

    def create_expected_result(self, data):
        """Create a correctly formatted expected result"""
        result = []

        # Append both or either of the term codes & their values
        if "Main Term Code" in data:
            result.append({
                "term_code": data["Main Term Code"],
                "term_value": data["Main Term Value"]
            })
        if "Notes Term Code" in data:
            result.append({
                "term_code": data["Notes Term Code"],
                "term_value": data["Notes Term Value"]
            })

        return result

    def create_roam_term_data(self, data):
        return {
            "Name": data["Name"],
            "License Qualifiers": data["License Qualifiers"],
            "Allowed": data["Allowed"],
            "Description": data["Description"]
        }

    def test_convert_normal_roam_term_to_alma(self):
        """Test Correct ROAM license terms; that they convert correctly to Alma format"""

        # An array of roam term data, followed by the expected result
        # roam: Name, Allowed (yes, no, n/a), License Qualifiers, Description
        # alma: Main License Term Code, Main License Term Value, Notes License Term Code, Notes License Term Value
        test_data_set = [
            {"roam": {"Name": "Printing", "Allowed": "yes", "License Qualifiers": "", "Description": "Reasonable amount by needed parties"},
             "alma": {"Main Term Code": "PRINTCOPY", "Main Term Value": "PERMITTED", "Notes Term Code": "PRINTCOPYN", "Notes Term Value": "Reasonable amount by needed parties"}},
            {"roam": {"Name": "Copying", "Allowed": "n/a", "License Qualifiers": "On Premesis", "Description": "Reasonable amount by needed parties"},
             "alma": {"Main Term Code": "DIGCOPY", "Main Term Value": "SILENT", "Notes Term Code": "DIGCOPYN", "Notes Term Value": "On Premesis; Reasonable amount by needed parties"}},
            {"roam": {"Name": "Interlibrary Loan (ILL)", "Allowed": "no", "License Qualifiers": "", "Description": "The license states you cannot transfer this data to other libraries."},
             "alma": {"Main Term Code": "ILLELEC", "Main Term Value": "PROHIBITED", "Notes Term Code": "ILLN", "Notes Term Value": "The license states you cannot transfer this data to other libraries."}},
            {"roam": {"Name": "ADA Accessibility", "Allowed": "yes", "License Qualifiers": "", "Description": "Accessibility terms available on our website at..."},
             "alma": {"Main Term Code": "ACCESSIBILITY", "Main Term Value": "YES"}},
            {"roam": {"Name": "ADA Accessibility", "Allowed": "n/a", "License Qualifiers": "", "Description": ""},
             "alma": {"Main Term Code": "ACCESSIBILITY", "Main Term Value": "NO"}},
            {"roam": {"Name": "Archiving", "Allowed": "no", "License Qualifiers": "", "Description": "We do not allow archiving of any materials."},
             "alma": {"Main Term Code": "ARCHIVE", "Main Term Value": "NO", "Notes Term Code": "ARCHIVEN", "Notes Term Value": "We do not allow archiving of any materials."}},
            {"roam": {"Name": "Archiving", "Allowed": "n/a", "License Qualifiers": "", "Description": ""},
             "alma": {"Main Term Code": "ARCHIVE", "Main Term Value": "YES"}},
            {"roam": {"Name": "Authentication", "Allowed": "yes", "License Qualifiers": "Walk-ins or IP-based", "Description": "IP users or walk-ins allowed."},
             "alma": {"Notes Term Code": "AUTHUSERDEF", "Notes Term Value": "Walk-ins or IP-based; IP users or walk-ins allowed."}},
            {"roam": {"Name": "Cancellation Policy", "Allowed": "yes", "License Qualifiers": "", "Description": "We must know 60 days before cancellation"},
             "alma": {"Notes Term Code": "TERMREQS", "Notes Term Value": "We must know 60 days before cancellation"}},
            {"roam": {"Name": "Course Packs", "Allowed": "yes", "License Qualifiers": "", "Description": "You are allowed to reproduce electronic notes for course reserves."},
             "alma": {"Main Term Code": "COURSEPACKELEC", "Main Term Value": "PERMITTED", "Notes Term Code": "COURSEPACKN", "Notes Term Value": "You are allowed to reproduce electronic notes for course reserves."}},
            {"roam": {"Name": "Course Reserves", "Allowed": "yes", "License Qualifiers": "", "Description": "Course reserve use information can be found at our link: ..."},
             "alma": {"Main Term Code": "COURSERES", "Main Term Value": "PERMITTED", "Notes Term Code": "COURSERESNOTE", "Notes Term Value": "Course reserve use information can be found at our link: ..."}},
            {"roam": {"Name": "Downloading/Saving", "Allowed": "n/a", "License Qualifiers": "", "Description": "Fair Use Prevails."},
             "alma": {"Main Term Code": "DIGCOPY", "Main Term Value": "SILENT", "Notes Term Code": "DIGCOPYN", "Notes Term Value": "Fair Use Prevails."}},
            {"roam": {"Name": "Perpetual Access/Post Cancellation Rights", "Allowed": "no", "License Qualifiers": "", "Description": "Cease use upon cancellation."},
             "alma": {"Main Term Code": "PERPETUAL", "Main Term Value": "NO", "Notes Term Code": "PERPETUALN", "Notes Term Value": "Cease use upon cancellation."}},
            {"roam": {"Name": "Public Performance", "Allowed": "yes", "License Qualifiers": "CRED", "Description": "Please Give Credit."},
             "alma": {"Main Term Code": "OTHERUSERSTRN", "Main Term Value": "Public Performance: CRED; Please Give Credit."}},
            {"roam": {"Name": "Sharing/Linking", "Allowed": "yes", "License Qualifiers": "", "Description": "Please see sharing/linking policy at www.link.com"},
             "alma": {"Main Term Code": "ELECLINK", "Main Term Value": "PERMITTED", "Notes Term Code": "ELECLINKNOTE", "Notes Term Value": "Please see sharing/linking policy at www.link.com"}},
            {"roam": {"Name": "Sharing/Linking", "Allowed": "n/a", "License Qualifiers": "", "Description": "Please see sharing/linking policy at www.link.com"},
             "alma": {"Main Term Code": "ELECLINK", "Main Term Value": "SILENT", "Notes Term Code": "ELECLINKNOTE", "Notes Term Value": "Please see sharing/linking policy at www.link.com"}},
            {"roam": {"Name": "Simultaneous Users", "Allowed": "yes", "License Qualifiers": "Unlimited", "Description": "Terms do not specify number of simultaneous users."},
             "alma": {"Main Term Code": "CONCURUSERN", "Main Term Value": "Concurrent Users Permitted", "Notes Term Code": "CONCURUSERN", "Notes Term Value": "Unlimited; Terms do not specify number of simultaneous users."}},
            {"roam": {"Name": "Usage Statistics", "Allowed": "yes", "License Qualifiers": "", "Description": "Counter Compliant will be provided."},
             "alma": {"Notes Term Code": "OTHERUSERSTRN", "Notes Term Value": "Usage Statistics: Counter Compliant will be provided."}},
        ]

        alma_interface = RoamAlmaInterface(
            [], [], Mappings, Settings)

        for test_data in test_data_set:
            correct_term_data = self.create_roam_term_data(
                test_data["roam"])
            expected_result = self.create_expected_result(
                test_data["alma"])

            actual_result = alma_interface._RoamAlmaInterface__convert_license_term_to_alma(
                correct_term_data["Name"], correct_term_data["License Qualifiers"], correct_term_data["Allowed"], correct_term_data['Description'])

            for idx, actual_term in enumerate(actual_result):
                self.assertDictEqual(actual_term, expected_result[idx])


class TestConvertRoamObjectToAlmaJson(unittest.TestCase):

    def test_convert_normal_roam_to_alma_json(self):
        # Filepath of Excel to convert from
        filepath = "tests/testdata/simple_roam_test.xlsx"

        expected_roam_object = {
            "license_details": {
                "ownered_entity": {
                    "created_by": "USMAI ROAM to Alma Converter"
                },
                "license_code": "",
                "license_name": "Wiley",
                "license_status": "ACTIVE",
                "type": "LICENSE",
                "start_date": "20200512",
                "end_date": "20200724",
                "review_status": "ACCEPTED",
                "URI": "www.google.com"
            },
            "term_list": [
                {
                    "term_code": "DIGCOPY",
                    "term_value": "PERMITTED"
                },
                {
                    "term_code": "DIGCOPYN",
                    "term_value": "On Premesis; Reasonable amount by needed parties"
                }
            ],
            "note_list": [
                {
                    "content": "License Summary: A summary"
                },
                {
                    "content": "License Notes: Here's the note!"
                },
                {
                    "content": "Publisher: Wiley Electronics"
                }
            ]
        }

        # Parse the ROAM object
        roam_object = convert_xlsx_to_objects(filepath)[0]

        # Convert the ROAM object date
        roam_object = RoamAlmaInterface.convert_objects_date_to_alma(
            [roam_object], ["Start Date", "End Date"])[0]

        # Clean the ROAM object
        roam_object = clean_json(roam_object)

        alma_interface = RoamAlmaInterface(
            [], [], Mappings, Settings)

        # Parse the ROAM object
        converted_roam_object = alma_interface._RoamAlmaInterface__convert_roam_license_terms_object(
            roam_object)

        # Convert to string, so that we can compare the dictionaries deeply
        string_of_converted_object = json.dumps(
            converted_roam_object, sort_keys=True)
        string_of_expected_object = json.dumps(
            expected_roam_object, sort_keys=True)

        self.maxDiff = None

        self.assertEqual(string_of_converted_object,
                         string_of_expected_object)


class TestTimestampConversion(unittest.TestCase):

    def test_convert_datetime_to_alma(self):
        """Test that the RoamAlmaInterface can transform datetimes to a string"""

        object_to_convert = {
            "Name": "An Object",
            "Start Date": datetime(2022, 2, 25),
        }

        expected_object = {
            "Name": "An Object",
            "Start Date": "20220225"
        }

        converted_object = RoamAlmaInterface.convert_object_date_to_alma(
            object_to_convert, ["Start Date"])

        self.assertDictEqual(converted_object, expected_object)

    def test_convert_timestamp_to_alma(self):
        """Test that the RoamAlmaInterface can transform timestamp to a string"""

        object_to_convert = {
            "Name": "An Object",
            "Start Date": Timestamp(year=2022, month=2, day=25, hour=12, minute=12),
        }

        expected_object = {
            "Name": "An Object",
            "Start Date": "20220225"
        }

        converted_object = RoamAlmaInterface.convert_object_date_to_alma(
            object_to_convert, ["Start Date"])

        self.assertDictEqual(converted_object, expected_object)

    def test_convert_datetime_and_timestamp_to_alma(self):
        """Test that the RoamAlmaInterface can transform timestamps and datetimes to a string"""

        object_to_convert = {
            "Name": "An Object",
            "Start Date": Timestamp(year=2022, month=2, day=25, hour=12, minute=12),
            "End Date": datetime(2024, 5, 27)
        }

        expected_object = {
            "Name": "An Object",
            "Start Date": "20220225",
            "End Date": "20240527"
        }

        converted_object = RoamAlmaInterface.convert_object_date_to_alma(
            object_to_convert, ["Start Date", "End Date"])

        self.assertDictEqual(converted_object, expected_object)

    def test_convert_multiple_objects_empty_property(self):
        to_convert = [
            {
                "Name": "An Object",
                "Start Date": Timestamp(year=2022, month=2, day=25, hour=12, minute=12),
                "End Date": datetime(2024, 5, 27)
            }, {
                "Name": "An Object",
                "Start Date": Timestamp(year=2022, month=2, day=25, hour=12, minute=12),
                "End Date": ""
            }
        ]

        expected_results = [
            {
                "Name": "An Object",
                "Start Date": "20220225",
                "End Date": "20240527"
            },
            {
                "Name": "An Object",
                "Start Date": "20220225",
                "End Date": ""
            }
        ]

        actual_results = RoamAlmaInterface.convert_objects_date_to_alma(
            to_convert, ["Start Date", "End Date"])

        for idx, result in enumerate(actual_results):
            self.assertDictEqual(result, expected_results[idx])