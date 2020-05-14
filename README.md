# crosswalk

HCP implementation of a suite of in-house and pip-installed (python-based) tools to facilitate open and reproducible harmonization between local REDCap databases and BOX sources with NDA data dictionary.  Use this repo to identify HCP-lifespan specific variable names in either database system, and/or to develop a similar Crosswalk for your own data (e.g. to talk to your Redcap, Box, and NDA data dictionary APIs using the libraries developed and/or curated here).     

## Directory structure
- **Crosswalk/** - The object oriented library used for mapping
- **definitions/** - The redcap database definitions
- **nda/** - The structure definitions from [nda.nih.gov](https://nda.nih.gov/data_dictionary.html?source=NDA&submission=ALL)
- **maps/hca** - The mapping files for HCA
- **maps/hcd** - The mapping files for HCD

## Usage
Step 0: If this is your first time cloning a jupyter notebook from a github repository, or you think we might have forgotten to mention something,
        follow the instructions in helpMeSetUpThisRepoInMyLocalEnvironment.txt

Step 1: First run the [Setup_Definitions](./Setup_Definitions.ipynb) notebook. This will download the latest data dictionaries from your REDCap databases and the NDA.
If this is your first time cloning a jupyter notebook from a github repository, follow the instructions in helpMeSetUpThisRepoInMyLocalEnvironment.txt to get here

Step 2: Modify and run the notebooks [HCD](./HCD.ipynb) and [HCA](./HCD.ipynb) according to the names/variables in your own local REDCap and Box systems.
They will download the data, transform it, and validate it against the NDA servers.  Your most time consuming task will be in modifying the map betweeen
variables in your Redcap Databases and their destinations at the NDA.

- For example, every variable that you would like to send to the NDA has to be in one of the maps, such as https://github.com/humanconnectome/NDA_submissions/blob/master/maps/hcd/asr01.yaml. 
- Note any actionable errors.

Step 3: Validation of structures at the NDA can happen either by downloading vtcmd.py and running it against all of your generated .csv files,
        https://pypi.org/project/nda-tools/
        or by navigating to their folder from the GUI tool https://nda.nih.gov/vt/  

Step 4: After you have all of your structures validated, you can upload them to the NDA under your collection using the same tools as in step 3,
        but you'll need an admin to grant permission to submit data under your NDA user name.


Step 5: Browse the documentation headings on  https://pypi.org/project/nda-tools/ so you know more about this tool and can discuss its use cases.
        In particular, note that this tool is also capable of DOWNLOADING the data from the NDA

