from app.repositories.booking_repository import create_booking as cb, get_booking_by_id as gb, cancel_booking as cb


def create_booking(data):
    return cb(data)


def cancel_booking(booking_id):
    cb(booking_id=booking_id)


def get_booking_by_id(id):
    return gb(id).to_dict()