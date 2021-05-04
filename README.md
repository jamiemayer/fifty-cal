# Fifty Cal
> This is a utility script that enables shared calendars from email accounts hosted by 
> namesco. 

[Namesco Webmail](http://webmail.names.co.uk) comes with an iCal based calendar 
feature that doesn't allow for sharing calendars between users. It does however have a 
manual import and export feature that must be done via the web application interface.
This script essentially just automates that manual process by using a combination of 
[Selenium for Python](https://selenium-python.readthedocs.io) and the `requests` 
package in from the Python 3 standard library.

> **Disclaimer - This project is an exercise in bodging and hackery that required me 
> to do things so unspeakably filthy that after writing it, I wanted to just sit in the 
> shower hugging my knees!** I've done my best to test, test and test again but if 
> any bugs are encountered please either raise an issue or alternatively feel free 
> to stick in a PR.


# Contents


# Installation

## MacOS and Linux

### Clone from repo

Currently, this project is only installable from the repo.

* Clone the repository:
  ```
  git clone https://github.com/jamiemayer/fifty-cal.git
  ```

* Ensure that the relevant python virtualenv is activated and run:
  ```
  pip install -r requirements.txt
  ```

* Download and install the Firefox [Gecko Driver](https://github.com/mozilla/geckodriver) 
  and ensure it's accessible in the system path. 
  

# Usage

## Download

To run fifty-cal in download only mode, ensure you are in the root folder of the 
repo and run the following command:
  ```
  python run.py <path/to/config.yaml> --download
  ```

> **Note**: The `--download` flag is optional as this fifty-cal's default mode but 
> is provided where explicit commands are desired, for example in a large crontab.

Running this will pull the `.ics` file down from the server and save it in the 
location specified in the config. If there is an existing file with this name 
already in the location, a diff will be run between them and the merged file will be 
saved. On conflict, I.E an event with the same ID exists in both files but do not 
match, the version with the latest updated timestamp will be kept.


## Upload

Upload mode is in active development and is due to be released "**Soon**"<sup>TM.

## Configuration File
In order to run, a configuration file is needed with a set of mandatory and optional 
values. 

The configuration file should be a YAML file with the following fields:

- `username` - Your email address E.g: jbloggs@example.co.uk
- `password` - The password to your email account
- `output_path` - The location to save downloaded calendars to. This should be a directory not a file.
- `cal_ids` - A YAML dictionary with the name of the calendar as a key and the unique hash of the calendar as the value.
- `calendar_url` - Should be `https://webmail.names.co.uk/?_task=calendar&_cal=` 
  This option only exists for extensibility reasons (probably over-engineering at this point if I'm honest.) and 
  is not used. Technically, this can be overridden to point to another roundcube 
  login page, but I am giving no guarantee of this working as it is not tested. 



## Windows
Windows is currently not supported and there are currently no plans to add this 
functionality.