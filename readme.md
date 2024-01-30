# USMAI ROAM License to Alma Converter

Welcome to the USMAI ROAM to Alma Converter! This program takes licenses and their associated license terms which have been extracted from the ROAM ERM tool in XLSX format, and converts them into XML that can be imported into ExLibris Alma. It maps the values of certain ROAM XLSX columns into specific fields of the Alma XML. It will then validate the created XML against an ExLibris-provided XSD file.

This converter is currently configured according to our needs, but the mappings are designed to be easily configurable through the Mappings class in `config/config_prod.py`! There's comments throughout the code explaining what most things do, but I'll try to condense things here and give a clear enough understanding.

IMPORTANT: This application was written in August 2023. Since then, either the ROAM extracts or Alma XSD may have changed. If so, this program may have to be modified to reflect these changes. There is a section below describing the sections that may have to be changed. (See 'Re-configuring the application')

## Getting Started

As this is a Python program that uses a number of 3rd party libraries, you'll have to start out by creating a virtual environment using the terminal:

- `python3 -m venv .venv`
  (Of course, you can set the venv to whatever location you want. This just makes it simple by creating it in the project directory.)

You'll then have to use the terminal to set the source to the venv & active it:

- Mac bash/zsh: `source .venv/bin/activate`
- Other: see https://docs.python.org/3/library/venv.html

Then, install the pip requirements:

- `pip3 install -r requirements.txt`

Lastly, copy config_template.py into a file called config_prod.py. This will be your configuration file for the program.

To ensure basic things are working, you can run the included tests with:

- `python3 -m unittest discover`

Pretty simple!

## Configuring the application

You'll mainly be looking at the config_prod.py file in the config foler, as that's where the user-configurable settings are. Edit the config_prod and leave the config_template be; this will allow you to reference the original settings.

### Settings class

(Within the config files)

In this class, you can configure some simple options. By default the program look for licenses.xlsx and license_terms.xlsx in the input/ folder, and will output XML files to /output. You can set these option in this Settings class, and override them with command line arguments.

There are a few other options in the Settings class. You can set the log file output and the logging level here. DEBUG will show the most information, so I recommend using 'INFO' unless something strange is happening.

You can also modify how the program extracts data from the ROAM license XML. Extracted ROAM licenses tend to have certain messy-looking content, such as HTML or compatibility characters, in the text. These will show up as plain text in Alma, which will again look messy. The program is set to automatically remove such characters through the 'clean' option. Turning off 'clean' will leave any HTML or compatibility characters in the extracted data. If you set clean=True, you can also opt to remove newlines (\n), which cleans up the XML files a bit more. These will be visible as the newline character in Alma, which is again not what we want.

### Mappings class

(Within the config files)

The Mappings class tells the program how to convert ROAM values to what they should be in Alma. This is relatively complex, and is explained below.

#### Term Mappings

**TLDR: This dict maps Roam License Term names into the codes that they should appear as in Alma. For each entry in the term mappings dictionary (`Mappings.term_mappings`), a ROAM license term is followed by 2 Alma Term Codes. This is because Alma generally stores license terms in a main term and a secondary term. The main term generally indicates whether the respective action (copying, inter-library loan, archiving) is permitted or not, while the secondary term has a similar name (with an 'N' appended at the end) and holds the notes for that term. The first Alma Term code in the mappings will transform the 'Allowed' column in the ROAM XSLX into an Alma Term using the associated Term Value Mapping (see below), and the second one will construct a term with the License Term Qualifiers and Description.**

NOTES

In the term mappings. you can leave either the first or second array entry (term code) blank. If you leave either of them blank, the program will not generate the respective license term.

LONG VERSION:

IMPORTANT - partway into our development of this program, ExLibris told us we can use whatever term codes we want. We suggest using the provided terms when possible, and creating new ones where none of the provided terms fit. The list of terms can be found in the included XSD files, as well as in ExLibris's documentation. This greatly simplifies this process because we can create a MAIN and NOTES term for every ROAM license term.

