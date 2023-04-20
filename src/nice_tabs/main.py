import os,sys,io
from message_systems import MessageManager
from processes import TabConverter
from user_interfaces import GUI

""" 
	Nice Tabs
    ~~~~~~~~~
    
	This program allows the user to convert an Ultimate Guitar webpage containing a tab to a clean printable PDF.
	Selenium scrapes the data from the given page and they are processed with Beautiful Soup.
	The data are formatted and sent to a LaTeX compiler which creates the PDF.
	Utilizing the Azure dark theme for tkk, a simple GUI is implemented.

	:Copyright (c) 2023 Andrew Schalk

         /\  __
        /--\/  \
       /    \__
               \
            \__/

"""
os.chdir(sys._MEIPASS)#Uncomment for .exe deployment

# This stuff catches anything meant for the terminal and stops it from crashing exe
buffer = io.StringIO()
sys.stdout = buffer
sys.stderr = buffer

MESSAGE_MANAGER = MessageManager()
TAB_CONVERTER   = TabConverter(MESSAGE_MANAGER)
MY_GUI          = GUI(TAB_CONVERTER)#The main thread hangs at this line and will loop forever within GUI to update GUI elements.
