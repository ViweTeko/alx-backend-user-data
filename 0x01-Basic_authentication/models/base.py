#!/usr/bin/env python3
""" Base model"""
from datetime import datetime
from uuid import uuid4
import json
from os import path
fro typing import List, TypeVar, Iterable


DATA = {}
TIMESTAMP_FORMAT = "%Y-%m-%T%H:%M:%S"


class Base():
    """ Base class"""

    def __init__(self, *args: list, **kwargs: dict):
        """ Initializes Base instance"""
        s_class = str(self.__class__.__name__)
        if DATA.get(s_class) is None:
            DATA[s_class] = {}

        self.id = kwargs.get('id', (uuid4()))
        if kwargs.get('created_at') is not None:
            self.created_at = datetime.strptime(
                kwargs.get('created_at'), TIMESTAMP_FORMAT)
        else:
            self.created_at = datetime.utcnow()
        if kwargs.get('updated_at') is not None:
            self.updated_at = datetime.strptime(
                kwargs.get('updated_at'), TIMESTAMP_FORMAT)
        else:
            self.updated_at = datetime.utcnow()

    def __eq__(self, other: TypeVar('Base')) -> bool:
        """ Checks for equality"""
        if type(self) != type(other):
            return False
        if not isinstance(self, Base):
            return False
        return (self.id == other.id)

    def to_json(self, for_serialization: bool = False) -> dict:
        """ Converts object to JSON"""
        result = {}
        for key, val in self.__dict__.items():
            if not for_serialization and key[0] == '_':
                continue
            if type(val) is datetime:
                result[key] = val.strftime(TIMESTAMP_FORMAT)
            else:
                result[key] = val
        return result

    def save(self):
        """Saves current object"""
        s_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()
        DATA[s_class][self.id] = self
        self.__class__.save_to_file()

    def remove(self):
        """Removes current object"""
        s_class = self.__class__.__name__
        if DATA[s_class].get(self.id) is not None:
            del DATA[s_class][self.id]
            self.__class__.save_to_file()

    @classmethod
    def all(cls) -> Iterable[TypeVar('Base')]:
        """ Return all objects"""
        return cls.search()

    @classmethod
    def count(cls) -> int:
        """Counts all objects"""
        s_class = cls.__name__
        return len(DATA[s_class].keys())

    @classmethod
    def get(cls, id: str) -> TypeVar('Base'):
        """Returns one object by ID"""
        s_class = cls.__name__
        return DATA[s_class].get(id)

    @classmethod
    def load_from_file(cls):
        """Loads all objects from file"""
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        DATA[s_class] = {}
        if not path.exists(file_path):
            return
        with open(file_path, 'r') as f:
            objs_json = json.load(f)
            for o_id, o_json in objs_json.items():
                DATA[s_class][o_id] = cls(**o_json)

        @classmethod
        def save_to_file(cls):
            """ Saves all objects to file"""
            s_class = cls.__name__
            file_path = f".db_{s_class}.json"
            objs_json = {}
            for o_id, obj in DATA[s_class].items():
                objs_json[o_id] = obj.to_json(True)
            with open(file_path, 'w') as f:
                json.dump(objs_json, f)

            @classmethod
            def search(cls, attributes: dict = {}) -> List[TypeVar('Base')]:
                """Searches all objects with matching attributes"""
                s_class = cls.__name__
                
                def _search(obj):
                    if len(attributes) == 0:
                        return True
                    for key, val in attributes.items():
                        if (getattr(obj, key) != val):
                            return False
                    return True
                return list(filter(_search, DATA[s_class].values()))
