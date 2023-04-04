from selenium import webdriver
from bs4 import BeautifulSoup
from pylatex import Document
import pylatex.config as cf
from pylatex.package import Package
from pylatex.utils import NoEscape
import tkinter as tk
from tkinter import IntVar, messagebox,ttk
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename
import threading
from threading import Event
import time
import os,sys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from subprocess import CREATE_NO_WINDOW
import traceback

""" Nice Tabs
This program allows a user to convert an Ultimate Guitar webpage containing a tab to a clean printable PDF.
Selenium scrapes the data from the given page and they are processed with Beautiful Soup.
The data are formatted and sent to a LaTeX compiler which creates the PDF.
Utilizing the Azure dark theme for tkk, a simple GUI is displayed.

Copyright 2023 Andrew Schalk

         /\  __
        /--\/  \
       /    \__
               \
            \__/
      
"""
isConverting = False#False when application is idle, True when converting

#os.chdir(sys._MEIPASS)#Uncomment for .exe deployment

class GUI:
    """Creates the window that contains the GUI and its components. Uses tkk with Azure dark theme."""
    def __init__(self,convertCommand):
        self.generateTex = False
        width  = 600
        height = 250

        window = tk.Tk()

        # get screen width and height
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()

        # calculate x and y coordinates for the Tk window
        x = (ws/2) - (width/2)
        y = (hs/2) - (height/2)

        #Initialize window
        window.tk.call('source', './Azure/azure.tcl')
        window.tk.call("set_theme", "dark")
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))
        window.title('Nice Tabs')
        window.resizable(False,False)

        #GUI user options
        generateTex = IntVar()

        #Instantiate elements
        greeting    = ttk.Label(text="Paste an ultimate guitar link in the box and hit \"Create\" to create and save a tab as a PDF.\n\n Example: https://tabs.ultimate-guitar.com/tab/darius-rucker/wagon-wheel-chords-1215756\n")
        button = ttk.Button(text="Create")
        button.configure(command=convertCommand)
        entry  = ttk.Entry(width=80)
        entry.configure('<Return>',convertCommand)
        check       = ttk.Checkbutton(text='Generate .tex file',variable=generateTex,onvalue=False,offvalue=True,)
        check.invoke()#Make sure the box starts unticked

        #Pack elements (order matters!)
        ttk.Label().pack()
        greeting.pack()
        entry.pack()
        ttk.Label().pack()
        button.pack()
        check.pack()
        window.mainloop()#Create window

    def setCommand(self,convertCommand):
        #self.entry.configure('<Return>',convertCommand)
        print(self.button)
        self.button.configure(command=convertCommand)
        
    

