from datetime import datetime
import os
import re
import logging
import json

from pandas import Timestamp
from bin.license_class import license, license_details, note, note_list, term, term_list, ownered_entity
import xmlschema


class RoamAlmaInterface():

    def __init__(self, roam_license_objects, roam_license_term_objects, mappings, settings):
        self.roam_license_objects = roam_license_objects
        self.roam_license_term_objects = roam_license_term_objects
        self.term_mapping = mappings.term_mappings
        self.term_value_mapping = mappings.term_value_mappings
        self.mappings = mappings
        self.settings = settings

        self.namespace = 'xmlns="http://com/exlibris/urm/repository/migration/license/xmlbeans"'

        # Set empty vars for converted objects
        self.converted_roam_license_terms = None
        self.converted_roam_licenses = None

        # Set empty var for generateDS objects
        self.generateds_instances = None

        self.code_counter = {
            "prefix": "ROAM",
            "counter": 0
        }

    def get_converted_license_objects(self):
        """Returns converted license objects. Converts them if not already done so.

        WILL NOT RE-CONVERT IF THERE'S CHANGES

        Input: None
        Output: Array of converted ROAM licenses
        """
        if not self.converted_roam_licenses:
            self.converted_roam_licenses = self.__convert_roam_license_array(
                self.roam_license_objects)

        return self.converted_roam_licenses

    def get_converted_license_term_objects(self):
        """Returns converted license term objects. Converts them if not already done so.

        WILL NOT RE-CONVERT IF THERE'S CHANGES

        Input: None
        Output: Array of converted ROAM license terms
        """
        if not self.converted_roam_license_terms:
            self.converted_roam_license_terms = self.convert_roam_license_terms_array(
                self.roam_license_term_objects)

        return self.converted_roam_license_terms

    def combine_roam_license_and_license_terms(self):
        """This method takes all the license term objects and merges their term_list into the respective license

        This function will ignore any license term objects that don't have matching licenses

        Input: None
        Output: None (sets internal instance variable)"""
        license_terms_matched = 0

        logging.info("Combining Roam Licenses and License Terms...")
        for license in self.converted_roam_licenses:
            # Get the code of the license to match by
            target_license_name = license["license_details"]["license_name"]
            target_license_start_date = license["license_details"]["start_date"]

            logging.debug("Target Name: " + target_license_name)

            # Loop through the license terms to find the matching terms
            for license_term_object in self.converted_roam_license_terms:

                # If the license names are a match,
                # AND the start dates are a match
                # add the license terms to the original license
                if (license_term_object["license_details"]["license_name"] == target_license_name) and (license_term_object["license_details"]["start_date"] == target_license_start_date):

                    # Set a variable that it's matched, for logging purposes, or increment it if its not there
                    if "matched" in license_term_object:
                        license_term_object["matched"] += 1
                    else:
                        license_term_object["matched"] = 1

                    # Increment the 'matched' variable
                    license_terms_matched += 1
                    for license_term in license_term_object["term_list"]:
                        license["term_list"].append(license_term)

                    # If the license notes are empty, add them
                    if len(license['note_list']) == 0:
                        license['note_list'] = license_term_object['note_list']

                    # Add license links, if empty
                    if license['license_details']['URI'] == "":
                        license['license_details']["URI"] = license_term_object['license_details']["URI"]

                    # Also, set the license Status and Review Status equal to that of the license term,
                    # as they're set dynamically by the term using the 'Active' column. I know this will
                    # go through more than once, but it should do.
                    license["license_details"]["license_status"] = license_term_object["license_details"]["license_status"]
                    license["license_details"]["review_status"] = license_term_object["license_details"]["review_status"]

        # Make sure all license terms were matched
        unmatched_license_terms = []
        license_terms_matched_more_than_once = []
        for license_term_object in self.converted_roam_license_terms:
            if "matched" in license_term_object:
                if license_term_object["matched"] > 1:
                    # If it's matched more than once, add it to the appropriate array
                    license_terms_matched_more_than_once.append(
                        {"name": license_term_object["license_details"]["license_name"], "terms": license_term_object["term_list"]})
            else:
                # If there's no matched variable, add it to the unmatched license terms
                unmatched_license_terms.append(license_term_object)

        logging.info("License Terms Matched: " + str(license_terms_matched))
        logging.info("Number of license terms unmatched: " +
                     str(len(unmatched_license_terms)))
        if len(unmatched_license_terms) > 0:
            logging.error("Unmatched License Terms: " +
                          json.dumps(unmatched_license_terms))
        logging.info("Number of license terms matched more than once: " + str(
            len(license_terms_matched_more_than_once)))
        if len(license_terms_matched_more_than_once) > 0:
            logging.error("License Terms Matched More Than Once: " +
                          json.dumps(license_terms_matched_more_than_once))
        logging.info("Done.\n\n")

    @staticmethod
    def convert_objects_date_to_alma(object_array, property_names_array):
        """Converts certain properties in an object to the proper Alma format YYYMMDD

        Input: Array of objects to convert, property names that you want to convert.
        Output: Array of converted objects."""
        converted_objects = []
        for object_to_convert in object_array:
            converted_objects.append(RoamAlmaInterface.convert_object_date_to_alma(
                object_to_convert, property_names_array))

        return converted_objects

    @staticmethod
    def convert_object_date_to_alma(ind_object, property_names_array):
        """Converts certain properties in an individual object to the proper Alma format YYYYMMDD

        Input: Object, array of property names you want to convert
        Output: Converted object"""

        for property in property_names_array:
            # Convert it only if it's not empty
            if ind_object[property] != "":

                # If it's a datetime or timestamp, convert it with strftime
                if isinstance(ind_object[property], datetime) or isinstance(ind_object[property], Timestamp):
                    ind_object[property] = datetime.strftime(
                        ind_object[property], "%Y%m%d")

                # If it's a string, convert it with strptime and strftime. ONLY YYYY-MM-DD ACCEPTED
                elif isinstance(ind_object[property], str):
                    try:
                        ind_object[property] = datetime.strftime(datetime.strptime(
                            ind_object[property], "%m/%d/%Y"), "%Y%m%d")
                    except ValueError:
                        ind_object[property] = datetime.strftime(datetime.strptime(
                            ind_object[property], "%Y-%m-%d"), "%Y%m%d")

        return ind_object

    def create_generateds_instances(self):
        """Generate generateDS instances from the combined license + license terms objects.

        These instances can then be exported to xml simply by calling the export() method.

        Input: None
        Output: None (Sets internal instance variable.)
        """
        logging.info("Creating generateDS instances...")
        generateds_instances = []
        for converted_license in self.converted_roam_licenses:
            generateds_object = self.__create_generateds_instance(
                converted_license)
            generateds_instances.append(generateds_object)

        self.generateds_instances = generateds_instances
        logging.info("Done.\n\n")
        return self.generateds_instances

    def export_validate_generateds_instances(self, output_folder, prefix="license-", suffix=""):
        """Print out all the licenses, in xml format, using the given output_folder, prefix, and suffix

        Input: output_folder (optional), prefix (optional), suffix (optional)
        Output: -1 for not successful, 1 for successful"""
        # Make the folder if it doesn't already exist
        logging.info("Exporting license XML files to " + output_folder)
        os.makedirs(output_folder, exist_ok=True)
        counter = 0

        if not self.generateds_instances:
            return -1

        for generateds_instance in self.generateds_instances:
            # Generate the output file name using the specified prefix and suffix, as well as the license name (cleaned up to lower case and certain chars removed)
            # , with an XML file extension
            output_file = output_folder + "/" + \
                str(counter) + "-" + prefix + re.sub("[.,!'() &$%#@*]", '', generateds_instance.get_license_details(
                ).get_license_name().lower()) + suffix + ".xml"
            with open(output_file, "w") as opened_output_file:
                generateds_instance.export(
                    opened_output_file, level=0, namespacedef_=self.namespace)
                logging.debug("Wrote to " + output_file)

            xmlschema.validate(output_file, self.settings.xsd_file)
            logging.debug("Validation for " + output_file + " successful")

            counter += 1

        logging.info("Exported {} out of {} generateDS instances".format(
            counter, str(len(self.generateds_instances))))
        logging.info("Done.\n\n")
        return 1

    def convert_roam_license_terms_array(self, roam_objects):
        """Converts Roam objects parsed from XLSX to objects that can be passed to the license_class, which generates XML
        Input: ROAM XLSX parsed object[]
        Output: Alma license_class-ready object[]"""
        converted_objects = []

        for roam_object in roam_objects:
            converted_object = self.__convert_roam_license_terms_object(
                roam_object)
            converted_objects.append(converted_object)

        return converted_objects

    def __convert_roam_license_array(self, roam_objects):
        """Converts Roam objects parsed from XLSX to objects that can be passed to the license_class, which generates XML
        Input: ROAM XLSX parsed object[]
        Output: Alma license_class-ready object[]"""
        converted_objects = []

        for roam_object in roam_objects:
            converted_object = self.__convert_roam_license_object(
                roam_object)
            converted_objects.append(converted_object)

        return converted_objects

    def __create_generateds_instance(self, converted_license):
        """Generates a GenerateDS license class from a converted license (a license that's been converted to Alma JSON format)

        Input: Alma JSON license
        Output: GenerateDS license class"""
        # Create ds ownered entity
        ds_ownered_entity = ownered_entity(
            created_by=converted_license["license_details"]["ownered_entity"]["created_by"])

        # Create the ds notes + notes list component
        ds_notes = []
        for json_note in converted_license["note_list"]:
            ds_notes.append(
                note(content=json_note["content"], ownered_entity=ds_ownered_entity))
        ds_note_list = note_list(note=ds_notes)
        if len(ds_note_list.get_note()) != len(converted_license["note_list"]):
            logging.error(
                converted_license["license_details"]["license_name"] + " - Not all notes added")

        # Create the ds license terms + license terms list component
        ds_terms = []
        for json_term in converted_license["term_list"]:
            ds_terms.append(
                term(term_code=json_term["term_code"], term_value=json_term["term_value"]))
        ds_term_list = term_list(term=ds_terms)
        if len(ds_term_list.get_term()) != len(converted_license["term_list"]):
            logging.error(
                converted_license["license_details"]["license_name"] + " - Not all terms added")

        ds_license_details = license_details(license_code=converted_license["license_details"]["license_code"], type_=converted_license["license_details"]["type"],  license_name=converted_license["license_details"]["license_name"], license_status=converted_license[
            "license_details"]["license_status"], start_date=converted_license["license_details"]["start_date"], review_status=converted_license["license_details"]["review_status"], URI=converted_license["license_details"]["URI"], ownered_entity=ds_ownered_entity)
        if "end_date" in converted_license["license_details"]:
            ds_license_details.set_end_date(
                converted_license["license_details"]["end_date"])

        final_license_ds = license(ds_license_details, None, None)
        # Add terms and notes only if they exist
        if len(ds_notes) > 0:
            final_license_ds.set_note_list(note_list=ds_note_list)
        if len(ds_terms) > 0:
            final_license_ds.set_term_list(term_list=ds_term_list)

        return final_license_ds

    def __convert_roam_license_object(self, roam_object):
        # It is possible to forget to export license links in the main license file. If this is the case,
        # they will be set by the license terms.
        license_links = ""
        if "License Links" in roam_object:
            license_links = roam_object["License Links"]

        alma_license_class_object = {
            "license_details": {
                "ownered_entity": {
                    "created_by": "USMAI ROAM License to Alma License Converter"
                },
                "license_name": roam_object["Name"],
                "license_code": self.code_counter["prefix"] + "-" + str(self.code_counter["counter"]),
                "license_status": "ACTIVE",
                "review_status": "ACCEPTED",
                "start_date": roam_object['Start Date'],
                "URI":  license_links,
                "type": "LICENSE"
            },
            "term_list": [],
            "note_list": [],
        }

        # Increment code counter
        self.code_counter["counter"] += 1

        # Add end date, if it exists
        if roam_object["End Date"] != "":
            alma_license_class_object["license_details"]["end_date"] = roam_object['End Date']
        return alma_license_class_object

    def __convert_roam_license_terms_object(self, roam_object):
        alma_license_class_object = {
            "license_details": {
                "ownered_entity": {
                    "created_by": "USMAI ROAM to Alma Converter"
                },
                "license_name": roam_object["License Name"],
                # License code will be generated for the license, not license term. They are
                # matched on 'name', for now. 
                "license_code": "",
                "license_status": self.mappings.convert_active_to_license_status(roam_object["Active"]),
                "review_status": self.mappings.convert_active_to_review_status(roam_object["Active"]),
                "start_date": roam_object["Start Date"],
                "end_date": roam_object["End Date"],
                "URI": roam_object["License Links"],
                "type": "LICENSE"
            },
            "term_list": self.__convert_license_term_to_alma(roam_object["Name"], roam_object["License Qualifiers"], roam_object["Allowed"], roam_object["Description"]),
            "note_list": self.__convert_license_notes(roam_object["License Summary"], roam_object["License Notes"], roam_object["Publisher"]),
        }

        return alma_license_class_object

    def __convert_license_notes(self, license_summary, license_notes, publisher):
        """Convert license summary and license notes into Alma notes format

        Input: license_summary, license_notes
        Output: Notes JSON array, convertable to Alma
        """
        notes = []

        if license_summary != "":
            notes.append({
                "content": "License Summary: " + license_summary
            })
        if license_notes != "":
            notes.append({
                "content": "License Notes: " + license_notes
            })
        if publisher != "":
            notes.append({
                "content": "Publisher: " + publisher
            })

        return notes

    def __convert_license_term_to_alma(self, roam_term_name, roam_term_qualifier, roam_term_allowed, roam_term_description):
        """Converts a ROAM term into one or more Alma License Terms

        Input: Roam License Term Name, Roam License Term Qualifier, Roam Term Allowed, Roam Term Description
        Output: Roam term JSON array, convertable to Alma.
        """
        # Get the mapping of the ROAM license term name to the Alma License Term Names
        mapping = self.term_mapping[roam_term_name]

        main_license_term_code_name = mapping[0]
        notes_license_term_code_name = mapping[1]

        # The array of terms to return
        term_array = []

        # If there's a main license term, get the terms
        if main_license_term_code_name != "":
            main_license_term = {
                "term_code": main_license_term_code_name,
                "term_value": self.term_value_mapping[main_license_term_code_name][roam_term_allowed]
            }
            term_array.append(main_license_term)

        # Create a notes license term if the code exists and there's a roam qualifier or roam description
        if notes_license_term_code_name != "" and (roam_term_qualifier or roam_term_description):
            # Format the notes term value free-text based on whether there's a roam qualifier and/or roam description
            term_value = ""

            # If things are going into the Other User Restriction field, add a descriptor for what's included based on the roam name, followed by a colon
            if notes_license_term_code_name == "OTHERUSERSTRN":
                term_value += roam_term_name + ": "
            # If there's a roam term qualifier, add the qualifier followed by a a semicolon.
            if roam_term_qualifier:
                term_value += roam_term_qualifier
                if roam_term_description:
                    term_value += "; "
            # If there's a roam term description, add it at the end.
            if roam_term_description:
                term_value = term_value + roam_term_description

            notes_license_term = {
                "term_code": notes_license_term_code_name,
                "term_value": term_value
            }

            term_array.append(notes_license_term)

        return term_array