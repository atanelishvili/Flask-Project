import requests
from flask import render_template, request, redirect, url_for, flash, session
from . import properties_bp
from models import db, Property, PropertyImage, Favorite, ContactRequest
from decorators import login_required, roles_required
from datetime import datetime

@properties_bp.route('/')
def index():
    
    Property.query.filter(Property.expires_at < datetime.utcnow(), Property.is_active == True).update({Property.is_active: False})
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'date_desc')

    
    query = Property.query.filter_by(is_active=True)

    
    city = request.args.get('city', '').strip()
    type_ = request.args.get('type', '').strip()
    deal_type = request.args.get('deal_type', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    rooms = request.args.get('rooms')

    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if type_:
        query = query.filter_by(type=type_)
    if deal_type:
        query = query.filter_by(deal_type=deal_type)
    if min_price and min_price.isdigit():
        query = query.filter(Property.price >= float(min_price))
    if max_price and max_price.isdigit():
        query = query.filter(Property.price <= float(max_price))
    if rooms and rooms.isdigit():
        query = query.filter_by(rooms=int(rooms))

    
    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    else:
        query = query.order_by(Property.created_at.desc())

    
    pagination = query.paginate(page=page, per_page=9, error_out=False)
    
    
    user_fav_ids = []
    if 'user_id' in session:
        user_fav_ids = [f.property_id for f in Favorite.query.filter_by(user_id=session['user_id']).all()]

    return render_template('index.html', 
                           pagination=pagination, 
                           properties=pagination.items, 
                           user_fav_ids=user_fav_ids,
                           search_params=request.args)

@properties_bp.route('/property/<int:id>', methods=['GET', 'POST'])
def detail(id):
    prop = Property.query.get_or_404(id)
    
    
    viewed_key = f"viewed_{id}"
    if viewed_key not in session:
        prop.views += 1
        db.session.commit()
        session[viewed_key] = True

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        req = ContactRequest(property_id=id, name=name, phone=phone, message=message)
        db.session.add(req)
        db.session.commit()
        flash('საკონტაქტო მოთხოვნა წარმატებით გაიგზავნა მფლობელთან!', 'success')
        return redirect(url_for('properties.detail', id=id))

    return render_template('property_detail.html', property=prop)

@properties_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('Owner', 'Agent')
def create():
    if request.method == 'POST':
        p_type = request.form.get('type')
        deal_type = request.form.get('deal_type')
        price = float(request.form.get('price'))
        area = float(request.form.get('area'))
        rooms = int(request.form.get('rooms'))
        city = request.form.get('city')
        address = request.form.get('address')
        description = request.form.get('description')
        
        
        urls = request.form.getlist('images')
        valid_urls = [u.strip() for u in urls if u.strip()]

        if len(valid_urls) < 3:
            flash('გთხოვთ მიუთითოთ მინიმუმ 3 სურათის ლინკი!', 'error')
            return redirect(url_for('properties.create'))

        
        lat, lon = None, None
        api_url = f"https://nominatim.openstreetmap.org/search?q={address}, {city}&format=json&countrycodes=ge"
        headers = {'User-Agent': 'FinalRealEstateApp/1.0'}
        try:
            res = requests.get(api_url, headers=headers).json()
            if res:
                lat = float(res[0]['lat'])
                lon = float(res[0]['lon'])
        except Exception:
            pass 

        prop = Property(user_id=session['user_id'], type=p_type, deal_type=deal_type, price=price,
                        area_sqm=area, rooms=rooms, city=city, address=address, lat=lat, lon=lon, description=description)
        db.session.add(prop)
        db.session.flush() 

        for index, url in enumerate(valid_urls):
            img = PropertyImage(property_id=prop.id, image_url=url, order=index+1)
            db.session.add(img)
        
        db.session.commit()
        flash('განცხადება წარმატებით აიტვირთა!', 'success')
        return redirect(url_for('properties.index'))

    return render_template('create_property.html')

@properties_bp.route('/favorite/toggle/<int:id>')
@login_required
def toggle_favorite(id):
    fav = Favorite.query.filter_by(user_id=session['user_id'], property_id=id).first()
    if fav:
        db.session.delete(fav)
        flash('წაიშალა სანიშნეებიდან!', 'success')
    else:
        new_fav = Favorite(user_id=session['user_id'], property_id=id)
        db.session.add(new_fav)
        flash('დაემატა სანიშნეებში!', 'success')
    db.session.commit()
    return redirect(request.referrer or url_for('properties.index'))

@properties_bp.route('/favorites')
@login_required
def favorites():
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    return render_template('favorites.html', favorites=favs)

@properties_bp.route('/compare/add/<int:id>')
def add_to_compare(id):
    compare_list = session.get('compare', [])
    if id not in compare_list:
        if len(compare_list) >= 3:
            flash('შესადარებლად შეგიძლიათ მაქსიმუმ 3 ქონების არჩევა!', 'error')
        else:
            compare_list.append(id)
            session['compare'] = compare_list
            flash('ქონება დაემატა შესადარებელ სიას!', 'success')
    else:
        flash('ეს ქონება უკვე დამატებულია შესადარებელ სიაში!', 'error')
    return redirect(request.referrer or url_for('properties.index'))

@properties_bp.route('/compare')
def compare():
    ids = session.get('compare', [])
    props = Property.query.filter(Property.id.in_(ids)).all() if ids else []
    return render_template('comparison.html', properties=props)

@properties_bp.route('/compare/remove/<int:id>')
def remove_from_compare(id):
    compare_list = session.get('compare', [])
    if id in compare_list:
        compare_list.remove(id)
        session['compare'] = compare_list
        flash('ქონება მოიხსნა შედარებიდან!', 'success')
    return redirect(url_for('properties.compare'))

@properties_bp.route('/compare/clear')
def clear_compare():
    session.pop('compare', None)
    flash('შედარების სია გასუფთავდა!', 'success')
    return redirect(url_for('properties.compare'))