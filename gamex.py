import json
import random
import kivy
kivy.require('1.1.1')

from kivy.clock import Clock
from kivy.app import App
from kivy.config import Config
from kivy.graphics import Color, Ellipse, Line, Rectangle, InstructionGroup
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

from functools import partial
import settings
from backends import Backend

Builder.load_file('gamex.kv')
if not settings.DEBUG:
    Config.set('graphics', 'fullscreen', "auto")
backend = Backend()


class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.
    Add an action to be called from the kv lang file.
    '''

    db = backend.get("metadata")
    index =  0
    count = db.count() - 1
    paint = ObjectProperty(None)
    menu = ObjectProperty(None)
    colors = {'tree':[1,0,0,0.4],
                'alt':[0,1,0,0.2],
                'alt2':[0,0,1,0.4],
                'profile':[0.8,0.8,0,0.4],
                'user': [0,0.8,0.8, 0.4]}
    x_start = 0
    y_start = 0
    prop = 1.0
    ellipses = []
    score = 0
    high_score = 0
    icon = None

    def show_faces(self):
        with self.paint.canvas:
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

            self.ellipses = []
            for k,faces in self.db.get(self.index)['face_methods'].iteritems():
                for f in faces:
                    print 'face: ' + str(f)
                    Color(  self.colors[k][0],self.colors[k][1],
                            self.colors[k][2],self.colors[k][3] )
                    e = Ellipse(
                            pos =(  self.x_start + int(f['x']*self.prop) - 
                                    int(f['width'] * self.prop / 2.0),
                                    self.height - self.y_start - 
                                    int(f['y']*self.prop) - 
                                    int(f['height'] * self.prop/2.0)), 
                            size =( int(f['width'] * self.prop),
                                    int(f['height'] * self.prop)))
                    print 'ellipse: ' + str(e.pos)
                    self.ellipses.append(e)

    def to_image_coord(self, touch):
        touch.x = int((touch.x - self.x_start) / float(self.prop))
        touch.y = ((self.height - touch.y - self.y_start) / float(self.prop))
        print "to_image: " + str(touch.x) + ',' + str(touch.y)
        return touch

    def to_screen_coord(self, touch):
        touch.x = self.x_start + int(touch.x*self.prop)
        touch.y =  self.height - self.y_start - int(touch.y*self.prop)
        print "to_screen: "+ str(touch.x) + ',' + str(touch.y)
        return touch

    def remove_ellipses(self):
        with self.paint.canvas:
            for e in self.ellipses:
                self.paint.canvas.remove(e)

    def touch_down(self, paint, touch, *args):
        print "original: "+ str(touch.x) + ',' + str(touch.y)
        touch = self.to_image_coord(touch)
        touch = self.to_screen_coord(touch)
        w=h=48
        icon = Image(source='img/punch.png', 
                        pos=(touch.x-int(w/2.0),touch.y-int(h/2.0)), 
                        size=(w,h))
        self.paint.add_widget(icon);
        Clock.schedule_interval(partial(fade, parent = self, image = icon), .01)


    def start(self):
        self.remove_widget(self.menu)
        self.paint.source = self.db.get(self.index)["image"]
        self.show_faces()

    def previous(self):
        """ shows the previous image and update the index """
        self.remove_ellipses()
        if self.index > 0:
            self.index -= 1
        else:
            self.index == self.count
        self.paint.source = self.db.get(self.index)["image"]
        self.show_faces()

    def face(self):
        pass

    def eyes(self):
        pass

    def next(self):
        """ shows the next image and update the index """
        self.remove_ellipses()
        if self.index < self.count:
            self.index += 1
        else:
            self.index = 0
        self.paint.source = self.db.get(self.index)["image"]
        self.show_faces()


def fade(time, parent, image, rate = .01, limit = 0):
    a = image.color[3]

    if a > limit:
        a -= rate
        image.color = (1, 1, 1, a)
    if a <= limit:
        parent.paint.remove_widget(image);
        a = 1.0
        return False


class ControllerApp(App):

    def build(self):
        return Controller(info='Hello world')


if __name__ in ('__android__', '__main__'):
    ControllerApp().run()
