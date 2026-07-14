import os
import uuid
import calendar
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_
from werkzeug.utils import secure_filename
from models import db, User, Room, Booking, SystemBooking
from config import Config

bookings_bp = Blueprint("bookings", __name__)

UPLOAD_FOLDER = Config.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@bookings_bp.route("/api/bookings", methods=["GET"])
@jwt_required()
def list_bookings():
    from models import SystemBooking
    date_str = request.args.get("date", "")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "日期格式错误"}), 400
    else:
        target_date = date.today()

    bookings = Booking.query.filter(
        and_(
            Booking.booking_date == target_date,
            Booking.status == "active",
        )
    ).all()

    weekday = target_date.weekday()
    js_weekday = (weekday + 1) % 7
    system_bookings = SystemBooking.query.filter(
        and_(
            SystemBooking.weekday == js_weekday,
            SystemBooking.is_active == True,
        )
    ).all()

    result = [b.to_dict() for b in bookings]
    for sb in system_bookings:
        result.append({
            "id": f"sys_{sb.id}",
            "room_id": sb.room_id,
            "user_id": 0,
            "booking_date": target_date.isoformat(),
            "start_time": sb.start_time,
            "end_time": sb.end_time,
            "status": "active",
            "meeting_content": sb.remark,
            "is_system": True,
            "room_name": sb.room.name if sb.room else None,
            "room_code": sb.room.room_code if sb.room else None,
            "user_name": "系统预订",
            "user_department": "",
            "user_phone": "",
        })

    return jsonify(result)


@bookings_bp.route("/api/bookings/month", methods=["GET"])
@jwt_required()
def list_month_bookings():
    from models import SystemBooking
    year_str = request.args.get("year", "")
    month_str = request.args.get("month", "")

    try:
        year = int(year_str)
        month = int(month_str)
        if not (1 <= month <= 12):
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "年月参数错误"}), 400

    last_day = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    bookings = Booking.query.filter(
        and_(
            Booking.booking_date >= start_date,
            Booking.booking_date <= end_date,
            Booking.status == "active",
        )
    ).all()

    result = [b.to_dict() for b in bookings]

    for day in range(1, last_day + 1):
        d = date(year, month, day)
        js_weekday = (d.weekday() + 1) % 7
        system_bookings = SystemBooking.query.filter(
            and_(
                SystemBooking.weekday == js_weekday,
                SystemBooking.is_active == True,
            )
        ).all()
        for sb in system_bookings:
            result.append({
                "id": f"sys_{sb.id}_{day}",
                "room_id": sb.room_id,
                "user_id": 0,
                "booking_date": d.isoformat(),
                "start_time": sb.start_time,
                "end_time": sb.end_time,
                "status": "active",
                "meeting_content": sb.remark,
                "is_system": True,
                "room_name": sb.room.name if sb.room else None,
                "room_code": sb.room.room_code if sb.room else None,
                "user_name": "系统预订",
                "user_department": "",
                "user_phone": "",
            })

    return jsonify(result)


@bookings_bp.route("/api/bookings", methods=["POST"])
@jwt_required()
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    room_id = data.get("room_id")
    booking_date_str = data.get("booking_date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    meeting_content = data.get("meeting_content", "")

    if not room_id or not booking_date_str or not start_time or not end_time:
        return jsonify({"error": "缺少必填参数"}), 400

    try:
        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "日期格式错误"}), 400

    today = date.today()
    max_date = today + timedelta(days=21)
    if booking_date < today:
        return jsonify({"error": "不能预订当天以前的日期"}), 400
    if booking_date > max_date:
        return jsonify({"error": "只能预订15天内的会议室"}), 400

    if start_time >= end_time:
        return jsonify({"error": "结束时间必须大于开始时间"}), 400

    room = Room.query.get(room_id)
    if not room or not room.is_active:
        return jsonify({"error": "会议室不存在或已停用"}), 400

    conflict = Booking.query.filter(
        and_(
            Booking.room_id == room_id,
            Booking.booking_date == booking_date,
            Booking.status == "active",
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        )
    ).first()

    if conflict:
        return jsonify({"error": "该时间段已被预订"}), 400

    weekday = booking_date.weekday()
    js_weekday = (weekday + 1) % 7
    system_conflict = SystemBooking.query.filter(
        and_(
            SystemBooking.room_id == room_id,
            SystemBooking.weekday == js_weekday,
            SystemBooking.is_active == True,
            SystemBooking.start_time < end_time,
            SystemBooking.end_time > start_time,
        )
    ).first()

    if system_conflict:
        return jsonify({"error": "该时间段为系统预订时段，无法预订"}), 400

    booking = Booking(
        room_id=room_id,
        user_id=user_id,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        status="active",
        meeting_content=meeting_content,
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201


@bookings_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "预订不存在"}), 404

    if not user.is_admin and booking.user_id != user_id:
        return jsonify({"error": "无权限取消此预订"}), 403

    booking.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "取消成功"})


