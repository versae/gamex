import  json
from SimpleCV import Image as ImageCV


xmls=[{'file':'haarcascade_frontalface_alt_tree.xml', 'code':'tree'}, 
        {'file':'haarcascade_frontalface_alt.xml', 'code':'alt'}, 
        {'file':'haarcascade_frontalface_alt2.xml', 'code':'alt2'}, 
        {'file':'haarcascade_profileface.xml', 'code':'profile'}
        ]

src=open('barroco.json')
db = json.load(src) 


def fuzzy_add(new, faces, face_method):
    add_new = True

    for f in faces:
                    
        width = min(new['width'], f['width'], 
                    (new['x']+new['width']/2) - (f['x']-f['width']/2),
                    (f['x']+f['width']/2) - (new['x']-new['width']/2))
                    
        height = min(new['height'], f['height'], 
                    (new['y']+new['height']/2) - (f['y']-f['height']/2),
                    (f['y']+f['height']/2) - (new['y']-new['height']/2))

        if width < 0 or  height < 0:
            # disjoint rectangles
            pass
        elif width == new['width'] and height == new['height']:
            # the new rectangle is inside an old one
            add_new = False
            break
        elif width == f['width'] and height == f['height']:
            # the old rectangle is inside the new one
            add_new = False;
            f['x'] = new['x']
            f['y'] = new['y']
            f['width'] = new['width']
            f['height'] = new['height']
            break
        elif width*height/float(new['width']*new['height']) > 0.5 or \
                width*height/float(f['width']*f['height']) > 0.5:
            # there is an old one that has more thant 50% of the new one
            add_new = False;
            #merge
            f['x'] = int((f['x'] + new['x']) / 2.0)
            f['y'] = int((f['y'] + new['y']) / 2.0)
            f['width'] = max(f['width'], new['width'])
            f['height'] = max(f['height'], new['height'])
            break

    face_method.append(new)
    if add_new:
        faces.append(new)



ind = 0
for paint in db:
    print str(ind)
    i = ImageCV('./barroco/' + str(paint ['id']) + '.jpg')
    paint['resolution'] = {'width':i.size()[0], 'height':i.size()[1]}
    paint['faces'] = []
    paint['face_methods'] = {}

    for xml in xmls:
        faces = i.findHaarFeatures(
            '/usr/local/share/OpenCV/haarcascades/' + xml['file'])
        face_method = []
        paint['face_methods'][xml['code']]=face_method
        if faces:
            for f in faces:
                fuzzy_add({ 'x':f.coordinates()[0],
                            'y':f.coordinates()[1],
                            'width':f.width(),
                            'height':f.height() },
                            paint['faces'],
                            face_method)
    ind+=1
    if ind >= 100:
        break;





out = open('barroco_faces.json', 'w')
out.write(json.dumps(db, sort_keys=True, indent=4))

src.close()
out.close()

