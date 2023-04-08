import time
import threading
from threading import Event

class MessageManager():
    
    def __init__(self):
        pass
    
    def _loadingBar(self):
        """Creates a simple loading animation along with the given text.
        :param str (String): The message to display to the user while they wait.
        :param event (Event): The Event object that will be called when loading is finished.
        """
        time.sleep(.1)#Allows the previous thread to see that the event was set before clearing
        self.event.clear()
        i=0
        dots=''
        while not self.event.is_set():#Adds 0 to 3 dots incrementally at the end of the string with a pause between them
            self.messageText.set(self.str+dots)
            time.sleep(.3)
            dots=dots+'.'
            i+=1
            if i == 4:
                i=0
                dots=''
        
    def clearMessage(self):
        try:#Sometimes the Event object may not yet be initialized. In this case, there is no message, so no need to clear.
            self.event.set()
            self.messageText.set('')
        except:
            pass
            
    
    def addMessage(self,str,isLoading,messageText):
        self.clearMessage()
        self.str = str
        self.messageText = messageText
        self.event = Event()
        if isLoading:
            threading.Thread(target=self._loadingBar).start()
