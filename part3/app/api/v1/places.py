# part3/app/api/v1/places.py

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade
from app.api.v1.reviews  import review_model

facade = HBnBFacade()
api    = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title':       fields.String(required=True),
    'description': fields.String(),
    'price':       fields.Float(required=True),
    'latitude':    fields.Float(required=True),
    'longitude':   fields.Float(required=True),
    'amenities':   fields.List(fields.String)
})

@api.route('/')
class PlaceList(Resource):
    @jwt_required()
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(403, 'Authentication required')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create place (authenticated users)"""
        current = get_jwt_identity()
        data = api.payload.copy()
        data['owner'] = current['id']
        new = facade.create_place(data)
        return {
            'id': new.id, 'title': new.title, 'description': new.description,
            'price': new.price, 'latitude': new.latitude, 'longitude': new.longitude
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """List all places (public)"""
        return [{
            'id':    p.id, 'title': p.title, 'price': p.price
        } for p in facade.get_all_places()], 200

@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place (public)"""
        p = facade.get_place(place_id)
        if not p:
            return {'error': 'Place not found'}, 404
        return {
            'id':          p.id, 'title': p.title, 'description': p.description,
            'price':       p.price, 'latitude': p.latitude, 'longitude': p.longitude
        }, 200

    @jwt_required()
    @api.expect(place_model, validate=False)
    @api.response(200, 'Place updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        """Update place (owner or admin)"""
        current = get_jwt_identity()
        p = facade.get_place(place_id)
        if not p:
            return {'error': 'Place not found'}, 404
        if p.owner != current['id'] and not current.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        updated = facade.update_place(place_id, api.payload)
        if not updated:
            return {'error': 'Invalid input data'}, 400
        return {'message': 'Place updated successfully'}, 200

    @jwt_required()
    @api.response(200, 'Place deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    def delete(self, place_id):
        """Delete place (owner or admin)"""
        current = get_jwt_identity()
        p = facade.get_place(place_id)
        if not p:
            return {'error': 'Place not found'}, 404
        if p.owner != current['id'] and not current.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        facade.delete_place(place_id)
        return {'message': 'Place deleted successfully'}, 200
