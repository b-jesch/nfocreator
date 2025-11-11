## nfocreator
### a tool for creating nfo files from tvheadend recordings

This is a postprocessor script for tvheadend that creates a .nfo file and dowloads images (poster/fanart) - if available - and stores them together within the 
recording folder of the recording.

The script extracts all information from the dvr database and use a TVH Api call.

### Usage

simply determine your python version and get the script from here and make it executable.
> type in a terminal, you should get your default python interpreter
> 
> python --version
>
> wget https://raw.githubusercontent.com/b-jesch/nfocreator/master/main.py -O main.py # for python 2.x
> 
> wget https://raw.githubusercontent.com/b-jesch/nfocreator/Python3.8/main.py -O main.py # for python 3.x
> 
> chmod a+x main.py

 Change the line 3-6 (URL, USER, PASS) within the script to your requirements. Set the full path of the script into the post processor field in the recording tab.
