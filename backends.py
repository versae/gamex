# -*- coding: utf-8 -*-
import json
from os import path

from kivy.logger import Logger
from pymongo import Connection

import settings


__all__ = ["Backend", "Types"]


# Type of actions
class Types(object):
    FACE = 'face'
    EYES = 'eyes'
    EARS = 'ears'
    NOSE = 'nose'
    THROAT = 'throat'
    MOUTH = 'mouth'


class BackendInstance(object):

    def __call__(self, using="default"):
        database = settings.DATABASES[using]
        if database["ENGINE"] == "mongodb":
            db = MongoBackend(database)
        else:
            raise NotImplementedError("Not supported engine.")
        return db

Backend = BackendInstance()


class BaseBackend(object):
    pass


class MongoBackend(BaseBackend):

    def __init__(self, database):
        self.connection = Connection(database["HOST"], database["PORT"])
        self.db = self.connection[database["NAME"]]
        self.load_metadata()

    def _get_mean(self, methods, default=50):
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

    def load_metadata(self):
        metadata_file = open(settings.METADATA_PATH)
        metadata = json.load(metadata_file)
        metadata_file.close()
        if settings.DEBUG:
            Logger.info("Backend: Removing the key-value store for metadata")
            for c in self.db.collection_names():
                if c.startswith(u"metadata"):
                    self.db[c].drop()
                    self.db[c].drop_indexes()
        Logger.info("Backend: Filling the key-value store for metadata")
        self.db["metadata"].drop()
        for i, data in enumerate(metadata):
            image_path = path.join(settings.IMAGES_PATH,
                                   u"%s.jpg" % data["id"])
            data.update({
                "index": i,
                "image": image_path,
                "mean": self._get_mean(data["face_methods"])
            })
            self.db["metadata"].insert(data)

    def get(self, name):
        if name == "metadata":
            return Collection(self.db[name], "index")
        if name == Types.FACE:
            return Collection(self.db[name], "index")
        if name == Types.EARS:
            return Collection(self.db[name], "index")
        if name == Types.EYES:
            return Collection(self.db[name], "index")
        if name == Types.NOSE:
            return Collection(self.db[name], "index")
        if name == Types.THROAT:
            return Collection(self.db[name], "index")
        if name == Types.MOUTH:
            return Collection(self.db[name], "index")



class Collection(object):

    def __init__(self, collection, index):
        self.collection = collection
        self.index = index

    def add(self, key, value):
        key = unicode(key)
        self.collection.insert({key: value, self.index: key})

    def get(self, index, index_key=""):
        return self.collection.find_one({index_key or self.index: index})

    def first(self, *args, **kwards):
        return self.collection.find_one(*args, **kwards)

    def find(self, *args, **kwards):
        return self.collection.find(*args, **kwards)

    def count(self, *args, **kwards):
        return self.collection.count(*args, **kwards)

    def insert(self, *args, **kwards):
        return self.collection.insert(*args, **kwards)

    def insert(self, *args, **kwards):
        return self.collection.insert(*args, **kwards)

    def group(self, *args, **kwards):
        return self.collection.group(*args, **kwards)

    def remove(self, *args, **kwards):
        return self.collection.remove(*args, **kwards)

    def update(self, *args, **kwards):
        return self.collection.update(*args, **kwards)
