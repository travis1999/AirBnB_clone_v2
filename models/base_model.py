#!/usr/bin/python3
"""This module defines a base class for all models in our hbnb clone"""
import uuid
from datetime import datetime
from inspect import Signature, Parameter


class BaseModel:
    """A base class for all hbnb models"""

    def __init__(self, *args, **kwargs):
        """Instatntiates a new model"""
        base_signature = Signature(
            [Parameter('id', Parameter.POSITIONAL_OR_KEYWORD,
                       default=str(uuid.uuid4())),
             Parameter('created_at', Parameter.POSITIONAL_OR_KEYWORD,
                       default=datetime.now()),
             Parameter('updated_at', Parameter.POSITIONAL_OR_KEYWORD,
                       default=datetime.now())])

        filter_dict = \
            {param.name for param in base_signature.parameters.values()}
        new_kwargs = {k: v for k, v in kwargs.items() if k in filter_dict}
        params = base_signature.bind(*args, **new_kwargs)
        params.apply_defaults()

        self.__dict__.update(params.arguments)
        self.to_datetime("created_at")
        self.to_datetime("updated_at")

    def to_datetime(self, attr):
        """To datetime if attr is isostring"""
        if isinstance(self.__dict__[attr], str):
            self.__setattr__(attr,
                             datetime.fromisoformat(self.__dict__[attr]))

    def __str__(self):
        """Returns a string representation of the instance"""
        cls = self.__class__.__name__
        return '[{}] ({}) {}'.format(cls, self.id, self.__dict__)

    def save(self):
        """Updates updated_at with current time when instance is changed"""
        from models import storage
        self.updated_at = datetime.now()
        storage.save()

    def to_dict(self):
        """Convert instance into dict format"""
        dictionary = {}
        dictionary.update(self.__dict__)
        dictionary.update({'__class__':
                          (str(type(self)).split('.')[-1]).split('\'')[0]})
        dictionary['created_at'] = self.created_at.isoformat()
        dictionary['updated_at'] = self.updated_at.isoformat()
        return dictionary
