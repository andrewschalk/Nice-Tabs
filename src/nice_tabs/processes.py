from selenium import webdriver
from bs4 import BeautifulSoup
from pylatex import Document
from pylatex.package import Package
from pylatex.utils import NoEscape
from tkinter import messagebox
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from tkinter.filedialog import asksaveasfilename
from pdflatex import PDFLaTeX
from subprocess import CREATE_NO_WINDOW
import subprocess

import traceback
import os
import pylatex.config as cf

class TabConverter():
    """Retreives data from webpage and creates a PDF.
    The data is scraped from the given URL. The data is then packed into a .tex file.
    The user can choose whether to keep the .tex file using a checkbox.
    The user is then prompted for where to save the file and the file is saved.
    """
    global is_converting
    is_converting = False#False when application is idle, True when converting

    def __init__(self,message_manager):
        """
        :param message_manager (MessageManager): The current instance of MessageManager.
        """
        self.message_manager = message_manager


    def _get_website(self):
        """Retreives the webpage from the given URL.
        Here we use Microsoft Edge as our browser because every Windows user should have this.
        """
        self.message_manager.set_message('Downloading webpage',True,self.message_text)
        
        options = webdriver.EdgeOptions()
        options.add_argument('--ignore-certificate-errors')#Don't show these errors as we don't care
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--headless=new')#Run in headless mode. '=new' fixes massive download time issue
        options.add_argument('--window-size=1920,1200')

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
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        #The driver manager will download the necessary drivers for the version of Edge installed on the system.
        edge_service = EdgeService(EdgeChromiumDriverManager().install())
        edge_service.creation_flags = CREATE_NO_WINDOW
        self.driver = webdriver.Edge(service=edge_service,options=options)
        self.driver.get(self.URL)
        self.message_manager.clear_message()
        return True
        
    def _process_HTML(self):
        """Processes HTML page after we grab it from the website."""
        self.message_manager.set_message("Generating PDF",True,self.message_text)
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            self.driver.quit()#We've downloaded all needed data, close driver

            tab_lines  = soup.find_all('span', class_='y68er')#Each line of tab is one of these
            self.title = soup.find('h1',class_='dUjZr').text
            artist     = soup.find('a',class_='aPPf7 fcGj5')
        except:
            self.message_manager.clear_message()
            messagebox.showinfo('Issue!',"Something is wrong with the URL you entered. Please try again.")
            return False

        cf.active = cf.Version1(indent=False)

        self.doc = Document('basic')

        self.doc.preamble.append(Package('geometry','margin=0.5in'))
        self.doc.preamble.append(NoEscape('\setlength{\parskip}{-.4em}'))
        self.doc.preamble.append(NoEscape('\pagenumbering{gobble}'))
        self.doc.preamble.append(Package('needspace'))
        self.doc.preamble.append(Package('courier'))
        self.doc.preamble.append(NoEscape('\\renewcommand*\\familydefault{\\ttdefault}'))

        try:#An exception here could mean that the user entered a URL that gives a page that doesn't have the expected HTML elements.
            self.doc.append(NoEscape('\\begin{center}\\begin{large}'+self.title.replace('Chords','').replace('Tab','')+'\\end{large}\\\\by '+artist.text+'\\end{center}\\vspace{1em}'))
        except:
            self.message_manager.clear_message()
            messagebox.showinfo('Issue!',"Something may be wrong with the URL you entered. Please try again.")
            return False

        for tab_line in tab_lines:
            """"This is all the formatting for the lines of the tab. This determines how each line is placed"""
            if len(tab_line.text) <4:
                self.doc.append(NoEscape('\\vspace{1em}'))
            else:
                if '[' in tab_line.text:#If a [verse] or [chorus] line, then give this line some vertical space and don't let page break here.
                    self.doc.append(NoEscape('\\vspace{.4em}'))
                    self.doc.append(NoEscape('\\par\\needspace{2\\baselineskip}'))
                else:
                    if (tab_line.text.count(' ')>len(tab_line.text)/2) or len(tab_line.text)<5:# If this line is a "chord" line then give it some space above.
                        self.doc.append(NoEscape('\\par\\needspace{\\baselineskip}'))
                        self.doc.append(NoEscape('\\vspace{.6em}'))

                #Replaces all special characters with their LaTeX display codes. Otherwise latex treats them as markup and not text.
                self.doc.append(NoEscape(tab_line.text.replace('\\','\\textbackslash').replace(' ','\space ').replace('#','\\#').replace('_','\\_').replace('-','-{}')))
        self.message_manager.clear_message()
        return True

    def _save_file(self):
        """Prompts the user where to save the file. Then saves the file."""
        file = asksaveasfilename(defaultextension = '.pdf',initialfile=self.title,filetypes=[("PDF Doc", "*.pdf")])
        self.message_manager.set_message("Saving file(s)",True,self.message_text)
        if file:#If user selected a file path
            try:#Will usually fail if LaTeX compiler failed. Could also fail if saveas path is wrong.
                self.doc.generate_pdf(file.replace('.pdf',''),compiler='D:\\ProgrammingProjects\\Nice-Tabs\\TinyTex\\bin\\windows\\pdflatex.exe',clean_tex=self.generate_tex)
                self.message_manager.set_message("File(s) saved. You may exit the application or continue generating files.",False,self.message_text)
            except:
                print(traceback.format_exc())
                self.message_manager.clear_message()
                messagebox.showerror("Fatal Error","Something went wrong trying to render or save PDF. \n\n"+traceback.format_exc())
        else:
            self.message_manager.clear_message()
            messagebox.showinfo("File Not Saved","Please select a file location. Click \"Create\" again to select location.")
        return True

    def convert(self,generate_tex,entry_text,message_text):
        """Retreives, processes, and saves the tab given by the user.
        :param generate_tex (IntVar)   : Determines whether a .tex file will be generated.
        :param entry_text   (StringVar): The variable that holds the value in the entry field
        :param message_text (StringVar): The variable that holds the current user message.
        """
        self.URL          = entry_text.get()
        self.message_text = message_text
        global is_converting
        if is_converting:
            return False
        
        self.generate_tex = generate_tex
        try:
            is_converting = True#We are no longer idle
        
            if 'tabs.ultimate-guitar.com' not in self.URL:#If not ultimate guitar website
                messagebox.showinfo('Issue!',"The URL must link to an Ultimate Guitar tab or chords page.")
                is_converting = False
                return False
            
            if not self._get_website():
                return
            if not self._process_HTML():
                return
            if not self._save_file():
                return

            is_converting = False#We're done converting; back to idle.
            
        except:#If anything unexpected happens, throw error window with stacktrace
            messagebox.showerror("Fatal Error!","Something went wrong!\n"+traceback.format_exc())
            print(traceback.format_exc())
            self.message_manager.clear_message()
        finally:
            try:
                self.driver.quit()
            except:
                pass
            is_converting = False
