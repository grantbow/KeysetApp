#!/usr/bin/python

import kivy
kivy.require('1.10.0')

# via kivy.org/docs/guide/basic.html#quickstart

from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import  NumericProperty, \
    ObjectProperty, \
    StringProperty, \
    OptionProperty, \
    BooleanProperty
#import ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
#from kivy.lang.builder import Builder # automatic
#Builder.load_file('keyset.kv') # automatic

#from kivy.input.providers.mouse import MouseMotionEventProvider

#import pdb

#from kivy.config import Config
#Config.set('graphics', 'fullscreen', '0') # for pi 3 auto didn't work due to DSI touch screen

from kivy.uix.screenmanager import ScreenManager, Screen

fingerkeylist = []
modkeylist = []

# on-screen widgets

class ReadyDisplay(Label):
    '''result of FingerKeys

    Values are assigned
    '''
    text = StringProperty('')
    val = NumericProperty(None)
    app = App.get_running_app()

    def val_finger_clear(self):
        self.text=''
        self.val = 0
        global fingerkeylist
        for finger in fingerkeylist:
            if finger.state == 'normal':
                finger.chord_pressed = 0

    def on_val(self, *args):
        # self.val is the sum of keys pressed
        # ascii_val is computed
        mod_val = int(0)
        ascii_val = int(0)
        global modkeylist
        if self.val:
            #indicator_text = '        '
            # modifiers first
            #pdb.set_trace()
            for modkey in modkeylist:
                if modkey.state == 'down':
                    mod_val = int(round(modkey.val))
                    #if mod_val == 32:
                        #indicator_text = ' +Shi   '
                    #elif mod_val == 64:
                        #indicator_text = '    +Num'
            ascii_val = int(round(self.val + 96 - mod_val))
            # self.val + 96      (net 96) gets ascii lower case
            # self.val + 96 - 32 (net 64) gets ascii upper case
            # self.val + 96 - 64 (net 32) gets ascii symbols and numbers

            # num swap except <SP> and 0 (zero)
            if ascii_val > 32 and ascii_val < 48:
                ascii_val += 16 # swap symbols to numbers
            elif ascii_val > 48 and ascii_val < 64:
                ascii_val -= 16 # swap numbers to symbols

            #self.text = str(chr(ascii_val)) + '   : ' + str(self.val) + indicator_text +' ; ascii ' + str(ascii_val) +':' +str(debug)+':'+str(mod_val)+':'
            if ascii_val == 127:
                self.text = "<del>"
            else:
                self.text = str(chr(ascii_val))
                      
        else:
            self.text = ''
        

class ModKey(ToggleButton):
    '''chording key modifier in kv lang file

    Modify key values
    '''
    val = NumericProperty(None)
    state = OptionProperty('normal', options=['normal','down'])
    app = App.get_running_app()

    def __init__(self, *args, **kwargs):
        global modkeylist
        modkeylist.append(self)
        ToggleButton.__init__(self, *args, **kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ready_display.text = str(chr(int(round(self.ready_display.val + 96 - self.val))))
        return super(ModKey, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.ready_display.text = str(chr(int(round(self.ready_display.val + 96 - self.val))))
        return super(ModKey, self).on_touch_down(touch)


class PressKey(Button):
    '''special key in kv lang file

    Ascii Values are assigned
    '''
    state = OptionProperty('normal', options=['normal','down'])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ready_display.text = self.flash_text
        return super(Button, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) or self.state == 'down':
            self.ready_display.val_finger_clear()
        return super(Button, self).on_touch_up(touch)


class FingerKey(Button):
    '''chording key in kv lang file

    Values are assigned
    '''
    chord_pressed = 0
    val = NumericProperty(None)
    ready_display = ObjectProperty(None)
    state = OptionProperty('normal', options=['normal','down'])

    def __init__(self, *args, **kwargs):
        global fingerkeylist
        fingerkeylist.append(self)
        Button.__init__(self, *args, **kwargs)

    def chording(self):
        retval = 0
        global fingerkeylist
        #pdb.set_trace()
        for finger in fingerkeylist:
            if finger.chord_pressed:
                retval = 1
        return retval

    def downing(self):
        retval = 0
        global fingerkeylist
        #pdb.set_trace()
        for finger in fingerkeylist:
            if finger.state == 'down':
                retval = 1
        return retval

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.chord_pressed == 0:
                self.chord_pressed = 1
                self.ready_display.val += self.val
        return super(FingerKey, self).on_touch_down(touch)

    def on_touch_up(self, touch, after=False):
        if after:
            if self.collide_point(*touch.pos):
                self.chord_pressed = 0
                global fingerkeylist
                if not self.chording() or not self.downing():
                    # last finger up
                    self.ready_display.val = 0
                    for finger in fingerkeylist:
                        finger.chord_pressed = 0
                else:
                    self.chord_pressed = 1
        else:
            Clock.schedule_once(lambda dt: self.on_touch_up(touch,True))
            return super(FingerKey, self).on_touch_up(touch)


# root widget & ascii screen

class Keyset(Screen):
    '''Create a controller that receives a custom widget from the kv lang file

    Adds actions to the keys
    '''
    pass


class AsciiScreen(Screen):
    pass


# app

class KeysetApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Keyset(name='keysetscr'))
        sm.add_widget(AsciiScreen(name='ascii'))
        return sm


if __name__ == '__main__':
    KeysetApp().run()