class TabConverter:
    """Retreives the data and creates a PDF.
    The data is scraped from the given URL. The data is then packed into a .tex file.
    The user can choose whether to keep the .tex file using a checkbox.
    The user is then prompted for where to save the file and the file is saved.
    """
    global driver,doc,title,generateTex

    def __init__(self):
        pass

    def getWebsite():
        URL = entry.get()

        options = webdriver.EdgeOptions()
        options.add_argument('--ignore-certificate-errors')#Don't show these errors as we don't care
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--headless=new')#Run in headless mode. '=new' fixes massive download time issue
        options.add_argument("--window-size=1920,1200")

        #Don't download unnecessary GUI data
        prefs = {"profile.managed_default_content_settings.images":2,
         "profile.default_content_setting_values.notifications":2,
         "profile.managed_default_content_settings.stylesheets":2,
         "profile.managed_default_content_settings.cookies":2,
         "profile.managed_default_content_settings.javascript":1,
         "profile.managed_default_content_settings.plugins":1,
         "profile.managed_default_content_settings.popups":2,
         "profile.managed_default_content_settings.geolocation":2,
         "profile.managed_default_content_settings.media_stream":2,
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()),options=options)

        try:#Let's try to contact the given webpage.
            driver.get(URL)
        except:
            messagebox.showinfo("Issue!","Something is wrong with the URL you entered.")
            driver.quit()
            isConverting = False
            return
    def processHTML(driver):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()#We've downloaded all needed data, close driver
        tabLines = soup.find_all("span", class_="y68er")#Each line of tab is one of these
        title  = soup.find("h1",class_="dUjZr").text
        artist = soup.find("a",class_="aPPf7 fcGj5")

        cf.active = cf.Version1(indent=False)
        doc = Document('basic')
        doc.preamble.append(Package('geometry','margin=0.5in'))
        doc.preamble.append(NoEscape('\setlength{\parskip}{-.4em}'))
        doc.preamble.append(NoEscape('\pagenumbering{gobble}'))
        doc.preamble.append(Package('needspace'))
        doc.preamble.append(Package('courier'))
        doc.preamble.append(NoEscape('\\renewcommand*\\familydefault{\\ttdefault}'))

        try:
            doc.append(NoEscape('\\begin{center}\\begin{large}'+title.replace('Chords','').replace('Tab','')+'\\end{large}\\\\by '+artist.text+'\\end{center}\\vspace{1em}'))
        except:
            messagebox.showinfo("Issue!","Something may be wrong with the URL you entered. Please try again.")
            isConverting = False
            return

        for tabLine in tabLines:
            """"This is all the formatting for the lines of the tab. This determines how each line is placed"""
            if len(tabLine.text) <4:
                doc.append(NoEscape('\\vspace{1em}'))
            else:
                space_count = 0
                if '[' in tabLine.text:
                    doc.append(NoEscape('\\vspace{.4em}'))
                    doc.append(NoEscape('\\par\\needspace{2\\baselineskip}'))
                else:
                    if (tabLine.text.count(' ')>len(tabLine.text)/2) or len(tabLine.text)<5:
                        doc.append(NoEscape('\\par\\needspace{\\baselineskip}'))
                        doc.append(NoEscape('\\vspace{.6em}'))
                doc.append(NoEscape(tabLine.text.replace('\\','\\textbackslash').replace(' ','\space ').replace('#','\\#').replace('_','\\_').replace('-','-{}')))

    def saveFile():
        file = asksaveasfilename(defaultextension = '.pdf',initialfile=title,filetypes=[("PDF Doc", "*.pdf")])
        if file:#If user selected a file path
            try:#Will usually fail if LaTeX compiler failed. Could also fail if saveas path is wrong.
                doc.generate_pdf(file.replace('.pdf',''),clean_tex=generateTex.get(),compiler='venv/Lib/site-packages/pdflatex-0.1.3.dist-info')
                threading.Thread(target=saved).start()
            except:
                messagebox.showerror("Error","Something went wrong trying to render or save PDF. \n\n"+traceback.format_exc())
        else:
            messagebox.showinfo("File Not Saved","Please select a file location. Click \"Create\" again to select location.")

    def convert(self,generateTex):
        self.generateTex = generateTex
        try:
            isConverting = True#We are no longer idle
        
            if 'tabs.ultimate-guitar.com' not in entry.get():#If not ultimate guitar website
                messagebox.showinfo("Issue!","The URL must link to an Ultimate Guitar tab or chords page.")
                isConverting = False
                return
        
            self.getWebsite()
            self.processHTML()
            self.saveFile()
            isConverting = False#We're done converting; back to idle.
        except:#If anything unexpected happens, throw error window with stacktrace
            messagebox.showerror("Error!","Something went wrong!\n"+traceback.format_exc())
            print(traceback)
            driver.quit()
            isConverting = False

def runConverterAsThread(event=None):
    """Creates a new thread to run the conversion process in."""
    global myGUI
    if not isConverting:#Only start conversion if idle
        threading.Thread(target=myConverter.convert(myGUI.generateTex)).start()

def saved():
    """Creates text at bottom of window telling user that file was saved. Disappears after 10 seconds"""
    time.sleep(.2)
    global savedLabel1, entry, savedLabel2
    entry.delete(0,END)
    savedLabel1 = ttk.Label(text=title + ' saved.')
    savedLabel1.pack()
    savedLabel2 = ttk.Label(text='You may exit the application or continue generating files.')
    savedLabel2.pack()
    time.sleep(10)
    savedLabel1.pack_forget()
    savedLabel2.pack_forget()

def loadingBar(str,event):
    """Creates a simple loading animation along with the given text.
    :param str The message to display to the user while they wait.
    :param event The Event object that will be called when loading is finished.
    """
    time.sleep(.2)#Allows for previous message to clear before displaying this one.
    loading = ttk.Label()
    loading.pack()
    waitTime =.3
    
    i=0
    dots=''
    while not event.is_set():#Adds 0 to 3 dots incrementally at the end of the string with a pause between them
        loading.config(text=str+dots)
        time.sleep(waitTime)
        dots=dots+'.'
        i+=1
        if i == 4:
            i=0
            dots=''
    loading.pack_forget()
    
myConverter = TabConverter()
myGUI = GUI(runConverterAsThread)
#myGUI.setCommand(runConverterAsThread)