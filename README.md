# id_db

# Setup

## Python Setup
This script was developed using Python 3.7.6, however the script should work with any version of python greater than 3.5.  Run `python --version` to check your the version currently installed on your system.*

## Get and install >= Python 3.6
`sudo add-apt-repository ppa:deadsnakes/ppa` *these repositories expire from time to time.  As of 3/19/20 deadsnakes worked to install*  
`sudo apt-get update`
`sudo apt-get install python3.x` [.6 or .7]

## Set updated version as default version called with Python3 command
`sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.x 1`    
`sudo update-alternatives --config python3`  
`python3 --version` //now returns newly installed version of python  


## Repository Setup
git clone https://github.com/awpenn/id_db.git  
cd id_db  
bash setup.sh  

## Additional Configuration
You will have to create a .env file in the root directory of the repository (`id_db`), containing the appropriate database connection variables. Use the template below:
```
DBIP = "[DATABASE.IP.ADDRESS]"
DBPASS = "[USER_PASS]" *for testing, will be "adsp.tester"*
DBPORT = "5432"
DB = "[DATABASE_NAME]"
DBUSER = "[USERNAME]" *for testing, will be "tester"*
```

# Using the script
1. Enable the virtualenv with `source .venv/bin/activate`
2. place a csv (not .xslx) file in the `source_files` directory.  This file should contain rows of comma-separated values for the following fields (in the following order):
- site-based family id
- site-based individual id
- a "lookup" id representing a concatenation of the site-based family and individual ids, separated by underscore
- the letter-based code representing the cohort to which the subject belongs.  These are typically 3 or 4-letter codes in allcaps, and must be taken from the `cohort_identifier_codes` table in the database. 

so for example, one record in this file could look like:  
``` 
895,13,895_13,CUHS
```
Make sure that there are no blank lines at the end of the csv file (this can occur sometimes when saving a .csv file from an existing .xsls file).

3. In the command line, run `python adspid-csv.py` -- *ensure again that your virtual environment is activated*

4. You will be prompted to input some information regarding the data to be loaded into the database.  Select the type of data being entered (ie. case/control or family data).  This will determine how the "lookup id" is generated.  If you select "family", you will be further prompted to select whether or not ADSP family ids should be assigned.  

5. Upon completion of the script, you will find a logfile in the `log_files` directory, which will give brief information about any errors that occurred during loading.  You will also find a document that lists newly generated ADSP ids that were successfully added to the database.
6. In the database, review newly entered data to ensure that it has been entered correctly.  