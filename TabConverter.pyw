from selenium import webdriver
from bs4 import BeautifulSoup
from pylatex import Document
import pylatex.config as cf
from pylatex.package import Package
from pylatex.utils import NoEscape
from tkinter import messagebox
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from tkinter.filedialog import asksaveasfilename
import traceback

class TabConverter():
    """Retreives the data and creates a PDF.
    The data is scraped from the given URL. The data is then packed into a .tex file.
    The user can choose whether to keep the .tex file using a checkbox.
    The user is then prompted for where to save the file and the file is saved.
    """
    global isConverting
    isConverting = False#False when application is idle, True when converting

    def __init__(self,messageManager):
        """
        :param messageManager (MessageManager): The current instance of MessageManager.
        """
        self.messageManager = messageManager
        isConverting = False


    def _getWebsite(self):
        """Retreives the webpage from the given URL."""
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

        self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()),options=options)
        self.driver.get(self.URL)
        
    def _processHTML(self):
        """Processes HTML page after we grab it from the website."""
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.driver.quit()#We've downloaded all needed data, close driver
            tabLines = soup.find_all("span", class_="y68er")#Each line of tab is one of these
            self.title = soup.find("h1",class_="dUjZr").text
            artist = soup.find("a",class_="aPPf7 fcGj5")
        except:
            messagebox.showinfo("Issue!","Something is wrong with the URL you entered.")
            self.driver.quit()
            isConverting = False
            return

        cf.active = cf.Version1(indent=False)
        self.doc = Document('basic')
        self.doc.preamble.append(Package('geometry','margin=0.5in'))
        self.doc.preamble.append(NoEscape('\setlength{\parskip}{-.4em}'))
        self.doc.preamble.append(NoEscape('\pagenumbering{gobble}'))
        self.doc.preamble.append(Package('needspace'))
        self.doc.preamble.append(Package('courier'))
        self.doc.preamble.append(NoEscape('\\renewcommand*\\familydefault{\\ttdefault}'))

        try:
            self.doc.append(NoEscape('\\begin{center}\\begin{large}'+self.title.replace('Chords','').replace('Tab','')+'\\end{large}\\\\by '+artist.text+'\\end{center}\\vspace{1em}'))
        except:
            messagebox.showinfo("Issue!","Something may be wrong with the URL you entered. Please try again.")
            isConverting = False
            return

        for tabLine in tabLines:
            """"This is all the formatting for the lines of the tab. This determines how each line is placed"""
            if len(tabLine.text) <4:
                self.doc.append(NoEscape('\\vspace{1em}'))
            else:
                space_count = 0
                if '[' in tabLine.text:
                    self.doc.append(NoEscape('\\vspace{.4em}'))
                    self.doc.append(NoEscape('\\par\\needspace{2\\baselineskip}'))
                else:
                    if (tabLine.text.count(' ')>len(tabLine.text)/2) or len(tabLine.text)<5:
                        self.doc.append(NoEscape('\\par\\needspace{\\baselineskip}'))
                        self.doc.append(NoEscape('\\vspace{.6em}'))
                self.doc.append(NoEscape(tabLine.text.replace('\\','\\textbackslash').replace(' ','\space ').replace('#','\\#').replace('_','\\_').replace('-','-{}')))

    def _saveFile(self):
        """Prompts the user where to save the file. Then saves the file."""
        file = asksaveasfilename(defaultextension = '.pdf',initialfile=self.title,filetypes=[("PDF Doc", "*.pdf")])
        if file:#If user selected a file path
            try:#Will usually fail if LaTeX compiler failed. Could also fail if saveas path is wrong.
                self.doc.generate_pdf(file.replace('.pdf',''),clean_tex=self.generateTex.get(),compiler='venv/Lib/site-packages/pdflatex-0.1.3.dist-info')
            except:
                messagebox.showerror("Error","Something went wrong trying to render or save PDF. \n\n"+traceback.format_exc())
        else:
            messagebox.showinfo("File Not Saved","Please select a file location. Click \"Create\" again to select location.")

    def convert(self,generateTex,entryText,messageText):
        """Retreives, processes, and saves the tab given by the user.
        :param generateTex (boolean): Determines whether a .tex file will be generated.
        :param entryText (StringVar): The variable that holds the value in the entry field
        :param messageText (StringVar): The variable that holds the current user message.
        """
        self.URL = entryText.get()
        global isConverting
        if isConverting:
            return
        
        self.generateTex = generateTex
        try:
            isConverting = True#We are no longer idle
        
            if 'tabs.ultimate-guitar.com' not in self.URL:#If not ultimate guitar website
                messagebox.showinfo("Issue!","The URL must link to an Ultimate Guitar tab or chords page.")
                isConverting = False
                return
            self.messageManager.addMessage('Downloading webpage',True,messageText)
            self._getWebsite()
            self.messageManager.addMessage('Generating PDF',True,messageText)
            self._processHTML()
            self.messageManager.clearMessage()
            self._saveFile()
            self.messageManager.addMessage('File(s) saved. You may exit the application or continue generating files.',False,messageText)
            isConverting = False#We're done converting; back to idle.
            
        except:#If anything unexpected happens, throw error window with stacktrace
            messagebox.showerror("Error!","Something went wrong!\n"+traceback.format_exc())
            self.driver.quit()
            self.messageManager.clearMessage()
            isConverting = False
