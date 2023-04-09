import tkinter as tk
from tkinter import IntVar,ttk
from tkinter import *
from tkinter.ttk import *
import threading

class GUI():
    """ The graphical interface for NiceTabs. Uses the Azure dark theme for tkk."""
    
    def __init__(self,tab_converter):
        """
        :param tab_converter (TabConverter): The current instance of TabConverter
        """
        
        width  = 600
        height = 250

        self.window = tk.Tk()

        # get screen width and height
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()

        # calculate x and y coordinates for the Tk window
        x = (ws/2) - (width/2)
        y = (hs/2) - (height/2)

        #Initialize window
        self.window.tk.call('source', './Azure/azure.tcl')
        self.window.tk.call("set_theme", "dark")
        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.window.title('Nice Tabs')
        self.window.resizable(False,False)

        #GUI user options
        self.generate_tex = IntVar()

        #Instantiate elements
        greeting = ttk.Label(text="Paste an ultimate guitar link in the box and hit \"Create\" to create and save a tab as a PDF.\n\n Example: https://tabs.ultimate-guitar.com/tab/darius-rucker/wagon-wheel-chords-1215756\n")
        entry_button = ttk.Button(text="Create")
        
        message_text = StringVar()
        message_field = ttk.Label(textvariable=message_text)

        entryText = StringVar()
        entry_button.configure(command=lambda: threading.Thread(target=lambda: tab_converter.convert(self.generate_tex,entryText,message_text)).start())
        self.entry = ttk.Entry(width=80, textvariable=entryText)
        self.entry.bind('<Return>',lambda: threading.Thread(target=lambda: tab_converter.convert(self.generate_tex,entryText,message_text)).start())
        check = ttk.Checkbutton(text='Generate .tex file',variable=self.generate_tex,onvalue=False,offvalue=True,)
        check.invoke()#Make sure the box starts unticked

        #Pack elements (order matters!)
        ttk.Label().pack()
        greeting.pack()
        self.entry.pack()
        ttk.Label().pack()
        entry_button.pack()
        check.pack()
        message_field.pack()

        self.window.mainloop()
