# HIVE Software helper:
The software is composed by a **core** module. In this module the main functionalities are:
- Definition of the classes that will be recalled in every specific module
- functions to select the input files and generate the json files needed to recall the dynasaur library
- the keyword reader to parse the keyword from ls-dyna.
## Workflow: from input data in ls-dyna to plots for specific module
The steps that the software performs are the following:
1. Input the folder that contains the input and output LS-Dyna simultation files. In this way, the keyword parser will extract the database declared by the user for ls dyna and generate the JSON files and the commands required by Dynasaur.
2. Once all the files are passed to the 
