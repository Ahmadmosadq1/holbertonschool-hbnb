# part3/app/api/v1/places.py

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade
from app.api.v1.reviews  import review_model

facade = HBnBFacade()
api    = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id':   fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id':         fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name':  fields.String(description='Last name of the owner'),
    'email':      fields.String(description='Email of the owner')
})

place_model = api.model('Place', {
    'title':       fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price':       fields.Float(required=True, description='Price per night'),
    'latitude':    fields.Float(required=True, description='Latitude of the place'),
    'longitude':   fields.Float(required=True, description='Longitude of the place'),
    'owner_id':    fields.String(required=True, description='ID of the owner'),
    'amenities':   fields.List(fields.String, required=True, description="List of amenities ID's"),
    'reviews':     fields.List(fields.Nested(review_model), description='List of reviews')
})

@api.route('/')
class PlaceList(Resource):
    @jwt_required()
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new place (authenticated users only)"""
        current_user = get_jwt_identity()
        data = api.payload.copy()
        data['owner'] = current_user['id']
        data.pop('owner_id', None)

        try:
            new_place = facade.create_place(data)
            return {
                'id':          new_place.id,
                'title':       new_place.title,
                'description': new_place.description,
                'price':       new_place.price,
                'latitude':    new_place.latitude,
                'longitude':   new_place.longitude,
                'owner_id':    new_place.owner,
                'amenities':   new_place.amenities,
                'reviews': [{
                    'id':       r.id,
                    'text':     r.text,
                    'rating':   r.rating,
                    'user_id':  r.user_id,
                    'place_id': r.place_id
                } for r in facade.get_reviews_by_place(new_place.id)]
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places (public)"""
        places = facade.get_all_places()
        return [{
            'id':    p.id,
            'title': p.title,
            'price': p.price
        } for p in places], 200

@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID (public)"""
        p = facade.get_place(place_id)
        if not p:
            return {'error': 'Place not found'}, 404

        owner = facade.get_user(p.owner)
        amenities = [{
            'id':   a_id,
            'name': facade.get_amenity(a_id).name
        } for a_id in p.amenities]

        return {
            'id':          p.id,
            'title':       p.title,
            'description': p.description,
            'price':       p.price,
            'latitude':    p.latitude,
            'longitude':   p.longitude,
            'owner': {
                'id':         owner.id,
                'first_name': owner.first_name,
                'last_name':  owner.last_name,
                'email':      owner.email
            },
            'amenities': amenities,
            'reviews': [{
                'id':       r.id,
                'text':     r.text,
                'rating':   r.rating,
                'user_id':  r.user_id,
                'place_id': r.place_id
            } for r in facade.get_reviews_by_place(p.id)]
        }, 200

    @jwt_required()
    @api.expect(place_model, validate=False)  # Allow partial updates
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information (owner only)"""
        p = facade.get_place(place_id)
        if not p:
            return {'error': 'Place not found'}, 404

        current_user = get_jwt_identity()
        if p.owner != current_user['id']:
            return {'error': 'Unauthorized action'}, 403

        updated = facade.update_place(place_id, api.payload)
        if not updated:
            return {'error': 'Invalid input data'}, 400
        return {'message': 'Place updated successfully'}, 200

    @jwt_required()
    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    def delete(self, place_id):
        """Delete a place (owner only)"""
        p = facade.get_place(place_id)
        if not p:
            return {'error': 'Place not found'}, 404

        current_user = get_jwt_identity()
        if p.owner != current_user['id']:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_place(place_id)
        return {'message': 'Place deleted successfully'}, 200
