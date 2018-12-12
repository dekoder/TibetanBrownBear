"""API resources for interacting with Entities."""
from marshmallow import fields
from flask_classful import route
from flask import request
from webargs.flaskparser import parser

from yeti.core.entities.entity import Entity
from yeti.core.errors import YetiSTIXError
from .generic import GenericResource
from ..helpers import as_json, get_object_or_404, auth_required


class EntityResource(GenericResource):
    """Class describing resources to manipulate Entity objects."""

    route_base = '/entities/'
    resource_object = Entity

    searchargs = {
        'name': fields.Str(required=True),
        'type': fields.Str(),
        'page': fields.Int(),
        'page_size': fields.Int(),
    }

    neighbor_params = {
        'link_type': fields.Str(),
        'direction': fields.Str(),
        'include_original': fields.Boolean(),
        'hops': fields.Int(),
    }

    @as_json
    @route('/<id>/neighbors/', methods=['POST'])
    @auth_required
    def neighbors(self, id):  # pylint: disable=redefined-builtin
        """Fetch objects an object is related to.

        A (relationships_list, objects_list) tuple is built, the first list
        representing all the relationship data for a given object, the second
        list is all the objects referenced by those relationships.

        Args:
            id: The object's primary ID.

        Returns:
            A JSON representation of the object's relationships.
        """
        args = parser.parse(self.neighbor_params, request)
        obj = get_object_or_404(self.resource_object, id)
        return obj.neighbors(**args)

    @as_json
    @route('/<id>/addlink/', methods=['POST'])
    @auth_required
    def link(self, id):  # pylint: disable=redefined-builtin
        """Link an object to another object.

        Args:
            id: The source object's primary ID.

        Returns:
            A JSON representation of the object's relationships.
        """
        obj = get_object_or_404(self.resource_object, id)
        args = request.json
        links = []
        for link in args:
            target = self.resource_object.get(link['target']['id'])
            links.append(obj.link_to(target, link['link_type'], link['stix_rel']))
        return links

    @as_json
    @route('/<id>/', methods=['PUT'])
    @auth_required
    def put(self, id):  # pylint: disable=redefined-builtin
        """Updates a STIX SDO object.

        Args:
            id: The object's primary ID.

        Returns:
            A JSON representation of the requested object, or a 404 HTTP
            status code if the object cannot be found.
        """
        # Remove unupdatable fields (created, id, type) from the request JSON
        # Also remove the 'modified' field since we want STIX to change the
        # timestamp
        update_dict = request.get_json()
        update_dict.pop('created', None)
        update_dict.pop('id', None)
        update_dict.pop('type', None)
        update_dict.pop('modified', None)
        try:
            obj = get_object_or_404(self.resource_object, id)
            return obj.update(update_dict)
        except YetiSTIXError as err:
            return err, 400