NOTE THAT THE INCLUDED XSD IS NOT BEING UPDATED - YOU SHOULD VERIFY WHETHER IT HAS CHANGED. THE FORMAT OF THE ALMA XML IS ALSO NOT BEING UPDATED, THE CONVERTER MAY NEED TO BE REGENERATED.

\*\*Note, MAIN and NOTES are not ExLibris' vocabulary, they're mine.

Take a look at `Mappings.term_mappings`. This is where the ROAM license term is mapped to one or more Alma License Term Codes. Unlike ROAM, which holds everything pertaining to a license term in a single row, Alma only has one value per term code. So we should generally create two terms, one for the main value and one for the notes value.

Thie term_mappings dictionary takes the ROAM term name and returns two term codes. NOTE - THIS ONLY REPRESENTS ROAM TERMS WE USE. THERE MAY BE OTHERS THAT YOU HAVE TO ADD.

Each dictionary listing is a ROAM term name followed by an array of two strings, which represent the Alma Term Codes. The first array entry is always a main term code (unless the main term is in the second array entry, in which this array entry will be empty). It uses the value of the ROAM 'Allowed' column to create the Alma Term Value. The values for this column are mapped in `Mappings.term_value_mappings`.

Please note that any term_mapping in the first array entry (the MAIN term) must have a corresponding value term mapping, otherwise there will be a KeyError.

The second array entry (Main term) is _generally_ the notes term code, and it uses the ROAM 'License Qualifiers' and 'Description' columns to set the Alma Term Value. Although it's generally for notes, you could use it for the main term if you wanted to only include the License Qualifiers and Description and ignore the 'allowed' column entirely. Please note that a ROAM term with empty Description AND License Qualifiers will be when generating. This seems preferable to creating an empty term or extrapolating the values another way.

