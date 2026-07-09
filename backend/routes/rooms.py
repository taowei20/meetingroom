import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Room

rooms_bp = Blueprint("rooms", __name__)


def require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return None
    return user


def generate_room_code():
    return "RM" + uuid.uuid4().hex[:6].upper()


@rooms_bp.route("/api/rooms", methods=["GET"])
@jwt_required()
def list_rooms():
    keyword = request.args.get("keyword", "").strip()
    query = Room.query
    if keyword:
        query = query.filter(
            db.or_(
                Room.room_code.contains(keyword),
                Room.name.contains(keyword),
            )
        )
    rooms = query.order_by(Room.id.asc()).all()
    return jsonify([r.to_dict() for r in rooms])


@rooms_bp.route("/api/rooms", methods=["POST"])
@jwt_required()
def create_room():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    data = request.get_json()
    name = data.get("name", "").strip()
    remark = data.get("remark", "").strip()

    if not name:
        return jsonify({"error": "会议室名称不能为空"}), 400

    room = Room(
        room_code=generate_room_code(),
        name=name,
        remark=remark,
    )
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201


@rooms_bp.route("/api/rooms/<int:room_id>", methods=["PUT"])
@jwt_required()
def update_room(room_id):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "会议室不存在"}), 404

    data = request.get_json()
    room.name = data.get("name", room.name)
    room.remark = data.get("remark", room.remark)
    room.is_active = data.get("is_active", room.is_active)
    db.session.commit()
    return jsonify(room.to_dict())


@rooms_bp.route("/api/rooms/<int:room_id>", methods=["DELETE"])
@jwt_required()
def delete_room(room_id):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "会议室不存在"}), 404

    db.session.delete(room)
    db.session.commit()
    return jsonify({"message": "删除成功"})
