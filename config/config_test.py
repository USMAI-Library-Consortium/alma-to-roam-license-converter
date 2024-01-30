import logging

## THIS IS THE STATE OF THE MAPPINGS PARTWAY THROUGH DEVELOPMENT. IT'S USED WITH THE
## TESTS IN ORDER TO KEEP COMPATIBILITY, as the tests were not updated to reflect the new
## mappings, only code changes in the methods shared by all configurations. 

class Settings:
    # Clean all data parsed from excel, removing HTML data and Unicode compatibility characters (/xa0, etc)
    clean = True
    # Remove newlines only works if clean=True
    remove_newline = True
    # License XSD file
    xsd_file = "config/erm_license_official.xsd"
    # License input file (can also be set with commandline)
    license_input = "input/licenses.xlsx"
    # License terms input file (can also be set with commandline)
    license_terms_input = "input/license_terms.xlsx"
    # Logging file
    logging_file = "tests/test_logs.log"
    # Logging level
    logging_level = logging.DEBUG


class Mappings:

    # PLEASE MODIFY OR ADD TO THESE IN config_prod.py !!
    term_mappings = {
        "ADA Accessibility": ["ACCESSIBILITY", ""],
        "Archiving": ["ARCHIVE", "ARCHIVEN"],
        "Authentication": ["", "AUTHUSERDEF"],
        "Cancellation Policy": ["", "TERMREQS"],
        "Copying": ["DIGCOPY", "DIGCOPYN"],
        "Course Packs": ["COURSEPACKELEC", "COURSEPACKN"],
        "Course Reserves": ["COURSERES", "COURSERESNOTE"],
        "Downloading/Saving": ["DIGCOPY", "DIGCOPYN"],
        "Interlibrary Loan (ILL)": ["ILLELEC", "ILLN"],
        "Perpetual Access/Post Cancellation Rights": ["PERPETUAL", "PERPETUALN"],
        "Printing": ["PRINTCOPY", "PRINTCOPYN"],
        "Public Performance": ["", "OTHERUSERSTRN"],
        "Sharing/Linking": ["ELECLINK", "ELECLINKNOTE"],
        "Simultaneous Users": ["CONCURUSERN", "CONCURUSERN"],
        "Usage Statistics": ["", "OTHERUSERSTRN"]
    }

    term_value_mappings = {
        "ACCESSIBILITY": {"yes": "YES", "no": "NO", "n/a": "NO"},
        "ARCHIVE": {"yes": "YES", "no": "NO", "n/a": "YES"},
        "DIGCOPY": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "COURSEPACKELEC": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "COURSERES": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "ILLELEC": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "PERPETUAL": {"yes": "YES", "no": "NO", "n/a": "NO"},
        "PRINTCOPY": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "ELECLINK": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "CONCURUSERN": {
            "yes": "Concurrent Users Permitted",
            "no": "Concurrent Users Prohibited",
            "n/a": "Silent"
        },
    }

    # Define your custom transformation functions in config_prod.py, you can then add them to RoamAlmaInterface.__convert_roam_license_object and/or __convert_roam_license_term_object
    # Just include them in the alma_license_class_object property that you want to set dynamically.

    # If you don't want to break the unit tests, you'll have to add a method in HERE with the same name, 
    # but that would return the same value as would have been used had you not added the method. 
    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def convert_active_to_license_status(active):
        """Convert ROAM Active status to Alma license_status

        If ROAM Active = true, we set Alma license_status to ACTIVE. Else, we set it to RETIRED
        """
        if active == True:
            return "ACTIVE"
        else:
            return "RETIRED"

    @staticmethod
    def convert_active_to_review_status(active):
        """Infer value of Alma review_status from ROAM Active status

        If ROAM Active = true, we set Alma review_status to ACCEPTED. Else, we set it to PENDING
        """
        if active == True:
            return "ACCEPTED"
        else:
            return "PENDING"