# Nice Tabs
<p>
<img alt="GitHub" src="https://img.shields.io/github/license/andrewschalk/Nice-Tabs"/>
  </p>
A GUI based application that allows users to download Ultimate Guitar tabs and chords into a clean printable PDF. Nice Tabs comes packaged with a compact version of LiveTeX so the user is not required to have a LaTeX compiler installed.

### Installation Instructions
Tested with Windows 10,11. Go to [Nice Tabs v0.3.2-alpha](https://github.com/andrewschalk/Nice-Tabs/releases/tag/v0.3.2-alpha) and download NiceTabs.exe. Windows may suggest the program is a virus, I can assure you it's not, just hit "more info" and "run anyway". Nice Tabs will take a long time to open as it unpacks temporary files, this is a work in progress.

### Developer Instructions
Tested with Windows 10,11 but should work on most systems that run python including Mac OS and Linux distros. To run the program you will need to first clone the repository in your favorite Python IDE and then follow these steps. Requires Python 3.
1. Create virtual environment in the repository's root directory: ```python -m venv venv```
2. Activate the virtual environment and select the virtual environment's python interpreter: The best way to do this will vary based on your IDE. Many IDEs will do this automatically, just start a new terminal after creating a virtual environment.
3. Install required modules to virtual environment:```pip install -r requirements.txt```
4. Run: src/nice_tabs/main.py

### Usage
Simply paste a Ultimate Guitar Tabs URL into the box and hit "create". You will be prompted where to save your PDF.

If the "generate .tex" checkbox is selected, a .tex file of the same name as the PDF will be generated. This allows users with a LaTeX compiler to edit the output. (Note that the .tex file is not very human friendly)

If you run into any issues while running the program, please open an issue. Pull requests are appreciated.

## An example output

![An example output](ExampleTab.PNG)
