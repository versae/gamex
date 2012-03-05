import pygame, random, json, math

from functools import partial
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.opengl import glLineWidth

db = json.load(open('barroco_faces_user.json')) 
rects = []
index = 0

class Painting(Image):
    colors = {'tree':[1,0,0,0.4],
            'alt':[0,1,0,0.4],
            'alt2':[0,0,1,0.4],
            'profile':[1,1,0,0.6],
            'user': [0,1,1, 0.6]}
    x_start = 0
    y_start = 0
    prop = 1.0
    ellipses = []
    coords = []

    def show_faces(self):
        with self.canvas:
            r = db[index]['resolution']
            if r['width'] <= 800 and r['height'] <= 600:
                self.x_start = (800 - r['width']) / 2
                self.prop = 1.0
                self.y_start = (600 - r['height']) / 2
            elif 800 - r['width'] < 600 - r['height']:
                self.x_start = 0
                self.prop = self.width / float(r['width'])
                self.y_start= int((self.height - self.norm_image_size[1]) / 2)
            else:
                self.y_start = 0
                self.prop = self.height / float(r['height'])
                self.x_start = int((self.width - self.norm_image_size[0]) / 2)

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
                    Color(  self.colors[k][0],self.colors[k][1],
                            self.colors[k][2],self.colors[k][3])
                    Rectangle(
                        pos =(  self.x_start + int(f['x']*self.prop) - 
                                int(f['width'] * self.prop / 2),
                                600 - self.y_start - int(f['height'] * self.prop) - 
                                int(f['y']*self.prop) + 
                                int(f['height'] * self.prop / 2)), 
                        size =( int(f['width'] * self.prop),
                                int(f['height'] * self.prop)))



    def on_touch_down(self, touch):
        userdata = touch.ud
        userdata['color'] = c = (random.random(), 1, 1, 1)
        userdata['x'] = touch.x
        userdata['y'] = touch.y

        userdata['coord'] = {'min_x': touch.x, 'min_y': touch.y,
                             'max_x': touch.x, 'max_y': touch.y}

        with self.canvas:
            Color(*c, mode='hsv')
            #userdata['rectangle'] = Rectangle(  pos=(touch.x, touch.y),size=(1, 1))
            glLineWidth(5.0) 
            userdata['line'] = Line(points=(touch.x, touch.y))


    def on_touch_move(self, touch):
        userdata = touch.ud
        #touch.ud['rectangle'].size=(touch.x-touch.ud['x'], touch.y-touch.ud['y'])
        userdata['line'].points += [touch.x, touch.y]
        userdata['coord']['min_x'] = max(self.x_start,
                                        min(touch.x,userdata['coord']['min_x']))
        userdata['coord']['min_y'] = max(self.y_start,
                                        min(touch.y,userdata['coord']['min_y']))
        userdata['coord']['max_x'] = min(800-self.x_start,
                                        max(touch.x,userdata['coord']['max_x']))
        userdata['coord']['max_y'] = min(600-self.y_start,
                                        max(touch.y,userdata['coord']['max_y']))

    def on_touch_up(self, touch):
        userdata = touch.ud
        c = (random.random(), 1, 1, 0.5)

        if 'coord' in touch.ud:
            if userdata['coord']['min_x'] == userdata['coord']['max_x'] and \
                userdata['coord']['min_y'] == userdata['coord']['max_y']:
                for r in range(0,len(self.coords)):
                    if  touch.x > self.coords[r]['min_x'] and \
                        touch.x < self.coords[r]['max_x'] and \
                        touch.y > self.coords[r]['min_y'] and \
                        touch.y < self.coords[r]['max_y']:
                        self.canvas.remove(self.ellipses[r])
                        self.ellipses.pop(r)
                        self.coords.pop(r)
                        rects.pop(r)
            else:
                x = userdata['coord']['min_x']
                y = userdata['coord']['min_y']
                width = math.fabs(userdata['coord']['max_x'] - \
                        userdata['coord']['min_x'])
                height = math.fabs(userdata['coord']['max_y'] - \
                         userdata['coord']['min_y'])
                rect = {}
                rect['width'] = int(round(width/self.prop))
                rect['height'] = int(round(height/self.prop))
                rect['x'] = int(round((x + width/2.0 - \
                            self.x_start)/self.prop))
                rect['y'] = int(round((600 - (y + height/2.0) - \
                            self.y_start)/self.prop))
                rects.append(rect)
                with self.canvas:
                    Color(*c, mode='hsv')
                    self.ellipses.append(Ellipse(pos=(x,y),size=(width ,height)))
                    self.coords.append(userdata['coord'])
                    self.canvas.remove(touch.ud['line'])





class Main_menu(Widget):
    layout = BoxLayout(orientation='vertical', spacing = 20, size = (200, 250), 
        pos = (300, 10))
    btn1 = Button(text='Play Game')
    btn3 = Button(text='Quit')
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
        global rects
        if not 'user'  in db[index-1]['face_methods']:
            db[index-1]['face_methods']['user'] = []
        db[index-1]['face_methods']['user'].extend(rects)
        rects=[]
        out = open('barroco_faces_user.json', 'w')
        out.write(json.dumps(db, sort_keys=True, indent=4))
        out.close()
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
