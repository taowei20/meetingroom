from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, decode_token,
)
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from models import db, User, LoginLog
import secrets

auth_bp = Blueprint("auth", __name__)


def get_real_ip():
    if request.headers.get("X-Real-IP"):
        return request.headers["X-Real-IP"]
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or ""


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

    log = LoginLog(
        username=username+'/'+user.name,
        ip_address=get_real_ip(),
        user_agent=request.headers.get("User-Agent", ""),
    )
    db.session.add(log)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": access_token,
        "user": user.to_dict(),
    })


@auth_bp.route("/api/auth/verify", methods=["GET"])
def verify_token():
    token = request.args.get("token", "").strip()
    if token.lower().startswith("bearer"):
        token = token[len("bearer"):].strip()
    if not token:
        return jsonify({"error": "缺少token"}), 401

    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception:
        return jsonify({"error": "token无效或已过期"}), 401

    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "用户不存在或已禁用"}), 401

    frontend_url = getattr(Config, "FRONTEND_URL", "").rstrip("/")
    if frontend_url:
        target = f"{frontend_url}/?token={token}"
    else:
        target = f"/?token={token}"
    return redirect(target)


@auth_bp.route("/api/auth/password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "旧密码和新密码不能为空"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "新密码长度不能少于8位"}), 400

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


@auth_bp.route("/api/login-logs", methods=["GET"])
@jwt_required()
def list_login_logs():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "无权限"}), 403

    keyword = request.args.get("keyword", "").strip()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)

    query = LoginLog.query

    if keyword:
        query = query.filter(LoginLog.username.contains(keyword))

    total = query.count()
    logs = query.order_by(LoginLog.login_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        "items": [log.to_dict() for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


# ──────────────────────────────────────────────
# MCP 授权码管理
# ──────────────────────────────────────────────


@auth_bp.route("/api/auth/mcp-code", methods=["GET"])
@jwt_required()
def get_mcp_code():
    """获取当前用户的 MCP 授权码"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({
        "mcp_auth_code": user.mcp_auth_code,
        "has_mcp_code": user.mcp_auth_code is not None,
    })


@auth_bp.route("/api/auth/mcp-code", methods=["POST"])
@jwt_required()
def generate_mcp_code():
    """生成或刷新 MCP 授权码"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    user.mcp_auth_code = secrets.token_urlsafe(32)
    db.session.commit()
    return jsonify({
        "mcp_auth_code": user.mcp_auth_code,
        "message": "MCP授权码已生成，请妥善保管",
    })


@auth_bp.route("/api/auth/mcp-code", methods=["DELETE"])
@jwt_required()
def delete_mcp_code():
    """删除 MCP 授权码"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    user.mcp_auth_code = None
    db.session.commit()
    return jsonify({"message": "MCP授权码已删除"})


@auth_bp.route("/api/auth/mcp-verify", methods=["POST"])
def mcp_verify():
    """MCP 服务端验证授权码，返回用户信息和 JWT Token"""
    data = request.get_json()
    auth_code = data.get("auth_code", "").strip()

    if not auth_code:
        return jsonify({"error": "授权码不能为空"}), 400

    user = User.query.filter_by(mcp_auth_code=auth_code).first()
    if not user:
        return jsonify({"error": "授权码无效"}), 401

    if not user.is_active:
        return jsonify({"error": "账号已被禁用"}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": access_token,
        "user": user.to_dict(),
    })
