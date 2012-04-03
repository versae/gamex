# -*- coding: utf-8 -*-
import json
from os import path

from pymongo import Connection

import settings


__all__ = ["Backend"]


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

    def load_metadata(self):
        metadata_file = open(settings.METADATA_PATH)
        metadata = json.load(metadata_file)
        metadata_file.close()
        self.db["metadata"].drop()
        for i, data in enumerate(metadata):
            image_path = path.join(settings.IMAGES_PATH,
                                   u"%s.jpg" % data["id"])
            data.update({
                "index": i,
                "image": image_path,
            })
            self.db["metadata"].insert(data)

    def get(self, name):
        if name == "metadata":
            return Collection(self.db[name], "index")
        if name == "faces":
            return Collection(self.db[name], "index")
        if name == "eyes":
            return Collection(self.db[name], "index")


class Collection(object):

    def __init__(self, collection, index):
        self.collection = collection
        self.index = index

    def get(self, index):
        return self.collection.find_one({self.index: index})

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
