## nfocreator
### a tool for creating nfo files from tvheadend recordings

This is a postprocessor script for tvheadend that creates a .nfo file and dowloads images (poster/fanart) - if available - and stores them together within the 
recording folder of the recording.

The script extracts all information from the dvr database and use a TVH Api call.

### Usage

simply get the script from here and make it executable. Set the full path of the script into the post processor field in the recording tab.

> wget https://raw.githubusercontent.com/b-jesch/nfocreator/master/main.py -O main.py
> 
> chmod a+x main.py
