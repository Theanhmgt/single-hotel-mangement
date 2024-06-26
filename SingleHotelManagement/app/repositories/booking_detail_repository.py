from sqlalchemy import func

from app import db, app
from app.models.booking_detail import BookingDetail
from app.models.room import Room, RoomStatus
from app.models.tier import Tier
from app.repositories.tier_repository import get_tier_by_room_id, get_tier_by_id
from distutils.util import strtobool


def get_booking_details_by_booking_id(booking_id):
    return db.session.query(BookingDetail).filter(BookingDetail.booking_id == booking_id).all()


def get_booking_detail_with_tier_by_booking_id(booking_id):
    return db.session.query(BookingDetail, Tier.id, Tier.name, Room.name).join(Room,
                                                                               Room.id == BookingDetail.room_id).join(
        Tier, Tier.id == Room.tier_id).filter(BookingDetail.booking_id == booking_id).all()


def add_guest_to_booking_detail(booking_id, room_id, foreigner):
    booking_detail = db.session.query(BookingDetail).filter(BookingDetail.room_id == room_id,
                                                            BookingDetail.booking_id == booking_id).first()
    if strtobool(foreigner):
        booking_detail.num_foreigner_guest += 1
    else:
        booking_detail.num_normal_guest += 1
    db.session.commit(booking_detail)
    return True


def change_num_guest(booking_id, num_foreigner_guest, num_normal_guest, room_id):
    booking_detail = db.session.query(BookingDetail).filter(BookingDetail.room_id == int(room_id),
                                                            BookingDetail.booking_id == int(booking_id)).first()
    tier = get_tier_by_room_id(room_id)
    booking_detail.num_foreigner_guest = int(num_foreigner_guest)
    booking_detail.num_normal_guest = int(num_normal_guest)

    booking_detail.set_price(tier.get_price(int(num_normal_guest), int(num_normal_guest)))

    db.session.commit()
    return True


def check_max_guest(room_id, num_foreigner_guest, num_normal_guest):
    tier = get_tier_by_room_id(room_id)
    return (int(num_foreigner_guest) + int(num_normal_guest)) >= tier.max_guest


def add_booking_detail_in_booking(booking_id=None, tier_id=None):
    # Get tier by id to calculate price
    tier = get_tier_by_id(int(tier_id))
    # Get available room
    rooms = db.session.query(Room).filter(Room.tier_id.__eq__(tier_id)).filter(
        Room.status.__eq__(RoomStatus.AVAILABLE)).all()
    if len(rooms) == 0:
        db.rollback()
        return None
    room = rooms[0]
    # Change status room
    room.status = RoomStatus.RESERVED

    # Create booking detail
    booking_detail = BookingDetail(
        booking_id=int(booking_id),
        room_id=room.id,
        num_normal_guest=1,  # set default
        price=tier.get_price(1, 0)
    )
    db.session.add(booking_detail)
    db.session.commit()
    return {
        'room_id': room.id
    }


def get_total_price(booking_id):
    query = db.session.query(func.sum(BookingDetail.price)).group_by(BookingDetail.booking_id).filter(BookingDetail.booking_id.__eq__(int(booking_id))).first()
    return int(query[0])
