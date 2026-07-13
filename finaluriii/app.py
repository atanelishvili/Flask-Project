from flask import Flask
from models import db, Property, PropertyImage, User
from auth.routes import auth_bp
from properties.routes import properties_bp
from api.routes import api_bp
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import requests
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-for-real-estate-app'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///realestate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


app.register_blueprint(auth_bp)
app.register_blueprint(properties_bp)
app.register_blueprint(api_bp)


def fetch_from_open_api(user_id):
    if Property.query.count() > 0:
        return

    print("🌐 ვუკავშირდები ღვია საჯარო რეალური ქონებების API-ს...")
    
    
    url = "https://raw.githubusercontent.com/BrianQMclaren/real-estate/master/data.json"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data_json = response.json()
            properties_list = data_json.get("property", [])
            
            fallback_photos = [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600",
                "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600",
                "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=600"
            ]

            for idx, item in enumerate(properties_list[:12]):
                api_type = str(item.get("type", "apartment")).lower()
                p_type = "house" if "house" in api_type or "family" in api_type else "apartment"
                deal_type = "rent" if idx % 3 == 0 else "sell"
                
                raw_price = float(item.get("price", 150000))
                price = random.randint(600, 2500) if deal_type == "rent" else raw_price

                prop = Property(
                    user_id=user_id,
                    type=p_type,
                    deal_type=deal_type,
                    price=price,
                    area_sqm=float(item.get("floorspace", 85)),
                    rooms=int(item.get("beds", 2)),
                    city=item.get("city", "Scarsdale"),
                    address=item.get("address", "Garth Rd"),
                    description=f"Wonderful real estate property listed via public data API. Features {item.get('beds')} bedrooms.",
                    lat=41.7151 + (idx * 0.003),
                    lon=44.8271 + (idx * 0.003),
                    is_active=True,
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                db.session.add(prop)
                db.session.flush()

                img1_url = fallback_photos[idx % len(fallback_photos)]
                img2_url = fallback_photos[(idx + 1) % len(fallback_photos)]

                img1 = PropertyImage(property_id=prop.id, image_url=img1_url, order=1)
                img2 = PropertyImage(property_id=prop.id, image_url=img2_url, order=2)
                db.session.add(img1)
                db.session.add(img2)

            db.session.commit()
            print("🚀 მონაცემები წარმატებით წამოვიდა საჯარო API-დან და ჩაიწერა ბაზაში!")
        else:
            print(f"❌ სერვერმა დააბრუნა კოდი: {response.status_code}")
    except Exception as e:
        print(f"❌ კავშირის შეცდომა: {e}")


with app.app_context():
    db.create_all()
    
    user = User.query.filter_by(email="owner@test.com").first()
    if not user:
        user = User(
            username="test_agent",
            email="owner@test.com",
            phone="599112233",
            role="Owner",
            password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

    print("🧹 ვასუფთავებ ძველ მონაცემებს...")
    PropertyImage.query.delete()
    Property.query.delete()
    db.session.commit()

    fetch_from_open_api(user.id)

if __name__ == '__main__':
    app.run(debug=True)