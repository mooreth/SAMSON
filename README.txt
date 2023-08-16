0. This is still an early prototype, expect crashes, weird things, frustration, etc. Thanks for your help in making it better. 

1. See https://www.msg.chem.iastate.edu/GAMESS/download.html for directions on obtaining GAMESS

2.GAMESS needs to be installed in the default location or else changes to the code will be needed to tell the code where to look for GAMESS

3. Open the Python interface in SAMSOM. More information on using Python with SAMSON see the SAMSOM documentation. 

4. Run the extension with python.magic("run -i C:/Path/to/file/GAMESS.py") It is recommended not to have any spaces in the path. This should start the GUI.

It is possible to perform a simple single point energy calculation or geometry optimization from the GUI using various levels of theory. 
These are the only two types of calculations currently available from the GUI. However a user defined GAMESS input file can be used by selecting “use input file instead”. 
The code will add the SAMSON geometry to the GAMESS just above the $END keyword

5. Input and output files are created in the GAMESS directory along with a log that may contain any errors.

6. One CO2 file is available in the Examples folder. Open this in SAMSON, and run the script. Add a comment if you like, but keep everything else the same. Click run the calculation,
and in a few seconds the optimized geometry should be displayed in the SAMSOM window.

Please help me make this better with testing and suggestions, or even coding if you can. You can also support more development with a small donation at https://ko-fi.com/tommoore_diamondoid 