@bookings_bp.route("/api/bookings/my", methods=["GET"])
@jwt_required()
def my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(
        user_id=user_id, status="active"
    ).order_by(
        Booking.booking_date.desc(), Booking.start_time.asc()
    ).all()
    return jsonify([b.to_dict() for b in bookings])


@bookings_bp.route("/api/bookings/my/history", methods=["GET"])
@jwt_required()
def my_bookings_history():
    user_id = int(get_jwt_identity())
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)

    query = Booking.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    bookings = query.order_by(
        Booking.booking_date.desc(), Booking.start_time.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        "items": [b.to_dict() for b in bookings],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@bookings_bp.route("/api/bookings/all", methods=["GET"])
@jwt_required()
def all_bookings():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "无权限"}), 403

    status = request.args.get("status", "")
    keyword = request.args.get("keyword", "").strip()
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)

    query = Booking.query

    if status:
        query = query.filter_by(status=status)

    if keyword:
        query = query.join(User).join(Room).filter(
            or_(
                User.name.contains(keyword),
                User.username.contains(keyword),
                Room.name.contains(keyword),
                Room.room_code.contains(keyword),
            )
        )

    if date_from:
        try:
            d = datetime.strptime(date_from, "%Y-%m-%d").date()
            query = query.filter(Booking.booking_date >= d)
        except ValueError:
            pass

    if date_to:
        try:
            d = datetime.strptime(date_to, "%Y-%m-%d").date()
            query = query.filter(Booking.booking_date <= d)
        except ValueError:
            pass

    total = query.count()
    bookings = query.order_by(
        Booking.booking_date.desc(), Booking.start_time.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        "items": [b.to_dict() for b in bookings],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@bookings_bp.route("/api/bookings/<int:booking_id>/transfer", methods=["PUT"])
@jwt_required()
def transfer_booking(booking_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "无权限"}), 403

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "预订不存在"}), 404

    data = request.get_json()
    new_user_id = data.get("user_id")

    if not new_user_id:
        return jsonify({"error": "请选择新的预订人"}), 400

    new_user = User.query.get(new_user_id)
    if not new_user:
        return jsonify({"error": "用户不存在"}), 404

    booking.user_id = new_user_id
    db.session.commit()
    return jsonify(booking.to_dict())


@bookings_bp.route("/api/bookings/<int:booking_id>/attachment", methods=["POST"])
@jwt_required()
def upload_attachment(booking_id):
    user_id = int(get_jwt_identity())

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "预订不存在"}), 404

    user = User.query.get(user_id)
    if not user.is_admin and booking.user_id != user_id:
        return jsonify({"error": "无权限"}), 403

    if "file" not in request.files:
        return jsonify({"error": "请选择文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "请选择文件"}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1].lower().lstrip(".") or "dat"
    if ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({"error": f"不支持的文件类型，允许: {', '.join(Config.ALLOWED_EXTENSIONS)}"}), 400

    filename = f"booking_{booking_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    safe_name = secure_filename(file.filename) or "attachment"
    booking.attachment = filename
    booking.attachment_name = safe_name
    db.session.commit()

    return jsonify({"message": "上传成功", "filename": filename, "name": safe_name})


@bookings_bp.route("/api/uploads/<filename>", methods=["GET"])
@jwt_required()
def download_file(filename):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    basename = os.path.basename(filename)
    booking = Booking.query.filter_by(attachment=basename).first()
    if not booking:
        return jsonify({"error": "文件不存在"}), 404

    if not user.is_admin and booking.user_id != user_id:
        return jsonify({"error": "无权限下载此文件"}), 403

    return send_from_directory(UPLOAD_FOLDER, basename, as_attachment=True)


@bookings_bp.route("/api/users/options", methods=["GET"])
@jwt_required()
def user_options():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "无权限"}), 403

    keyword = request.args.get("keyword", "").strip()
    query = User.query
    if keyword:
        query = query.filter(
            or_(
                User.name.contains(keyword),
                User.username.contains(keyword),
            )
        )
    users = query.order_by(User.id.asc()).all()
    return jsonify([{"id": u.id, "name": u.name, "username": u.username, "department": u.department} for u in users])


@bookings_bp.route("/api/stats/overview", methods=["GET"])
@jwt_required()
def stats_overview():
    today = date.today()

    today_count = Booking.query.filter_by(
        booking_date=today, status="active"
    ).count()

    total_rooms = Room.query.filter_by(is_active=True).count()

    total_bookings = Booking.query.filter_by(status="active").count()

    recent_bookings = Booking.query.filter(
        and_(
            Booking.booking_date >= today,
            Booking.status == "active",
        )
    ).order_by(
        Booking.booking_date.asc(), Booking.start_time.asc()
    ).limit(10).all()

    week_data = []
    for i in range(7):
        d = date.fromordinal(today.toordinal() + i)
        count = Booking.query.filter_by(booking_date=d, status="active").count()
        week_data.append({"date": d.isoformat(), "count": count})

    return jsonify({
        "today_count": today_count,
        "total_rooms": total_rooms,
        "total_bookings": total_bookings,
        "recent_bookings": [b.to_dict() for b in recent_bookings],
        "week_data": week_data,
    })
