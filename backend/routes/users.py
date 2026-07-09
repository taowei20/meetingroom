from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User

users_bp = Blueprint("users", __name__)


def require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return None
    return user


@users_bp.route("/api/users", methods=["GET"])
@jwt_required()
def list_users():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    keyword = request.args.get("keyword", "").strip()
    query = User.query
    if keyword:
        query = query.filter(
            db.or_(
                User.username.contains(keyword),
                User.name.contains(keyword),
                User.department.contains(keyword),
            )
        )
    users = query.order_by(User.id.desc()).all()
    return jsonify([u.to_dict() for u in users])


@users_bp.route("/api/users", methods=["POST"])
@jwt_required()
def create_user():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    data = request.get_json()
    username = data.get("username", "").strip()
    name = data.get("name", "").strip()
    department = data.get("department", "").strip()
    phone = data.get("phone", "").strip()
    is_admin = data.get("is_admin", False)
    password = data.get("password", "123456")

    if not username or not name:
        return jsonify({"error": "登录账号和用户名不能为空"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "登录账号已存在"}), 400

    user = User(
        username=username,
        name=name,
        department=department,
        phone=phone,
        is_admin=is_admin,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@users_bp.route("/api/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    data = request.get_json()
    user.name = data.get("name", user.name)
    user.department = data.get("department", user.department)
    user.phone = data.get("phone", user.phone)
    user.is_admin = data.get("is_admin", user.is_admin)
    user.is_active = data.get("is_active", user.is_active)

    if "password" in data and data["password"]:
        user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify(user.to_dict())


@users_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "无权限"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    current_user_id = int(get_jwt_identity())
    if user.id == current_user_id:
        return jsonify({"error": "不能删除自己"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "删除成功"})
