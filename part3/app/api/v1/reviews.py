# part3/app/api/v1/reviews.py

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

facade = HBnBFacade()
api    = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text':     fields.String(required=True),
    'rating':   fields.Integer(required=True),
    'place_id': fields.String(required=True)
})

@api.route('/')
class ReviewList(Resource):
    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """List all reviews (public)"""
        return [{
            'id': r.id, 'text': r.text, 'rating': r.rating,
            'user_id': r.user_id, 'place_id': r.place_id
        } for r in facade.get_all_reviews()], 200

    @jwt_required()
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    def post(self):
        """Create review (authenticated users)"""
        current = get_jwt_identity()
        data = api.payload.copy()
        place = facade.get_place(data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner == current['id'] and not current.get('is_admin'):
            return {'error': 'You cannot review your own place.'}, 403
        if any(r.user_id == current['id'] for r in facade.get_reviews_by_place(data['place_id'])) and not current.get('is_admin'):
            return {'error': 'You have already reviewed this place.'}, 403

        data['user_id'] = current['id']
        new = facade.create_review(data)
        return {
            'id': new.id, 'text': new.text, 'rating': new.rating,
            'user_id': new.user_id, 'place_id': new.place_id
        }, 201

@api.route('/<string:review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review (public)"""
        r = facade.get_review(review_id)
        if not r:
            return {'error': 'Review not found'}, 404
        return {
            'id': r.id, 'text': r.text, 'rating': r.rating,
            'user_id': r.user_id, 'place_id': r.place_id
        }, 200

    @jwt_required()
    @api.expect(review_model, validate=False)
    @api.response(200, 'Review updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """Update review (author or admin)"""
        current = get_jwt_identity()
        r = facade.get_review(review_id)
        if not r:
            return {'error': 'Review not found'}, 404
        if r.user_id != current['id'] and not current.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        updated = facade.update_review(review_id, api.payload)
        if not updated:
            return {'error': 'Invalid input data'}, 400
        return {'message': 'Review updated successfully'}, 200

    @jwt_required()
    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete review (author or admin)"""
        current = get_jwt_identity()
        r = facade.get_review(review_id)
        if not r:
            return {'error': 'Review not found'}, 404
        if r.user_id != current['id'] and not current.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """List all reviews for a place (public)"""
        if not facade.get_place(place_id):
            return {'error': 'Place not found'}, 404
        return [{
            'id':     r.id, 'text': r.text, 'rating': r.rating,
            'user_id': r.user_id
        } for r in facade.get_reviews_by_place(place_id)], 200
