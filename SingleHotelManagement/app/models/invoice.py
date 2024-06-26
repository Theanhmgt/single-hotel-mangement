import enum
from datetime import datetime

from sqlalchemy import Column, Boolean, Integer, ForeignKey, event, Enum, DateTime
from sqlalchemy.dialects.mysql import DECIMAL
from app import db


class PaymentMethod(enum.Enum):
    CASH = 'CASH'
    VNPAY = 'VNPAY'


class Invoice(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    amount = Column(DECIMAL, nullable=False)
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime)

    payment_method = Column(Enum(PaymentMethod))

    # one-to-one relationship
    booking_id = Column(Integer, ForeignKey('booking.id'))

    def __str__(self):
        return "#{0}".format(self.id)