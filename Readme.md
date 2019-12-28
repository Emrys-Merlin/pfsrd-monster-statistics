# Pathfinder Monster Statistics

I wanted to compute my average damage given a challenge rating. For this I needed some distributions concerning armor class given challenge rating and in the end I started to plug a lot of things together and decided to put it in this repository.

## Getting started

1. Download the Excel containing the monster statistics under [this URL](https://docs.google.com/spreadsheets/d/1StTeUz_ZBU3pNlW120msjUX34p9cs7kqQbZ2Ym7cSBE/edit#gid=125506564) (This is _not_ my work. As far as I know thanks should go out to John Reyst, who generated the sheet). You should use the .xlsx format for the download. It might be that you first need to create a copy of the sheet in your own google account.
2. If you want to use the python-dotenv package. Adapt the dotenv-example file and rename it to .env
3. Run and/or have a look at descriptive_statistics.py. This script will create a subdirectory with a bunch of graphs describing the data set. This might be a good starting point to understand the data and the framework.
4. Have a look at the jupyter notebook(s) to see what you can use this tool for, if you want to try out 'inferences'.
5. Have a look at monsters.py and see if you can find some bugs :-)

