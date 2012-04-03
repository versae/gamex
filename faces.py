import pygame, random, json

from functools import partial
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Color, Ellipse, Line, Rectangle

from kivy.lang import Builder

Builder.load_file('faces.kv')

Config.set('graphics', 'fullscreen', "auto")
db = json.load(open('barroco_faces.json'))
index = 0

class Painting(Image):
    cols = {'tree':[0.5,0.5,0.5,0.5],
            'alt':[1,0,0,0.35],
            'alt2':[0,1,0,0.35],
            'profile':[0,0,1,0.35]}


    def show_faces(self):
        with self.canvas:
            r = db[index]['resolution']
            if r['width'] <= 800 and r['height'] <= 600:
                x_start = (800 - r['width']) / 2
                prop = 1.0
                y_start = (600 - r['height']) / 2
            elif 800 - r['width'] < 600 - r['height']:
                x_start = 0
                prop = self.width / float(r['width'])
                y_start= int((self.height - self.norm_image_size[1]) / 2)
            else:
                y_start = 0
                prop = self.height / float(r['height'])
                x_start = int((self.width - self.norm_image_size[0]) / 2)

#            display the generic view
#            for f in db[index]['faces']:
#                Rectangle(
#                    pos =(  x_start + int(f['x']*prop) - 
#                            int(f['width'] * prop / 2),
#                            600 - y_start - int(f['height'] * prop) - 
#                            int(f['y']*prop) + 
#                            int(f['height'] * prop / 2)), 
#                    size =( int(f['width'] * prop),
#                            int(f['height'] * prop)))



            for k,faces in db[index]['face_methods'].iteritems():
                for f in faces:
                    Color(  self.cols[k][0],self.cols[k][1],
                            self.cols[k][2],self.cols[k][3])
#                    Rectangle(
#                        pos =(  x_start + int(f['x']*prop) - 
#                                int(f['width'] * prop / 2),
#                                600 - y_start - int(f['height'] * prop) - 
#                                int(f['y']*prop) + 
#                                int(f['height'] * prop / 2)), 
#                        size =( int(f['width'] * prop),
#                                int(f['height'] * prop)))



    def on_touch_down(self, touch):
        userdata = touch.ud
        userdata['color'] = c = (random.random(), 1, 1, 0.5)
        userdata['x'] = touch.x
        userdata['y'] = touch.y
        with self.canvas:
            Color(*c, mode='hsv')
            current = db[index]
            d = self.get_mean(current)
            userdata['ellipse'] = Ellipse(pos=(touch.x - d/2, touch.y - d/2),
                                            size=(d, d))
            userdata['rectangle'] = Rectangle(  pos=(touch.x, touch.y),
                                                size=(1, 1))

    def get_mean(self, image, default=50):
        methods = image["face_methods"]
        width_count = 0
        height_count = 0
        height = 0
        width = 0
        for method, values in methods.items():
            if values:
                for value in values:
                    height += value["height"]
                    width += value["width"]
                    width_count += 1
                    height_count += 1
        if height_count and width_count:
            return (height / height_count + width / width_count) / 2
        else:
            return default

    def on_touch_move(self, touch):
        touch.ud['rectangle'].size=(touch.x-touch.ud['x'], touch.y-touch.ud['y'])

    def on_touch_up(self, touch):
        userdata = touch.ud
        if "rectangle" in userdata:
            current = db[index]
            rec = userdata["rectangle"]
            out = {
                "id": current["id"],
                "pos": rec.pos,
                "size": rec.size,
            }
            user_faces = open("userfaces.json", "a")
            user_faces.write(json.dumps(out) +"\n")
            print out
        if "ellipse" in userdata:
            current = db[index]
            eli = userdata["ellipse"]
            out = {
                "id": current["id"],
                "pos": eli.pos,
                "size": eli.size,
            }
            user_faces = open("userfaces.json", "a")
            user_faces.write(json.dumps(out) +"\n")
            print out

#        with self.canvas:
#            Rectangle(  pos=(userdata['x'], userdata['y']), 
#                        size=(touch.x-userdata['x'], touch.y-userdata['y']))


class Main_menu(Widget):
#    layout = BoxLayout(orientation='vertical', spacing = 20, size = (200, 250), pos = (300, 10))
    layout = FloatLayout(size=(300, 300))
    btn1 = Button(text='Play Game', size_hint=(None, .25), width=250, pos=(20, 20))
    btn3 = Button(text='Quit', size_hint=(.6, .6),
                pos=(250, 20))
    layout.add_widget(btn1)
    layout.add_widget(btn3)
    logo = Image(source='logo.png', size = (500, 150), pos = (150, 450))


class Exhibition(App):
    ma_men = None
    painting = None
    next_btn = Button(text='Next')

    def start_exhibition(self,instance):
        global base_running, a, ma_men, parent
        parent.remove_widget(ma_men.layout)
        parent.remove_widget(ma_men.logo)
        self.next_btn.bind(on_release=self.next)
        self.load()

    def next(self, instance):
        parent.remove_widget(self.painting)
        parent.remove_widget(self.next_btn)
        self.load()

    def load(self):
        global index
        self.painting = Painting(source = './barroco/' + str(db[index]['id'])+'.jpg', size = (800, 600), pos = (0, 0))
        parent.add_widget(self.painting)
        parent.add_widget(self.next_btn)
        self.painting.show_faces()
        index += 1

    def build(self):
        global base_running, a, parent, ma_men
        ma_men = Main_menu()
        parent = Widget()
        parent.add_widget(ma_men.layout)
        parent.add_widget(ma_men.logo)
        ma_men.btn1.bind(on_release = self.start_exhibition)
        ma_men.btn3.bind(on_release = exit)
        return parent


if __name__ == '__main__':
    exhibition = Exhibition()
    exhibition.run()	
