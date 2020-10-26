# dbgap-pfb
Transforming unharmonized dbgap phenotype study-level data into a single PFB file


# HOW-TO
in the `dicts.json` file add the data-dictionary files from dbgap and links as to how the different data nodes link to eachother

in the `nodes.json` file add the data files with the field that you will be using for submitter-id

after those are both filled out you need to run both the `parseDict.py` and `parseText.py` scripts to create the files that PyPFB can use to generate a PFB. You can then use the uc-cdis/pypfb to generate a PFB of the dbgap data
