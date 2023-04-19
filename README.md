# Nice Tabs
<p>
<img alt="GitHub" src="https://img.shields.io/github/license/andrewschalk/Nice-Tabs"/>
  </p>
A GUI based application that allows users to download Ultimate Guitar tabs into a clean printable PDF.

## Installation Instructions
The runnable .exe is still a work in progress and is currently flagged as a virus by windows defender. To run the program you will need to first clone the repository in your favorite Python IDE and then follow these steps. Requires Python 3.
1. Create virtual environment in the repository's root directory: ```python venv venv```
2. Activate the virtual environment and select the virtual environment's python interpreter: Many IDEs will do this automatically when you start a new terminal after creating a virtual environment. The best way to do this will vary based on your IDE.
3. Install required modules to virtual environment:```pip install -r requirements.txt``` and ```pip install pdflatex```(This will throw an error at the moment, which I'm working on fixing, but it can safely be ignored.)
4. Run: /src/nice_tabs/main.py

### Usage
Simply paste a Ultimate Guitar Tabs URL into the box and hit "create". You will be prompted where to save your PDF.


If the "generate .tex" checkbox is selected, a .tex file of the same name as the PDF will be generated. This allows users with a LaTeX compiler to edit the output. (Note that the .tex file is not very human friendly)

If you run into any issues while running the program, please open an issue. Pull requests are appreciated.

## An example output

![An example output](ExampleTab.PNG)
