import csv
import unicodedata
from bs4 import BeautifulSoup

# USE THE XLSX VERSION INSTEAD. IT HAS A DIFFERENT OUTPUT. IF YOU WANT THIS TO BE COMPATIBLE WITH
# THE REST OF THE PROGRAM, YOU'LL HAVE TO CONVERT SOME OF THE COLUMN VALUES


def clean_csv(filepath):
    """
    USE XLSX INSTEAD.
    This method removes compatiblity characters and HTML tags from the CSV file (e.g., /xa0, /xa03)

    Input: Filepath of CSV file to clean
    Output: Filepath of cleaned CSV file, same filename but with .csv_cleaned at the end.
    """
    cleaned_file_path = filepath + "_cleaned"

    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        # Remove special characters from the csv file
        compatibility_removed_file_text = unicodedata.normalize(
            'NFKD', csvfile.read())
        html_cleaned_file_text = BeautifulSoup(
            compatibility_removed_file_text, 'html.parser').get_text()

        # Write the cleaned text to a file.
        with open(cleaned_file_path, 'w', newline='', encoding='utf-8') as cleaned_file:
            cleaned_file.write(html_cleaned_file_text)

    # Return the filepath of the cleaned file
    return cleaned_file_path


def convert_csv_to_objects(filepath, clean=False):
    """
    USE XLSX INSTEAD.
    This method converts a CSV file to a list of python objects.

    Input: Filepath of CSV, clean=True/False (parameter to clean compatibility characters + HTML from the file or not)
    Output: Array of Python Objects representing CSV rows
    """
    objects = []
    file_to_run = filepath

    # Clean the file from special characters if clean is true
    if clean == True:
        file_to_run = clean_csv(filepath)

    with open(file_to_run, newline='', encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            objects.append(row)

    return objects