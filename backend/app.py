from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import event
from config import Config, get_server_config
from models import db, User
from werkzeug.security import generate_password_hash
import secrets


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
    app.config["SQLALCHEMY_SESSION_OPTIONS"] = {"expire_on_commit": False}

    CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)
    JWTManager(app)
    db.init_app(app)

    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            try:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA busy_timeout=30000")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
            except Exception:
                pass

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
        if 'mcp_auth_code' not in columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN mcp_auth_code VARCHAR(64) DEFAULT NULL"))

    if 'system_bookings' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('system_bookings')]
        if 'ignore_dates' not in columns:
            db.session.execute(text("ALTER TABLE system_bookings ADD COLUMN ignore_dates TEXT DEFAULT '[]'"))

    index_names = {ix['name'] for ix in inspector.get_indexes('bookings')}
    if 'ix_bookings_room_date' not in index_names:
        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_bookings_room_date ON bookings (room_id, booking_date, status)"))
    if 'ix_bookings_user_date' not in index_names:
        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_bookings_user_date ON bookings (user_id, booking_date)"))
    if 'ix_bookings_date_status' not in index_names:
        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_bookings_date_status ON bookings (booking_date, status)"))

    if 'login_logs' in inspector.get_table_names():
        ll_indexes = {ix['name'] for ix in inspector.get_indexes('login_logs')}
        if 'ix_login_logs_time' not in ll_indexes:
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_login_logs_time ON login_logs (login_time)"))

    if 'system_bookings' in inspector.get_table_names():
        sb_indexes = {ix['name'] for ix in inspector.get_indexes('system_bookings')}
        if 'ix_sys_room_weekday' not in sb_indexes:
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_sys_room_weekday ON system_bookings (room_id, weekday, is_active)"))

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
    print(f"  密码:   {admin_password}",flush = True)
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
