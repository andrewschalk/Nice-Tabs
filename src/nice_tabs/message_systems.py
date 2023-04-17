import time
import threading
from threading import Event

class MessageManager():
    """Manages the messages that are displayed to the user via GUI()."""
    
    def __init__(self):
        self.events = []#We need a list of events because each one will be used in a different thread.
    
    def _loading_bar(self,event):
        """Creates a simple loading animation along with the given text.
        :param str   (String): The message to display to the user while they wait.
        :param event (Event) : The Event object that will be called when loading is finished.
        """
        time.sleep(.1)#Allows the previous message to clear the screen

        i=0
        dots=''
        while not event.is_set():#Adds 0 to 3 dots incrementally at the end of the string with a pause between them
            self.message_text.set(self.str+dots)
            time.sleep(.3)
            dots = dots+'.'
            i+=1
            if i == 4:
                i = 0
                dots = ''
        
    def clear_message(self):
        """Clears the message currently being displayed."""
        try:#Sometimes the Event object may not yet be initialized. In this case, there is no message, so no need to clear.
            for event in self.events:
                event.set()
                self.message_text.set('')
            self.events = []
        except:
            pass
            
    def set_message(self,str,is_loading,message_text):
        """Sets the message to be displayed to the user
        :param str          (String)   : The message to be displayed
        :param is_loading   (Boolean)  : Sets whether the message is accompanied by a loading animation.
        :param message_text (StringVar): The textvariable that is linked to the Label which displays the message.
        """
        self.clear_message()

        self.str          = str
        self.message_text = message_text

        if is_loading:#If is_loading, then create an animation with the text.
            event = Event()
            self.events.append(event)

            threading.Thread(target=lambda: self._loading_bar(event)).start()
        else:#Otherwise, just set the static text.
            self.message_text.set(str)
