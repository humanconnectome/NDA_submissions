# crosswalk

HCP implementation of a suite of in-house and pip-installed (python-based) tools to facilitate open and reproducible harmonization between local REDCap databases and BOX sources with NDA data dictionary.  Use this repo to identify HCP-lifespan specific variable names in either database system, and/or to develop a similar Crosswalk for your own data (e.g. to talk to your Redcap, Box, and NDA data dictionary APIs using the libraries developed and/or curated here).     

## Directory structure
- **Crosswalk/** - The object oriented library used for mapping
- **definitions/** - The redcap database definitions
- **nda/** - The structure definitions from [nda.nih.gov](https://nda.nih.gov/data_dictionary.html?source=NDA&submission=ALL)
- **maps/hca** - The mapping files for HCA
- **maps/hcd** - The mapping files for HCD

## Usage

First run the [Setup_Definitions](./Setup_Definitions.ipynb) notebook. This will download the latest data dictionaries from redcap and the NDA.

Then run the notebooks [HCD](./HCD.ipynb) and [HCA](./HCD.ipynb). They will download the data, transform it, and validate it against the NDA servers. Note any actionable errors.
