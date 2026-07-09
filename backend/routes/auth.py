from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "用户名或密码错误"}), 401

    if not user.is_active:
        return jsonify({"error": "账号已被禁用，请联系管理员"}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": access_token,
        "user": user.to_dict(),
    })


@auth_bp.route("/api/auth/password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "旧密码和新密码不能为空"}), 400

    if len(new_password) < 4:
        return jsonify({"error": "新密码长度不能少于4位"}), 400

    user = User.query.get(user_id)
    if not user or not check_password_hash(user.password_hash, old_password):
        return jsonify({"error": "旧密码错误"}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "密码修改成功"})


@auth_bp.route("/api/users/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(user.to_dict())


@auth_bp.route("/api/users/me", methods=["PUT"])
@jwt_required()
def update_current_user():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    user.name = data.get("name", user.name)
    user.department = data.get("department", user.department)
    user.phone = data.get("phone", user.phone)
    db.session.commit()
    return jsonify(user.to_dict())
