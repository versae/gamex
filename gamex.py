import json
import random
import kivy
kivy.require('1.1.1')

from kivy.app import App
from kivy.config import Config
from kivy.graphics import Color, Ellipse, Line, Rectangle, InstructionGroup
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout


Builder.load_file('gamex.kv')
Config.set('graphics', 'fullscreen', "auto")


class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.
    Add an action to be called from the kv lang file.
    '''

    db = json.load(open('barroco_faces.json'))
    index =  0
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


    def show_faces(self):
        with self.paint.canvas:
            r = self.db[self.index]['resolution']

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
            for k,faces in self.db[self.index]['face_methods'].iteritems():
                for f in faces:
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
                    self.ellipses.append(e)


    def clean_rects(self):
        with self.paint.canvas:
            for e in self.ellipses:
                self.paint.canvas.remove(e)


    def touch_down(self, paint, touch, *args):
        print str(touch.x) + ',' + str(touch.y)
        with paint.canvas:
            Color(random.random(), 1, 1, 0.5, mode='hsv')
            w=20
            h=20
            Ellipse(pos=(touch.x-int(w/2.0),touch.y-int(h/2.0)), size=(w,h))


    def start(self):
        self.remove_widget(self.menu)
        self.paint.source = './barroco/' + str(self.db[self.index]['id'])+'.jpg'
        self.show_faces()

    def previous(self):
        """ shows the previous image and update the index """
        self.clean_rects()
        if self.index > 0: self.index -= 1
        else: self.index == len(self.db) - 1
        self.paint.source = './barroco/' + str(self.db[self.index]['id'])+'.jpg'
        self.show_faces()

    def faces(self):
        pass

    def eyes(self):
        pass

    def next(self):
        """ shows the next image and update the index """
        self.clean_rects()
        if self.index < len(self.db) - 1: self.index += 1
        else: self.index = 0
        self.paint.source = './barroco/' + str(self.db[self.index]['id'])+'.jpg'
        self.show_faces()




class ControllerApp(App):
    def build(self):
        return Controller(info='Hello world')

if __name__ in ('__android__', '__main__'):
    ControllerApp().run()
