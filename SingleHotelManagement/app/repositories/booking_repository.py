import datetime
from sqlalchemy.sql.functions import concat, func, coalesce
from app import db
from app.models.booking import Booking, BookingStatus
from app.models.booking_detail import BookingDetail
from app.models.room import Room, RoomStatus
from distutils.util import strtobool
from app.models.tier import Tier
from app.models.user import User
from app.repositories.tier_repository import get_tier_by_id


def create_booking_offline(data):
    booking = Booking(
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        status=BookingStatus.REQUESTED,
        receptionist_id=data.get('receptionist_id'),
        booker_id=data.get('booker_id')
    )
    db.session.add(booking)

    # Get available room
    rooms = db.session.query(Room).filter(Room.tier_id.__eq__(data.get('tier_id'))).filter(
        Room.status.__eq__(RoomStatus.AVAILABLE)).all()
    if len(rooms) == 0:
        db.rollback()
        return None
    room = rooms[0]
    # Change status room
    room.status = RoomStatus.RESERVED
    # Create booking detail
    booking_detail = BookingDetail(
        booking_id=booking.id,
        room_id=room.id,
    )
    db.session.add(booking_detail)
    # Cap nhap so luong khach
    if strtobool(data.get('foreigner').lower()):
        booking_detail.num_foreigner_guest = 1
    else:
        booking_detail.num_normal_guest = 1
    # Cap nhap gia tien
    tier = get_tier_by_id(int(data.get('tier_id')))
    booking_detail_price = tier.get_price(booking_detail.num_normal_guest, booking_detail.num_foreigner_guest)
    booking_detail.set_price(booking_detail_price)

    db.session.commit()
    return {
        'booking': booking.to_dict(),
        'room': room.to_dict()
    }


def create_booking_online(data):
    booking = Booking(
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        status=BookingStatus.REQUESTED,
        booker_id=data.get('booker_id')
    )
    db.session.add(booking)
    for r in data.get('rooms'):
        # Get available room
        rooms = db.session.query(Room).filter(Room.tier_id.__eq__(r['id']),Room.status.__eq__(RoomStatus.AVAILABLE)).all()
        if len(rooms) == 0:
            db.rollback()
            return None
        for x in range(r['quantity']):
            room = rooms[x]
            # Change status room
            room.status = RoomStatus.RESERVED
            # Create booking detail
            booking_detail = BookingDetail(
                booking_id=booking.id,
                room_id=room.id,
                num_foreigner_guest=r['foreignNum'],
                num_normal_guest=r['domesticNum'],
                price=r['price'] / r['quantity']
            )
            db.session.add(booking_detail)

    db.session.commit()
    return {
        'booking': booking.to_dict(),
    }


def get_booking_by_id(booking_id):
    return db.session.query(Booking).filter(Booking.id == booking_id).first()


def cancel_booking(booking_id):
    booking = get_booking_by_id(booking_id)
    booking.status = BookingStatus.CANCELED
    db.session.commit()
    set_status_room_by_booking_id(booking_id, RoomStatus.AVAILABLE)


def check_out(booking_id):
    booking = get_booking_by_id(booking_id)
    booking.status = BookingStatus.CHECKED_OUT
    booking.checkout = datetime.datetime.now()
    db.session.commit()
    set_status_room_by_booking_id(booking_id, RoomStatus.AVAILABLE)


def check_in(booking_id):
    booking = get_booking_by_id(booking_id)
    booking.status = BookingStatus.CHECKED_IN
    booking.checkin = datetime.datetime.now()
    db.session.commit()
    set_status_room_by_booking_id(booking_id, RoomStatus.OCCUPIED)


def reserve(booking_id):
    booking = get_booking_by_id(booking_id)
    booking.status = BookingStatus.CONFIRMED
    db.session.commit()
    set_status_room_by_booking_id(booking_id, RoomStatus.RESERVED)


def set_status_room_by_booking_id(booking_id, status_room):
    booking_details = db.session.query(Room).join(BookingDetail, Room.id == BookingDetail.room_id).filter(
        BookingDetail.booking_id == booking_id).all()

    # Cập nhật trạng thái của các phòng
    for room in booking_details:
        room.status = status_room

    db.session.commit()


def list_booking(status_values=None, limit=None):
    query = db.session.query(Booking, func.sum(BookingDetail.price),
                             concat(func.group_concat(Room.name)).label('room_names'),
                             coalesce(concat(User.first_name, User.last_name), 'Khách lẻ').label(
                                 'guest'), concat(func.group_concat(Room.id)).label('room_id')).select_from(
        Booking).join(
        BookingDetail, BookingDetail.booking_id == Booking.id,
        isouter=True).join(User,
                           Booking.booker_id == User.id,
                           isouter=True).join(Room,
                                              BookingDetail.room_id == Room.id,
                                              isouter=True).join(Tier, Tier.id == Room.tier_id).group_by(
        Booking).order_by(Booking.id.desc())
    if limit is not None:
        query = query.limit(limit)

    if status_values is None or len(status_values) == 0:
        query = query.all()
    else:
        # status_values ['3,99,5']
        status_enum_values = [BookingStatus(int(value)) for value in status_values[0].split(',')]
        query = query.filter(Booking.status.in_(status_enum_values)).all()

    booking_dict = []
    # Convert to dict
    for booking in query:
        temp = {
            'booking': booking[0].to_dict(),
            'price': booking[1],
            'rooms': booking[2],
            'booker': booking[3],
            'rooms_id': booking[4]
        }
        booking_dict.append(temp)

    return booking_dict


def retrieve_booking(booking_id):
    query = db.session.query(Booking, func.sum(BookingDetail.price),
                             concat(func.group_concat(Room.name)).label('room_names'),
                             coalesce(concat(User.first_name, User.last_name), 'Khách lẻ').label(
                                 'guest'), concat(func.group_concat(Room.id)).label('room_id')).select_from(
        Booking).filter(Booking.id.__eq__(int(booking_id))).join(
        BookingDetail, BookingDetail.booking_id == Booking.id,
        isouter=True).join(User,
                           Booking.booker_id == User.id,
                           isouter=True).join(Room,
                                              BookingDetail.room_id == Room.id,
                                              isouter=True).group_by(Booking).first()

    return {
        'booking': query[0].to_dict(),
        'price': query[1],
        'rooms': query[2],
        'booker': query[3],
        'rooms_id': query[4]
    }


def get_total_price_by_booking_id(id):
    return db.session.query(Tier).join(Room, Room.tier_id == Tier.id).join(BookingDetail,
                                                                           BookingDetail.room_id == Room.id).join(
        Booking, Booking.id == BookingDetail.booking_id).group_by(BookingDetail.room_id).all()


def count_booking():
    return db.session.query(Booking).count();