The second array entry (Notes term) does not take into account the value of the 'Allowed' column, so if allowed says 'n/a', for example, but the ROAM extract still contains notes, a Notes term will still be created. You could change this functionality by modifying the `RoamAlmaInterface.__convert_license_term_to_alma` function, however we've found that unhelpful because in our case, the values of ROAM's 'Allowed' column are not particularly reliable (e.g., there's main terms that say n/a but still describe active terms in the Description).

#### Term Value Mappings

Term Value Mappings are included in `Mappings.term_value_mappings`. They are designed to map the MAIN term code (the first array entry for each property in the term_mappings dictionary) to a value. When generating the MAIN term code for a ROAM license, program will match the value of the 'Allowed' column to whatever its corresponding value is. For instance, in the line:

`"COURSEPACKELEC": {"yes": "PERMITTED", "no": "PROHIBITED", "n/a": "SILENT"}`

If the 'Allowed' column for a ROAM license says 'n/a', and you have set this ROAM license to map to the Main Term Code 'COURSEPACKELEC' (in the process described in 'Term Mappings'), this program will assign the value 'PERMITTED' to an Alma term with code 'COURSEPACKELEC'.

#### Custom column transformation (Advanced, likely not neccesary)

Some quick info on the structure of the program, needed to understand this section. This program has a few processing steps, one of which is creating a JSON object representing the license and its associated term. This object will be used to generate the Alma XML. One of these is generated while processing the License file, and one while processing the License Terms file. They are later recombined into one object, which uses a mixture of data from both.

```
{
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
```

The roam_object referenced here is simply a dictionary representation of what's included in each ROAM xslx column after some data cleanup.

You'll see a few functions in the Mappings class. These are designed to convert the ROAM columns into different information for the License JSON. I put these here for convenience. Feel free to create your own. You can then reference them here, where it converts the JSON object parsed from ROAM to an Alma JSON object (shown above). To use your own function, simply replace the property value in the JSON object to the name of your function, and pass it whatever values you want. For example, you could create a function that changes the time zone of the start dates, pass the roam_object["Start Date"] to it, and then use that as the value for start_date instead. You'll find the JSON license creation for the License file in `roam_to_alma_interface.RoamAlmaInterface.__convert_roam_license_object`, and the JSON license creation for the License Terms file in `roam_to_alma_interface.RoamAlmaInterface.__convert_roam_license_terms_object`.

NOTE, if the changes you made aren't making a difference, you may be putting them in the wrong JSON license creation function
You can see the dynamics of this interaction in `roam_to_alma_interface.RoamAlmaInterface.combine_roam_license_and_license_terms`.
Everything is pulled from the License object created by the License file except:

1. License Terms
2. review_status
3. license_status ... which are pulled from the License obejct created by the License Terms object.<br>
   ADDITIONALLY, if License Links, License Notes, and License URI are not found in the License object created by the license file, it will look for them in the License objects created by the License Terms object.

WARNING: Making changes here will likely break some of the included unit tests. If you don't want to break the tests, include the same method name in the config_test.py file, but have it return the value that the program originally set that property to (before the custom transformation you created). It will use that method instead of the one you created in config_prod.py when running the tests. You could also modify the test data instead.

## Running the application

Phew, back to the simple stuff. You can run the application from the command line. Navigate to the root of the project and type:

`python3 handle.py`

This will run your program using the settings specified in your config_prod.py. You can override the input license file, input license terms file, and output folder with the following command-line arguments (These will take precedence over config_prod.py):

using command line arguments: `handle.py [-h] [-l LICENSE_FILE] [-t LICENSE_TERMS_FILE] [-o OUTPUT_FOLDER]`

-h, --help show this help message and exit

License File: -l LICENSE_FILE, --license_file LICENSE_FILE
Set the input license file

License Terms File: -t LICENSE_TERMS_FILE, --license_terms_file LICENSE_TERMS_FILE
Set the input license terms file

Output: -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
The folder to which the XML files will be output

As a note, the '&amp' followed by ';' in the XML output files is normal. It's required to display an ampersand properly in XML.

## Re-configuring the application

As mentioned in the introduction, it's possible that the Alma XSD or the ROAM extract formats have changed. Unfortunately, this script was created for one-time use so it's not gonna be super straightforward to modify. To easily support changes in the inputs or output format, the code would need a serious refactor. These are not in-depth instructions - it's gonna take some effort to do these changes (See the scenarios below). I (am486dx) am happy to answer some questions.

Now for some important background on the Alma XSD. The XSD from the ExLibris documentation site was out of date when we created this script. The original XSD forced the program to use one of the pre-defined license codes, but ExLibris said we can now create our own license codes. So, I created a modified XSD to allow for this, which is why the program set to use the `erm_license_edited.xsd`.

NOTE - If ExL makes changes to either of these and you're able to successfully adapt the script to work with them, a pull request on this repo with the changes would be much appreciated! I'm not planning on keeping this up-to-date otherwise, as our organization no longer has use for it, but others may find it helpful and I will still look at and review changes. And, if you could modify the tests (and perhaps add some) that would be even better!

### Scenario - ExLibris provides new XSD

If ExLibris provides a new XSD for generating and validating the License, there's a few things that need to change. You'll have to download the new XSD file into the config folder, and set your program to use that XSD file in the config_prod.py.

You'll then have to regenerate the license_class.py file using the python generateDS package. You'll find the commands to do so in the generate_ds file (comments at the top). This class is what actually generates the XML from the JSON objects.

Lastly, you'll have to look through the roam_to_alma_interface.py to add, remove, or modify the the properties that have changed. You'll likley have to modify \_\_convert_roam_license_terms_object and \_\_convert_roam_license_object to modify the properties on the objects it created. You may also have to modify \_\_create_generateds_instance to create the respective generateds property. And, perhaps other areas in there need to be modified. The JSON objects created by the first two functions I mentioned map to generateds classes, which mirror the format of the XSD.

### Scenario - ROAM provides new license and license terms output.

In this case, I suggest you modify \_\_convert_roam_license_terms_object and \_\_convert_roam_license_object to use the new columns present in the ROAM xlsx. Feel free to add new processor functions. Alternatively, you can pre-process the ROAM xlsx file to be in the older format.
