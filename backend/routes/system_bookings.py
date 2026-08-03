from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_
from models import db, User, Room, SystemBooking
import json

system_bookings_bp = Blueprint("system_bookings", __name__)


def require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return None
    return user


def parse_ignore_dates(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(d) for d in raw]
    return []


@system_bookings_bp.route("/api/system-bookings", methods=["GET"])
@jwt_required()
def list_system_bookings():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    bookings = SystemBooking.query.order_by(
        SystemBooking.weekday.asc(), SystemBooking.start_time.asc()
    ).all()
    return jsonify([b.to_dict() for b in bookings])


@system_bookings_bp.route("/api/system-bookings", methods=["POST"])
@jwt_required()
def create_system_booking():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    data = request.get_json()
    room_id = data.get("room_id")
    weekday = data.get("weekday")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    remark = data.get("remark", "系统预订")
    ignore_dates = parse_ignore_dates(data.get("ignore_dates"))

    if not room_id or weekday is None or not start_time or not end_time:
        return jsonify({"error": "缺少必填参数"}), 400

    if start_time >= end_time:
        return jsonify({"error": "结束时间必须大于开始时间"}), 400

    room = Room.query.get(room_id)
    if not room or not room.is_active:
        return jsonify({"error": "会议室不存在或已停用"}), 400

    conflict = SystemBooking.query.filter(
        and_(
            SystemBooking.room_id == room_id,
            SystemBooking.weekday == weekday,
            SystemBooking.is_active == True,
            SystemBooking.start_time < end_time,
            SystemBooking.end_time > start_time,
        )
    ).first()

    if conflict:
        return jsonify({"error": "该时间段已有系统预订"}), 400

    booking = SystemBooking(
        room_id=room_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        remark=remark,
    )
    booking.set_ignore_dates(ignore_dates)
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201


@system_bookings_bp.route("/api/system-bookings/<int:booking_id>", methods=["PUT"])
@jwt_required()
def update_system_booking(booking_id):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    booking = SystemBooking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "系统预订不存在"}), 404

    data = request.get_json()
    booking.room_id = data.get("room_id", booking.room_id)
    booking.weekday = data.get("weekday", booking.weekday)
    booking.start_time = data.get("start_time", booking.start_time)
    booking.end_time = data.get("end_time", booking.end_time)
    booking.remark = data.get("remark", booking.remark)
    booking.is_active = data.get("is_active", booking.is_active)
    if "ignore_dates" in data:
        booking.set_ignore_dates(parse_ignore_dates(data.get("ignore_dates")))
    db.session.commit()
    return jsonify(booking.to_dict())


@system_bookings_bp.route("/api/system-bookings/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def delete_system_booking(booking_id):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    booking = SystemBooking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "系统预订不存在"}), 404

    db.session.delete(booking)
    db.session.commit()
    return jsonify({"message": "删除成功"})
