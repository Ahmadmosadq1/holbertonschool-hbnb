# part3/app/api/v1/amenities.py

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

facade = HBnBFacade()
api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve all amenities (public)"""
        amenities = facade.get_amenities()
        return [{'id': a.id, 'name': a.name} for a in amenities], 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(403, 'Admin privileges required')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new amenity (admin only)"""
        current = get_jwt_identity()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        data = api.payload
        try:
            amenity = facade.create_amenity(data)
            return {'id': amenity.id, 'name': amenity.name}, 201
        except Exception as e:
            return {'error': str(e)}, 400


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get an amenity by ID (public)"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {'id': amenity.id, 'name': amenity.name}, 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Admin privileges required')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """Update an amenity (admin only)"""
        current = get_jwt_identity()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        data = api.payload
        amenity = facade.update_amenity(amenity_id, data)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {'message': 'Amenity updated successfully'}, 200

    @jwt_required()
    @api.response(200, 'Amenity deleted successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Admin privileges required')
    def delete(self, amenity_id):
        """Delete an amenity (admin only)"""
        current = get_jwt_identity()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        success = facade.delete_amenity(amenity_id)
        if not success:
            return {'error': 'Amenity not found'}, 404
        return {'message': 'Amenity deleted successfully'}, 200
