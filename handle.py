import argparse
import logging
import os

from bin.xlsx_to_objects import clean_json
from bin.roam_to_alma_interface import RoamAlmaInterface
from bin.xlsx_to_objects import convert_xlsx_to_objects
from config.config_prod import Mappings, Settings


def main():
    os.makedirs(name=os.path.dirname(Settings.logging_file), exist_ok=True)
    # Initialize logger:
    logging.basicConfig(filename=Settings.logging_file,
                        filemode='w', level=Settings.logging_level, format="%(levelname)s: %(message)s")

    logging.info("Initializing USMAI ROAM License to Alma Converter...\n")

    # Set default values, overridable by commandline
    license_input = Settings.license_input
    license_terms_input = Settings.license_terms_input
    output_folder = "output"

    # Parse the arguments to user
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--license_file",
                        help="Set the input license file")
    parser.add_argument("-t", "--license_terms_file",
                        help="Set the input license terms file")
    parser.add_argument("-o", "--output_folder",
                        help="The folder to which the XML files will be output")

    logging.info("Parsing Arguments...")
    args = parser.parse_args()

    if args.license_file:
        license_input = args.license_file
        logging.debug("License File Specified: " + args.license_file)
    if args.license_terms_file:
        license_terms_input = args.license_terms_file
        logging.debug("License Terms File Specified: " +
                      args.license_terms_file)
    if args.output_folder:
        output_folder = args.output_folder
        logging.debug("Output Folder Specified: " + args.output_folder)
    logging.info("Done.\n\n")

    logging.info("Parsing object from json...")
    # Parse JSON objects from the excel
    roam_license_objects = convert_xlsx_to_objects(
        license_input)
    if len(roam_license_objects) < 1:
        logging.error("No roam license objects were parsed from Excel!")
    roam_license_term_objects = convert_xlsx_to_objects(
        license_terms_input)
    if len(roam_license_objects) < 1:
        logging.error("No roam license terms were parsed from Excel!")
    logging.info("Done.\n\n")

    # Convert the date of the objects to Alma format
    logging.info("Fixing object date fields...")
    date_fixed_roam_license_objects = RoamAlmaInterface.convert_objects_date_to_alma(
        roam_license_objects, ["Start Date", "End Date"])
    date_fixed_roam_license_term_objects = RoamAlmaInterface.convert_objects_date_to_alma(
        roam_license_term_objects, ["Start Date", "End Date"])
    logging.info("Done.\n\n")

    # Clean the date-fixed objects, if the user wants to
    logging.info("Clean Objects? " + str(Settings.clean))
    if Settings.clean:
        roam_license_objects = clean_json(
            date_fixed_roam_license_objects, remove_newline=Settings.remove_newline)
        if len(roam_license_objects) < 1:
            logging.error("Cleaned license objects array empty!")
    if Settings.clean:
        roam_license_term_objects = clean_json(
            date_fixed_roam_license_term_objects, remove_newline=Settings.remove_newline)
        if len(roam_license_term_objects) < 1:
            logging.error("Cleaned license term objects array empty!")
    if Settings.clean:
        logging.info("Done.\n\n")

    # Initialize the Roam to Alma Interface
    roam_alma_interface = RoamAlmaInterface(
        roam_license_objects, roam_license_term_objects, Mappings, Settings)

    # Convert the terms to Alma values
    logging.info("Converting ROAM Licenses to Alma format...")
    converted_roam_licenses = roam_alma_interface.get_converted_license_objects()
    if len(converted_roam_licenses) < 1:
        logging.error("ROAM-ALMA converted license objects array empty!")
    logging.info("Done.\n\n")

    logging.info("Converting ROAM License Terms to Alma format...")
    converted_roam_license_terms = roam_alma_interface.get_converted_license_term_objects()
    if len(converted_roam_license_terms) < 1:
        logging.error("ROAM-ALMA converted license term objects array empty!")
    logging.info("Done.\n\n")

    # Combine the Licenses and License Terms (logging is in the method)
    roam_alma_interface.combine_roam_license_and_license_terms()

    # Generate generateDS instances (logging is in the method)
    roam_alma_interface.create_generateds_instances()

    # Export the instances to XML and validate them (logging is in the method)
    roam_alma_interface.export_validate_generateds_instances(output_folder)

    logging.info("Program completed.")
    exit(0)


if __name__ == "__main__":
    main()