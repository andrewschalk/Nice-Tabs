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
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW

""" Nice Tabs
This program allows a user to convert an Ultimate Guitar webpage containing a tab to a clean printable PDF.
Selenium scrapes the data from the given page and they are processed with Beautiful Soup.
The data are formatted and sent to a LaTeX compiler which creates the PDF.
Utilizing the dark Azure theme for tkk, a simple GUI is displayed.

Copyright 2023 Andrew Schalk
"""

#GUI user options
generateTex = IntVar()

#Events for threads
loadingEvent = Event()
loadingEvent2 = Event()
isConverting = False

#os.chdir(sys._MEIPASS)#Uncomment for .exe deployment


def GUI():
    """Creates the window that contains the GUI and its components. Uses tkk with Azure dark theme."""
    #Initialize window
    window = tk.Tk()
    window.tk.call('source', './Azure/azure.tcl')
    window.tk.call("set_theme", "dark")
    window.geometry('600x240')
    window.title('Nice Tabs')

    #Instantiate elements
    greeting = ttk.Label(text="Paste an ultimate guitar link in the box and hit \"Create\" to create and save a tab as a PDF.\n\n Example: https://tabs.ultimate-guitar.com/tab/darius-rucker/wagon-wheel-chords-1215756\n")
    button = ttk.Button(text="Create",command=runConverterAsThread)
    entry = ttk.Entry(width=80)
    check = ttk.Checkbutton(text='Generate .tex file',variable=generateTex,onvalue=False,offvalue=True,)
    check.invoke()#Make sure the box starts unticked

    #Pack elements (order matters!)
    ttk.Label().pack()
    greeting.pack()
    entry.pack()
    ttk.Label().pack()
    button.pack()
    check.pack()

    window.mainloop()#Create window

def tabConverter():
    """Retreives the data and creates a PDF.
    The data is scraped from the given URL. The data is then packed into a .tex file.
    The user can choose whether to keep the .tex file, with a checkbox.
    The user is then prompted for where to save the file and the file is saved.
    """
    global isConverting, savedLabel
    loadingEvent2.clear()
    loadingEvent.clear()
    try:
        try:
            savedLabel.pack_forget()
        except:
            pass
        isConverting = True
        threading.Thread(target=loadingBar,args=('Downloading webpage',loadingEvent2)).start()
        if 'tabs.ultimate-guitar.com' not in entry.get():
            loadingEvent.set()
            loadingEvent2.set()
            messagebox.showinfo("Issue!","The URL must link to an Ultimate Guitar site.")
            isConverting = False
            return
        URL = entry.get()
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--window-size=1920,1200")
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

        chromeService = Service('chromedriver.exe')
        chromeService.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(options=options, service=chromeService)
        try:
            driver.get(URL)
        except:
            messagebox.showinfo("Issue!","Something is wrong with the URL you entered.")
            loadingEvent.set()
            driver.quit()
            isConverting = False
            return
        loadingEvent2.set()
        threading.Thread(target=loadingBar,args=('Generating file',loadingEvent)).start()
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        job_elements = soup.find_all("span", class_="y68er")
        title = soup.find("h1",class_="dUjZr")
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
            doc.append(NoEscape('\\begin{center}\\begin{large}'+title.text.replace('Chords','').replace('Tab','')+'\\end{large}\\\\by '+artist.text+'\\end{center}\\vspace{1em}'))
        except:
            loadingEvent.set()
            messagebox.showinfo("Issue!","Something is wrong with the URL you entered.")
            isConverting = False
            return

        for job_element in job_elements:
            if len(job_element.text) <4:
                doc.append(NoEscape('\\vspace{1em}'))
            else:
                space_count = 0
                if '[' in job_element.text:
                    doc.append(NoEscape('\\vspace{.4em}'))
                    doc.append(NoEscape('\\par\\needspace{2\\baselineskip}'))
                else:
                    if (job_element.text.count(' ')>len(job_element.text)/2) or len(job_element.text)<5:
                        doc.append(NoEscape('\\par\\needspace{\\baselineskip}'))
                        doc.append(NoEscape('\\vspace{.6em}'))
                doc.append(NoEscape(job_element.text.replace('\\','\\textbackslash').replace(' ','\space ').replace('#','\\#').replace('_','\\_').replace('-','-{}')))
        loadingEvent.set()
        file = asksaveasfilename(defaultextension = '.pdf',initialfile=title.text,filetypes=[("PDF Doc", "*.pdf")])
        print(file)
        if file:
            try:
                loadingEvent.clear()
                threading.Thread(target=loadingBar,args=('Rendering and saving file',loadingEvent)).start()
                doc.generate_pdf(file.replace('.pdf',''),clean_tex=generateTex.get(),compiler='pdflatex')
                loadingEvent.set()
                threading.Thread(target=saved).start()
            except:
                loadingEvent.set()
                messagebox.showerror("Error","Something went wrong trying to render PDF. \nThere may be something wrong with how this program interprets the given tab.")
        else:
            messagebox.showinfo("File Not Saved","Please select a file location. Click \"Create\" again to select location.")
            loadingEvent.set()
        isConverting = False
    except Exception as e:
        messagebox.showerror("Error!","Something went wrong!\n"+str(e))
        loadingEvent.set()
        driver.quit()
        isConverting = False
        loadingEvent2.set()

def runConverterAsThread():
    """Creates a new thread to run the conversion process in."""
    if not isConverting:#Only start conversion if idle
        threading.Thread(target=tabConverter).start()
        loadingEvent.clear()#Nothing is loading anymore so clear any loading animation

def saved():
    """Creates text at bottom of window telling user that file was saved. Disappears after 10 seconds"""
    time.sleep(.2)
    global savedLabel,entry
    entry.delete(0,END)
    savedLabel = ttk.Label(text='File saved. You may exit the application or continue generating files.')
    savedLabel.pack()
    time.sleep(10)
    savedLabel.pack_forget()

def loadingBar(str,event):
    """Creates a simple loading animation with the given text.
    :param str The message to display to the user while they wait.
    :param event The Event object that will be called when loading is finished.
    """
    time.sleep(.2)#Allows for previous message to clear before displaying this one.
    loading = ttk.Label()
    loading.pack()
    waitTime =.3
    
    i=0
    dots=''
    while not event.is_set():#Adds 0 to 3 dots incrementally at the end of the string with a time between them
        loading.config(text=str+dots)
        time.sleep(waitTime)
        dots=dots+'.'
        i+=1
        if i == 4:
            i=0
            dots=''
    loading.pack_forget()
    

GUI()#Create the GUI