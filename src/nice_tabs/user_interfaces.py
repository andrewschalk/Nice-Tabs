import tkinter as tk
import threading

from tkinter import IntVar,ttk
from tkinter import *
from tkinter.ttk import *


class GUI():
    """ The graphical interface for NiceTabs. Uses the Azure dark theme for tkk."""
    
    def __init__(self,tab_converter):
        """
        :param tab_converter (TabConverter): The current instance of TabConverter
        """
        #The width and height of the window.
        width  = 600
        height = 268

        self.window = tk.Tk()

        #Get screen width and height.
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()

        #Using screen size and window size, find x and y for centering window.
        x = (ws/2) - (width/2)
        y = (hs/2) - (height/2)

        #Initialize window
        self.window.tk.call('source', './Azure/azure.tcl')
        self.window.tk.call("set_theme", "dark")
        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.window.title("Nice Tabs")
        self.window.resizable(False,False)

        #right-click paste menu for entry
        self.menu = Menu(self.window,tearoff=0)
        self.menu.add_command(label='Paste',command=self.paste)


        #Tkinter thread safe variables
        self.generate_tex = IntVar()
        message_text      = StringVar()
        message_field     = ttk.Label(textvariable=message_text,justify=CENTER)
        entryText         = StringVar()

        #Instantiate elements
        greeting     = ttk.Label(text="Paste an ultimate guitar link in the box and hit \"Create\" to create and save a tab as a PDF.\n\n Example: https://tabs.ultimate-guitar.com/tab/darius-rucker/wagon-wheel-chords-1215756\n")
        entry_button = ttk.Button(text='Create')
        check        = ttk.Checkbutton(text="Generate .tex file",variable=self.generate_tex,onvalue=False,offvalue=True)
        self.entry   = ttk.Entry(width=80, textvariable=entryText)

        #Configure elements
        entry_button.configure(command=lambda: threading.Thread(target=lambda: tab_converter.convert(self.generate_tex,entryText,message_text)).start())
        self.entry.bind('<Return>',lambda: threading.Thread(target=lambda: tab_converter.convert(self.generate_tex,entryText,message_text)).start())
        self.entry.bind('<Button-3>',self.popup)
        check.invoke()#Make sure the box starts unticked

        #Pack elements (order matters)
        ttk.Label().pack()
        greeting.pack()
        self.entry.pack()
        ttk.Label().pack()
        check.pack()
        ttk.Label().pack()
        entry_button.pack()
        message_field.pack()

        self.window.mainloop()#Infinite loop to update elements

    def popup(self,event):
        """Creates a small popup window when entry is right-clicked, to allow user to paste"""
        try:
            self.menu.tk_popup(event.x_root,event.y_root)
        finally:
            self.menu.grab_release()
    
    def paste(self):
        """Part of the right-click context window. Pastes clipboard text into entry"""
        clipboard = self.window.clipboard_get()
        self.entry.insert('end',clipboard)
