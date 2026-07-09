from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config, get_server_config
from models import db, User
from werkzeug.security import generate_password_hash
import secrets


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

    CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)
    JWTManager(app)
    db.init_app(app)

    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.rooms import rooms_bp
    from routes.bookings import bookings_bp
    from routes.system_bookings import system_bookings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(system_bookings_bp)

    with app.app_context():
        db.create_all()
        migrate_db()
        init_data()

    return app


def migrate_db():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    
    if 'bookings' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('bookings')]
        if 'attachment' not in columns:
            db.session.execute(text("ALTER TABLE bookings ADD COLUMN attachment VARCHAR(255) DEFAULT ''"))
        if 'attachment_name' not in columns:
            db.session.execute(text("ALTER TABLE bookings ADD COLUMN attachment_name VARCHAR(255) DEFAULT ''"))
        if 'meeting_content' not in columns:
            db.session.execute(text("ALTER TABLE bookings ADD COLUMN meeting_content TEXT DEFAULT ''"))
    
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'is_active' not in columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
    
    db.session.commit()


def init_data():
    if User.query.first():
        return

    admin_password = secrets.token_urlsafe(8)
    admin = User(
        username="admin",
        name="系统管理员",
        department="信息技术部",
        phone="13800000000",
        is_admin=True,
        password_hash=generate_password_hash(admin_password),
    )

    db.session.add(admin)
    db.session.commit()

    print(f"\n{'='*50}")
    print(f"  初始管理员账号已创建")
    print(f"  用户名: admin")
    print(f"  密码:   {admin_password}")
    print(f"  请登录后立即修改密码!")
    print(f"{'='*50}\n")

    from models import Room
    rooms = [
        Room(room_code="RM" + str(i).zfill(6), name=f"{name}会议室", remark=remark)
        for i, name, remark in [
            (1, "A栋301", "可容纳10人，配有投影仪"),
            (2, "A栋302", "可容纳20人，配有视频会议系统"),
        ]
    ]
    db.session.add_all(rooms)
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    server_config = get_server_config()
    app.run(
        debug=server_config['debug'],
        host=server_config['host'],
        port=server_config['port']
    )
