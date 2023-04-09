import os,sys
from MessageManager import MessageManager
from TabConverter import TabConverter
from GUI import GUI

""" Nice Tabs
This program allows the user to convert an Ultimate Guitar webpage containing a tab to a clean printable PDF.
Selenium scrapes the data from the given page and they are processed with Beautiful Soup.
The data are formatted and sent to a LaTeX compiler which creates the PDF.
Utilizing the Azure dark theme for tkk, a simple GUI is implemented.

Copyright 2023 Andrew Schalk

         /\  __
        /--\/  \
       /    \__
               \
            \__/
      
"""

#os.chdir(sys._MEIPASS)#Uncomment for .exe deployment

myMessageManager = MessageManager()
myConverter = TabConverter(myMessageManager)
myGUI = GUI(myConverter)#The main thread hangs at this line and will loop forever within GUI to update GUI elements.