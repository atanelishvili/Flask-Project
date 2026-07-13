from flask import jsonify, request, session
from . import api_bp
from models import db, Property, Favorite

@api_bp.route('/properties', methods=['GET'])
def get_properties():
    city = request.args.get('city')
    query = Property.query.filter_by(is_active=True)
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    
    output = []
    for p in query.all():
        output.append({
            "id": p.id, "type": p.type, "deal_type": p.deal_type,
            "price": p.price, "city": p.city, "lat": p.lat, "lon": p.lon
        })
    return jsonify(output)

@api_bp.route('/properties/<int:id>', methods=['GET'])
def get_property_detail(id):
    p = Property.query.get_or_404(id)
    return jsonify({
        "id": p.id, "type": p.type, "deal_type": p.deal_type, "price": p.price,
        "area_sqm": p.area_sqm, "rooms": p.rooms, "city": p.city, "address": p.address,
        "description": p.description, "views": p.views, "lat": p.lat, "lon": p.lon
    })

@api_bp.route('/properties', methods=['POST'])
def create_property_api():
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    
    user_id = session.get('user_id', 1) 
    p = Property(user_id=user_id, type=data['type'], deal_type=data['deal_type'],
                 price=data['price'], area_sqm=data['area_sqm'], rooms=data['rooms'],
                 city=data['city'], address=data['address'])
    db.session.add(p)
    db.session.commit()
    return jsonify({"message": "Listing created successfully", "id": p.id}), 21