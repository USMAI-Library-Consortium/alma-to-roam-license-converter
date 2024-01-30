import logging


class Settings:
    # Clean all data parsed from excel, removing HTML data and Unicode compatibility characters (/xa0, etc)
    clean = True
    # Remove newlines only works if clean=True
    remove_newline = True
    # License XSD file
    xsd_file = "config/erm_license_edited.xsd"
    # License input file (can also be set with commandline)
    license_input = "input/licenses.xlsx"
    # License terms input file (can also be set with commandline)
    license_terms_input = "input/license_terms.xlsx"
    # Logging file
    logging_file = "logs/systemlogs.log"
    # Logging level
    logging_level = logging.INFO


class Mappings:

    # PLEASE MODIFY OR ADD TO THESE IN config_prod.py !!
    term_mappings = {
        "ADA Accessibility": ["ACCESSIB", "ACCESSIB_N"],
        "ADA Compliancy": ["ACCESSIB", "ACCESSIB_N"],
        "Archiving": ["ARCHIVING", "ARCHIVEN"],
        "Authentication": ["AUTHNTIC", "AUTHNTIC_N"],
        "Cancellation Policy": ["CANC-POL", "CANC-POL_N"],
        "Post Cancellation Rights/Perpetual Access": ["TERM-RIGHT", "TERMRIGHTN"],
        "Copying": ["COPY", "COPY_N"],
        "Course Packs": ["COURSEPACKELEC", "COURSEPACKN"],
        "Course Reserves": ["COURSERES", "COURSERESNOTE"],
        "Downloading/Saving": ["DL-SAVE", "DL-SAVE_N"],
        "Interlibrary Loan (ILL)": ["ILLELEC", "ILLN"],
        "Inter-library loan": ["ILLELEC", "ILLN"],
        "International ILL": ["INTL-ILL", "INTL-ILL_N"],
        "Perpetual Access/Post Cancellation Rights": ["PERPET-RT", "PERPETUALN"],
        "Printing": ["PRINTCOPY", "PRINTCOPYN"],
        "Public Performance": ["PUB-PRFM", "PUB-PRFM_N"],
        "Sharing/Linking": ["ELECLINK", "ELECLINKNOTE"],
        "Simultaneous Users": ["CNCUR-USER", "CONCURUSERN"],
        "Usage Statistics": ["USE-STAT", "USE-STAT_N"],
        "IP access": ["IPACCESS", "IPACCESS_N"],
        "Walk-in user": ["WALK-IN", "WALKIN"]
    }

    term_value_mappings = {
        "ACCESSIB": {"yes": "YES", "no": "NO", "n/a": "SILENT"},
        "ARCHIVING": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "AUTHNTIC": {"yes": "YES", "no": "NO", "n/a": "SILENT"},
        "CANC-POL": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "TERM-RIGHT": {"yes": "YES", "no": "NO", "n/a": "SILENT"},
        "COPY": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "COURSEPACKELEC": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "COURSERES": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "DL-SAVE": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "ILLELEC": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "INTL-ILL": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "PERPET-RT": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "PRINTCOPY": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "ELECLINK": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "CNCUR-USER": {
            "yes": "PERMITTED",
            "no": "PROHIBITED",
            "n/a": "SILENT"
        },
        "IPACCESS": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "PUB-PRFM": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "WALK-IN": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"},
        "USE-STAT": {"yes": "YES", "no": "NO", "n/a": "SILENT"}
    }

    # Define your custom transformation functions here, you can then add them to RoamAlmaInterface.__convert_roam_license_object and/or __convert_roam_license_term_object
    # Just include them in the alma_license_class_object property that you want to set dynamically.
    # ----------------------------------------------------------------------------------------------
    # PLEASE MODIFY OR ADD THESE IN config_prod.py !!
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