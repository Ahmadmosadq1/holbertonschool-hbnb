# part3/app/api/v1/reviews.py

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

facade = HBnBFacade()
api    = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text':     fields.String(required=True, description='Text of the review'),
    'rating':   fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id':  fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place'),
})

@api.route('/')
class ReviewList(Resource):
    @jwt_required()
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    def post(self):
        """Create a new review (authenticated users only)"""
        current_user = get_jwt_identity()
        data = api.payload.copy()

        place = facade.get_place(data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404

        # Prevent reviewing own place
        if place.owner == current_user['id']:
            return {'error': 'You cannot review your own place.'}, 400

        # Prevent duplicate review
        if any(r.user_id == current_user['id']
               for r in facade.get_reviews_by_place(data['place_id'])):
            return {'error': 'You have already reviewed this place.'}, 400

        data['user_id'] = current_user['id']

        try:
            r = facade.create_review(data)
            return {
                'id':       r.id,
                'text':     r.text,
                'rating':   r.rating,
                'user_id':  r.user_id,
                'place_id': r.place_id
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        return [{
            'id':     r.id,
            'text':   r.text,
            'rating': r.rating,
            'user_id': r.user_id,
            'place_id': r.place_id
        } for r in reviews], 200

@api.route('/<string:review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Retrieve review details by ID"""
        r = facade.get_review(review_id)
        if not r:
            return {'error': 'Review not found'}, 404
        return {
            'id':       r.id,
            'text':     r.text,
            'rating':   r.rating,
            'user_id':  r.user_id,
            'place_id': r.place_id
        }, 200

    @jwt_required()
    @api.expect(review_model, validate=True)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """Update a review (author only)"""
        r = facade.get_review(review_id)
        if not r:
            return {'error': 'Review not found'}, 404

        current_user = get_jwt_identity()
        if r.user_id != current_user['id']:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.update_review(review_id, api.payload)
            return {'message': 'Review updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @jwt_required()
    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review (author only)"""
        r = facade.get_review(review_id)
        if not r:
            return {'error': 'Review not found'}, 404

        current_user = get_jwt_identity()
        if r.user_id != current_user['id']:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200

@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """List all reviews for a given place (public)"""
        if not facade.get_place(place_id):
            return {'error': 'Place not found'}, 404
        reviews = facade.get_reviews_by_place(place_id)
        return [{
            'id':     r.id,
            'text':   r.text,
            'rating': r.rating,
            'user_id': r.user_id
        } for r in reviews], 200
