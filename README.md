# crosswalk

My implementation of the NDA crosswalk

## Directory structure
- **Crosswalk/** - The object oriented library used for mapping
- **definitions/** - The redcap database definitions
- **nda/** - The structure definitions from [nda.nih.gov](https://nda.nih.gov/data_dictionary.html?source=NDA&submission=ALL)
- **maps/hca** - The mapping files for HCA
- **maps/hcd** - The mapping files for HCD

## Usage

First run the [Setup_Definitions](./Setup_Definitions.ipynb) notebook. This will download the latest data dictionaries from redcap and the NDA.

Then run the notebooks [HCD](./HCD.ipynb) and [HCA](./HCD.ipynb). They will download the data, transform it, and validate it against the NDA servers. Note any actionable errors.
