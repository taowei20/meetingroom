from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), default="")
    phone = db.Column(db.String(20), default="")
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    mcp_auth_code = db.Column(db.String(64), unique=True, nullable=True, default=None)
    created_at = db.Column(db.DateTime, default=datetime.now)

    bookings = db.relationship("Booking", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "department": self.department,
            "phone": self.phone,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "has_mcp_code": self.mcp_auth_code is not None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    remark = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    bookings = db.relationship("Booking", backref="room", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "room_code": self.room_code,
            "name": self.name,
            "remark": self.remark,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        db.Index("ix_bookings_room_date", "room_id", "booking_date", "status"),
        db.Index("ix_bookings_user_date", "user_id", "booking_date"),
        db.Index("ix_bookings_date_status", "booking_date", "status"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    status = db.Column(db.String(20), default="active")
    meeting_content = db.Column(db.Text, default="")
    attachment = db.Column(db.String(255), default="")
    attachment_name = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "user_id": self.user_id,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "meeting_content": self.meeting_content,
            "attachment": self.attachment,
            "attachment_name": self.attachment_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "room_name": self.room.name if self.room else None,
            "room_code": self.room.room_code if self.room else None,
            "user_name": self.user.name if self.user else None,
            "user_department": self.user.department if self.user else None,
            "user_phone": self.user.phone if self.user else None,
        }


class LoginLog(db.Model):
    __tablename__ = "login_logs"
    __table_args__ = (
        db.Index("ix_login_logs_time", "login_time"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), default="")
    user_agent = db.Column(db.String(500), default="")
    login_time = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "login_time": self.login_time.isoformat() if self.login_time else None,
        }


class SystemBooking(db.Model):
    __tablename__ = "system_bookings"
    __table_args__ = (
        db.Index("ix_sys_room_weekday", "room_id", "weekday", "is_active"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    remark = db.Column(db.String(255), default="系统预订")
    ignore_dates = db.Column(db.Text, default="[]")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    room = db.relationship("Room", backref="system_bookings")

    def get_ignore_dates(self):
        import json
        try:
            return json.loads(self.ignore_dates or "[]")
        except (ValueError, TypeError):
            return []

    def set_ignore_dates(self, dates):
        import json
        self.ignore_dates = json.dumps(dates or [])

    def is_date_ignored(self, target_date):
        if not target_date:
            return False
        return target_date.isoformat() in self.get_ignore_dates()

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "weekday": self.weekday,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "remark": self.remark,
            "ignore_dates": self.get_ignore_dates(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "room_name": self.room.name if self.room else None,
            "room_code": self.room.room_code if self.room else None,
        }
