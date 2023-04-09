import time
import threading
from threading import Event

class MessageManager():
    """Manages the messages that are displayed to the user via GUI()."""
    
    def __init__(self):
        self.events =[]
    
    def _loadingBar(self,event):
        """Creates a simple loading animation along with the given text.
        :param str (String): The message to display to the user while they wait.
        :param event (Event): The Event object that will be called when loading is finished.
        """
        time.sleep(.1)#Allows the previous message to clear the screen
        #event.clear()
        i=0
        dots=''
        while not event.is_set():#Adds 0 to 3 dots incrementally at the end of the string with a pause between them
            self.messageText.set(self.str+dots)
            time.sleep(.3)
            dots=dots+'.'
            i+=1
            if i == 4:
                i=0
                dots=''
        
    def clearMessage(self):
        """Clears the message currently being displayed."""
        try:#Sometimes the Event object may not yet be initialized. In this case, there is no message, so no need to clear.
            for event in self.events:
                event.set()
                self.messageText.set('')
        except:
            pass
            
    def setMessage(self,str,isLoading,messageText):
        """Sets the message to be displayed to the user
        :param str (String): The message to be displayed
        :param isLoading (Boolean): Sets whether the message is accompanied by a loading animation.
        :param messageText (StringVar): The textvariable that is linked to the Label which displays the message.
        """
        self.clearMessage()
        self.str = str
        self.messageText = messageText
        event = Event()
        self.events.append(event)
        if isLoading:
            threading.Thread(target=lambda: self._loadingBar(event)).start()
        else:
            self.messageText.set(str)
