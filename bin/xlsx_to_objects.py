import pandas as pd
import unicodedata
from bs4 import BeautifulSoup
import json


def clean_json(json_objects, remove_newline=False):
    """
    This method removes HTML tags, compatibility characters, and (optionally) newlines from a JSON object

    Input: json objects to be cleaned, remove_newlines (boolean)
    Output: Cleaned JSON
    """
    # Convert json object array to a string with ensure_ascii = false. If ensure_ascii is true,
    # it will convert certain spaces to compatibility characters ('/xa0', etc) which are hard to
    # remove
    stringified_json = json.dumps(json_objects, ensure_ascii=False)

    # Remove HTML Tags
    stringified_cleaned_json = BeautifulSoup(
        stringified_json, 'html.parser').get_text()

    # Remove compatibility characters
    stringified_normalized_json = unicodedata.normalize(
        "NFKD", stringified_cleaned_json)

    # Remove line breaks, if users want it
    if remove_newline == True:
        stringified_normalized_json = stringified_normalized_json.replace(
            "\\n", " ")

    # Convert the string back to JSON
    cleaned_json = json.loads(stringified_normalized_json)

    # Returned the cleaned JSON
    return cleaned_json


def convert_xlsx_to_objects(filepath):
    """
    This method converts an XLSX file to a list of python objects.

    Input: Filepath of XLSX
    Output: Array of Python Objects representing XLSX rows
    """

    objects = []

    # Read the excel file, and disable nan values (we want empty string instead)
    df = pd.read_excel(filepath, keep_default_na=False)

    objects = df.to_dict(orient="records")

    return objects