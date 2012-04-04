import json
import random
import kivy
from os import path
kivy.require('1.1.1')

from kivy.clock import Clock
from kivy.app import App
from kivy.config import Config
from kivy.graphics import Color, Ellipse, Line, Rectangle, InstructionGroup
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color

from functools import partial
import settings
from backends import Backend, Types

Builder.load_file('gamex.kv')
if not settings.DEBUG:
    Config.set('graphics', 'fullscreen', "auto")
backend = Backend()


class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.
    Add an action to be called from the kv lang file.
    '''

    types = Types
    selected = Types.FACE
    # Information of the action
    actions = {
        Types.FACE: path.join('img', 'punch.png'),
        Types.EYES: path.join('img', 'icon.png'),
        Types.EARS: path.join('img', 'punch.png'),
        Types.NOSE: path.join('img', 'punch.png'),
        Types.THROAT: path.join('img', 'punch.png'),
        Types.MOUTH: path.join('img', 'punch.png'),
    }

    # References to the database
    db = backend.get("metadata")
    index =  0
    count = db.count() - 1
    counter = 0
    current = StringProperty(db.get(index)["image"])

    # references to the paint widget of the interface
    paint = ObjectProperty(None)
    controls = ObjectProperty(None)
    new_high_score = ObjectProperty(None)
    start = ObjectProperty(None)
    navcolor = ObjectProperty((1,1,1,0))

    # keeps the possition of the current image
    x_start = 0
    y_start = 0
    prop = 1.0
    
    # these are the ellipses of the current faces 
    faces = []

    # Variables for scores
    score = NumericProperty(0)
    high_score = NumericProperty(0)

    # Make an object of the function so it can be unschedule
    _next_function = None

    def __init__(self, **kwargs):
        """ Overridint the constructor """
        super(Controller, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.calculate_starts()
        self._next_function = partial(next, self)
        Clock.schedule_once(self._next_function,settings.SECONDS_PER_IMAGE)

    def touch_down(self, paint, touch, *args):
        """ Controls when there is a touch in the screen """
        print "original: "+ str(touch.x) + ',' + str(touch.y)
        self.clock_transition()
        image_touch = self.to_image_coord(touch)
        touch = self.to_screen_coord(image_touch)
        if self.paint.collide_point(touch.x, touch.y):
            self.score += 10
            w=h=48
            icon = Image(source= self.actions[self.selected], 
                            pos=(touch.x-int(w/2.0),touch.y-int(h/2.0)), 
                            size=(w,h))
            self.paint.add_widget(icon);
            # Store 'touch' in the backend
            values = {"x": image_touch.x, "y": image_touch.y}
            Logger.info("Point: Adding (%s, %s) from image %s to %s" \
                        % (image_touch.x, image_touch.y, self.index,
                           self.selected))
            backend.get(self.selected).add(self.index, values)
            Clock.schedule_interval(partial(fade,parent=self,wdgt=icon),.01)
        else:
            for ctrl in self.controls.children:
                if ctrl.collide_point(touch.x, touch.y):
                    self.set_selected(ctrl, ctrl.action)

    def previous(self):
        """ shows the previous image and update the index """
        if self.index > 0: self.index -= 1
        else: self.index == self.count
        self.update_image()

    def set_selected(self, btn, select):
        """ set the type of game """
        self.unselect()
        self.selected = select
        btn.children[0].color = [1,1,1,1]

    def unselect(self):
        """ unselect all the options """
        for c in self.controls.children:
            c.children[0].color = [.5,.5,.5,.5]

    def next(self):
        """ shows the next image and update the index """
        if self.index < self.count: self.index += 1
        else: self.index = 0
        self.update_image()

    def update_image(self):
        """ update the image in the screen and set the counter values """
        self.clock_transition()
        self.hide_faces()
        self.increase_counter()
        self.current = self.db.get(self.index)["image"]
        self.calculate_starts()

    def clock_transition(self):
        """ clock the next transition """
        Clock.unschedule(self._next_function)
        Clock.schedule_once(self._next_function,settings.SECONDS_PER_IMAGE)

    def increase_counter(self):
        """ Increase counter for one game"""
        self.counter += 1
        if self.counter >= settings.IMAGES_PER_GAME:
            if self.score > self.high_score:
                self.high_score = self.score
                self.display_message(self.new_high_score)
                self.display_message(self.start)
            self.counter = 0
            self.score = 0

    def display_message(self, wdgt, msg=''):
        """ Display messages """
        wdgt.color = (1, 1, 1, 1)
        if not msg == '': wdgt.text = msg
        Clock.schedule_interval(partial(fade,parent=self,wdgt=wdgt,
            rate=.01),.02)

    def to_image_coord(self, touch):
        """ transforms to image coordinates """
        touch.x = int((touch.x - self.x_start) / float(self.prop))
        touch.y = ((self.height - touch.y - self.y_start) / float(self.prop))
        print "to_image: " + str(touch.x) + ',' + str(touch.y)
        return touch

    def to_screen_coord(self, touch):
        """ transforms to screen coordinates """
        touch.x = self.x_start + int(touch.x*self.prop)
        touch.y =  self.height - self.y_start - int(touch.y*self.prop)
        print "to_screen: "+ str(touch.x) + ',' + str(touch.y)
        return touch

    def _keyboard_closed(self):
        """ controls when the keyboard is closed"""
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """ with this is possible to control to show/hidden the faces """
        if keycode[1] == 's':
            self.hide_faces()
            self.show_faces()
            self.navcolor = [1,1,1,1]
            Clock.unschedule(self._next_function)
        if keycode[1] == 'h':
            self.hide_faces()
            self.navcolor = [1,1,1,0]
            Clock.schedule_once(self._next_function,settings.SECONDS_PER_IMAGE)
        return True

    def hide_faces(self):
        """ hide the faces """
        with self.paint.canvas:
            for f in self.faces:
                self.paint.canvas.remove(f)
            self.faces = []

    def calculate_starts(self):
        """ calculate the start point of the image """
        r = self.db.get(self.index)['resolution']
        if r['width'] <= self.paint.width \
            and r['height'] <= self.paint.height:
            self.prop = 1.0
        elif self.paint.width - r['width'] < self.paint.height - r['height']:
            self.prop = self.paint.width / float(r['width'])
        else:
            self.prop = self.paint.height / float(r['height'])
        self.x_start=self.paint.width/2.0 - \
                self.paint.norm_image_size[0] / 2.0
        self.y_start=self.paint.height/2.0 - \
                        self.paint.norm_image_size[1] / 2.0

    def show_faces(self):
        """ show the faces from the database """
        self.calculate_starts()
        with self.paint.canvas:
            for k,faces in self.db.get(self.index)['face_methods'].iteritems():
                for f in faces:
                    print 'face: ' + str(f)
                    Color( random.random(), random.random(), 
                            random.random(), 0.5)
                    e = Ellipse(
                            pos =(  self.x_start + int(f['x']*self.prop) - 
                                    int(f['width'] * self.prop / 2.0),
                                    self.height - self.y_start - 
                                    int(f['y']*self.prop) - 
                                    int(f['height'] * self.prop/2.0)), 
                            size =( int(f['width'] * self.prop),
                                    int(f['height'] * self.prop)))
                    print 'ellipse: ' + str(e.pos)
                    self.faces.append(e)

def fade(time, parent, wdgt, rate = .01, limit = 0):
    a = wdgt.color[3]
    if a > limit:
        a -= rate
        wdgt.color = (1, 1, 1, a)
    if a <= limit:
        parent.paint.remove_widget(wdgt);
        a = 1.0
        return False

class ControllerApp(App):
    def build(self):
        return Controller(info='Hello world')

if __name__ in ('__android__', '__main__'):
    ControllerApp().run()
