#!/usr/bin/python3
"""This module defines a class to manage file storage for hbnb clone"""
import json

from models.base_model import BaseModel
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review
from typing import Dict

classes = {
    'BaseModel': BaseModel, 'User': User, 'Place': Place,
    'State': State, 'City': City, 'Amenity': Amenity,
    'Review': Review
}


class FileStorage:
    """This class manages storage of hbnb models in JSON format"""
    __file_path: str = 'file.json'
    __objects: Dict[str, BaseModel] = {}

    def all(self, cls=None):
        """Returns a dictionary of models currently in storage"""
        if cls and cls in classes:
            return {k: v for k, v in FileStorage.__objects
                    if v.__class__.__name__ == cls}
        return FileStorage.__objects

    def new(self, obj):
        """Adds new object to storage dictionary"""
        self.all().update({obj.to_dict()['__class__'] + '.' + obj.id: obj})

    def save(self):
        """Saves storage dictionary to file"""
        with open(FileStorage.__file_path, 'w') as f:
            temp = {}
            temp.update(FileStorage.__objects)
            for key, val in temp.items():
                temp[key] = val.to_dict()
            json.dump(temp, f)

    def reload(self):
        """Loads storage dictionary from file"""
        try:
            with open(FileStorage.__file_path, 'r') as f:
                temp = json.load(f)
                for key, val in temp.items():
                    self.all()[key] = classes[val['__class__']](**val)
        except FileNotFoundError:
            pass

    def delete(self, obj: BaseModel = None) -> None:
        """Deletes obj from Basemodel if it exists"""
        if not obj:
            return
        del self.all()[obj.id]
