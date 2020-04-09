#Here is some Python code to add a method "show_message_threaded" to the SenseHat object.
#The intention is to make creating menus easier.
#the gist is..
#the normal "show_message" blocks until it's done scrolling the message
#this new version scrolls in a thread so it doesn't interrupt execution of the rest of the program. If you call show_message_threaded again, it stops scrolling the previous message and waits for the thread to end (which happens pretty instantly) before starting to scroll the new message.
#there is a simplistic example included to demonstrate
#honestly I would love to see this code added to the actual library, however this get's the job done :)

from sense_emu import *
import threading
import time

def tack_show_message_threaded_onto_the_sense_hat_class():
    kill_message = False
    lock = threading.Lock()
    
    def new_show_message_implementation(
            self,
            text_string,
            scroll_speed=.1,
            text_colour=[255, 255, 255],
            back_colour=[0, 0, 0]
        ):
        """
        Scrolls a string of text across the LED matrix using the specified
        speed and colours
        """
        nonlocal kill_message
        nonlocal lock        

        # We must rotate the pixel map left through 90 degrees when drawing
        # text, see _load_text_assets
        previous_rotation = self._rotation
        self._rotation -= 90
        if self._rotation < 0:
            self._rotation = 270
        dummy_colour = [None, None, None]
        string_padding = [dummy_colour] * 64
        letter_padding = [dummy_colour] * 8
        # Build pixels from dictionary
        scroll_pixels = []
        scroll_pixels.extend(string_padding)
        for s in text_string:
            scroll_pixels.extend(self._trim_whitespace(self._get_char_pixels(s)))
            scroll_pixels.extend(letter_padding)
        scroll_pixels.extend(string_padding)
        # Recolour pixels as necessary
        coloured_pixels = [
            text_colour if pixel == [255, 255, 255] else back_colour
            for pixel in scroll_pixels
        ]
        # Shift right by 8 pixels per frame to scroll
        scroll_length = len(coloured_pixels) // 8
        for i in range(scroll_length - 8):
            if (kill_message):
                break
            start = i * 8
            end = start + 64
            self.set_pixels(coloured_pixels[start:end])
            time.sleep(scroll_speed)
        self._rotation = previous_rotation
        lock.release()
 
    def wrap_it_in_a_thread(
            self,
            text_string,
            scroll_speed=.1,
            text_colour=[255, 255, 255],
            back_colour=[0, 0, 0]
        ):
        nonlocal lock
        nonlocal kill_message
        kill_message = True
        lock.acquire()
        kill_message = False
        x = threading.Thread(target=new_show_message_implementation, args=(self, text_string, scroll_speed, text_colour, back_colour,))
        x.start()
    SenseHat.show_message_threaded = wrap_it_in_a_thread

tack_show_message_threaded_onto_the_sense_hat_class()
hat = SenseHat()
def one():
    print("one")

def two():
    print("two")

def three():
    print("three")

def quit():
    exit()

options = [
        {"message": "one", "fun": one}, 
        {"message": "two", "fun": two}, 
        {"message": "three", "fun": three},
        {"message": "quit", "fun": quit}
        ]

index = 0
while True:
    event = hat.stick.wait_for_event()
    while event.action != 'pressed':
        event = hat.stick.wait_for_event()
    if event.direction == "up":
        index = max(index - 1, 0)
    elif event.direction == "down":
        index = min(index + 1, len(options) - 1)
    elif event.direction == "middle" or event.direction == "right":
        options[index]["fun"]()
    hat.show_message_threaded(options[index]["message"])
