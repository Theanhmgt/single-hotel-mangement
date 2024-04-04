import json
from distutils.util import strtobool
from flask import render_template, request, jsonify
from app import app
from app.services.guest_service import check_phone_number, register_guest
from app.services.tier_service import get_tiers, get_max_guests
from app.services.floor_service import get_floors


@app.route('/nhan-vien/lich-dat-phong/')
def home():
    return render_template('/receptionist/index.html')


@app.route('/nhan-vien/dat-phong/')
def booking():
    floors = get_floors()
    max_guests = get_max_guests()
    booking_id = request.args.get('ma')

    if not booking_id:
        max_guest = request.args.get('max_guest')
        floor = request.args.get('floor')
        tiers = get_tiers(max_guest=max_guest, floor=floor)

        return render_template('/receptionist/booking.html', tiers=tiers, floors=floors, max_guests=max_guests)
    else:
        # fetch booking detail by booking id
        bookings = [
            {
                "booking_id": "1",
                "customer_name": "John Doe",
                "check_in_date": "2024-04-10",
                "check_out_date": "2024-04-15",
                "room_type": "Deluxe Double Room",
                "num_of_guests": 2,
                "total_price": 600
            },
            {
                "booking_id": "2",
                "customer_name": "Jane Smith",
                "check_in_date": "2024-05-01",
                "check_out_date": "2024-05-07",
                "room_type": "Standard Single Room",
                "num_of_guests": 1,
                "total_price": 350
            },
            {
                "booking_id": "3",
                "customer_name": "Alice Johnson",
                "check_in_date": "2024-06-20",
                "check_out_date": "2024-06-25",
                "room_type": "Superior Suite",
                "num_of_guests": 3,
                "total_price": 900
            }
        ]
        room_id = request.args.get('phong')
        if any(b['booking_id'] == room_id for b in bookings):
            return render_template('/receptionist/room_detail.html', rooms=bookings, current_room=room_id)
        else:
            return render_template('/receptionist/room_detail.html', rooms=bookings,
                                   current_room=bookings[0]['booking_id'])


@app.route('/api/reception/add-guest/',methods=['post'])
def add_guest():
    data = json.loads(request.data)
    listData = {
        'last_name': data.get('last_name'),
        'first_name': data.get('first_name'),
        'birthdate': data.get('birthdate'),
        'phone_number': data.get('phone_number'),
        'city': data.get('city'),
        'district': data.get('district'),
        'address': data.get('address'),
        'foreigner':strtobool(data.get('foreigner').lower())
    }
    if check_phone_number(listData['phone_number']):  # user đã tồn tại
        return jsonify('0')

    try:
        register_guest(data=listData)
    except Exception as e:
        print(e)
        return jsonify('-1')

    return jsonify("1")

