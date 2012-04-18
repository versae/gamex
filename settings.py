# -*- coding: utf-8 -*-
from os import path


DEBUG = True
IMAGES_PER_GAME = 5
SECONDS_PER_IMAGE = 5

PROJECT_NAME = "Gamex"
PROJECT_ROOT = path.dirname(path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'mongodb',
        'NAME': 'gamex',
        'USER': '',
        'PASSWORD': '',
        'SCHEMA': 'http',
        'HOST': 'localhost',
        'PORT': 27017,
    },  # ./bin/mongod --dbpath db
}

METADATA_PATH = path.join(PROJECT_ROOT, "barroco_faces.json")
IMAGES_PATH = path.join(PROJECT_ROOT, "barroco")
