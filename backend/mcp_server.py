"""
会议室预订系统 MCP 服务端 (Streamable HTTP)

多 Agent 多用户隔离：
- 每个 Agent 在配置中携带自己的授权码（URL 参数或请求头）
- 服务端按授权码缓存独立的 token/user，用户身份互不影响，防止越权操作

配置方式:
  OpenCode / Claude Desktop / Cursor:
    "url": "http://127.0.0.1:8080/mcp?auth_code=你的授权码"

  或通过请求头:
    headers: { "X-Auth-Code": "你的授权码" }

授权码获取:
  Web 端登录 → 个人信息 → 生成MCP授权码
"""

import os
import argparse
import logging
from datetime import date
from typing import Any
from urllib.parse import parse_qs

import httpx
import uvicorn
import contextvars
from mcp.server import MCPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("meeting-room-mcp")

API_BASE = os.environ.get("MEETING_ROOM_API_URL", "http://127.0.0.1:5000")

# 当前请求的授权码（每个 HTTP 请求独立上下文）
current_auth_code: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_auth_code", default=""
)

# 授权码 -> {token, user} 缓存，实现按用户隔离的登录状态
_auth_cache: dict[str, dict[str, Any]] = {}


def get_auth_code() -> str:
    """获取当前请求的授权码"""
    return current_auth_code.get()


async def do_login(auth_code: str = "", username: str = "", password: str = "") -> dict:
    """执行登录，返回 token 和用户信息"""
    if auth_code:
        url = f"{API_BASE}/api/auth/mcp-verify"
        payload = {"auth_code": auth_code}
    else:
        url = f"{API_BASE}/api/auth/login"
        payload = {"username": username, "password": password}

    async with httpx.AsyncClient(timeout=15, verify=False) as client:
        resp = await client.post(url, json=payload)

    data = resp.json()
    if resp.status_code != 200:
        raise RuntimeError(data.get("error", "登录失败"))

    return {"token": data["token"], "user": data["user"]}


def get_session(code: str) -> dict[str, Any]:
    """获取某个授权码对应的会话状态"""
    if code not in _auth_cache:
        _auth_cache[code] = {"token": None, "user": None, "auth_code": code}
    return _auth_cache[code]


async def ensure_login(session: dict) -> bool:
    """确保会话已登录"""
    if session["token"]:
        return True
    if not session["auth_code"]:
        return False
    try:
        result = await do_login(auth_code=session["auth_code"])
        session["token"] = result["token"]
        session["user"] = result["user"]
        return True
    except Exception as e:
        logger.error(f"自动登录失败: {e}")
        return False


async def api_call(method: str, path: str, json_data=None, params=None) -> dict | list:
    """调用 Flask 后端 API，使用当前请求对应授权码的用户身份"""
    code = get_auth_code()
    if not code:
        raise RuntimeError(
            "未配置授权码。请在 MCP 配置 URL 中添加 ?auth_code=你的授权码，或在请求头中设置 X-Auth-Code。"
        )

    session = get_session(code)
    if not await ensure_login(session):
        raise RuntimeError("登录失败，请检查授权码是否正确。")

    url = f"{API_BASE}{path}"
    headers = {"Authorization": f"Bearer {session['token']}"}

    async with httpx.AsyncClient(timeout=15, verify=False) as client:
        resp = await client.request(method, url, json=json_data, params=params, headers=headers)

    # Token 过期，尝试用授权码重新登录后重试一次
    if resp.status_code == 401 and session["auth_code"]:
        logger.warning("Token 过期，尝试用授权码重新登录...")
        try:
            result = await do_login(auth_code=session["auth_code"])
            session["token"] = result["token"]
            session["user"] = result["user"]
            headers["Authorization"] = f"Bearer {session['token']}"
            async with httpx.AsyncClient(timeout=15, verify=False) as client:
                resp = await client.request(method, url, json=json_data, params=params, headers=headers)
        except Exception:
            raise RuntimeError("认证已过期，请重新生成授权码。")

    data = resp.json()
    if resp.status_code >= 400:
        raise RuntimeError(data.get("error", f"请求失败: HTTP {resp.status_code}"))
    return data


def format_booking(b: dict) -> str:
    parts = [
        f"预订ID: {b['id']}",
        f"会议室: {b.get('room_name', '')} ({b.get('room_code', '')})",
        f"日期: {b['booking_date']}",
        f"时间: {b['start_time']} - {b['end_time']}",
    ]
    if b.get("is_system"):
        parts.append("类型: 系统预订")
    else:
        parts.append(f"预订人: {b.get('user_name', '')}")
        if b.get("meeting_content"):
            parts.append(f"会议内容: {b['meeting_content']}")
    return " | ".join(parts)


# MCP Server
mcp = MCPServer(
    "会议室预订系统",
    instructions="""会议室预订系统MCP服务端。每个Agent通过配置的授权码自动识别用户身份。

授权码获取: Web端登录 → 个人信息 → 生成MCP授权码
配置方式: url?auth_code=授权码 或请求头 X-Auth-Code"""
)


@mcp.tool()
async def login(auth_code: str = "", username: str = "", password: str = "") -> str:
    """登录会议室预订系统。通常无需手动调用，系统会根据 Agent 配置的授权码自动登录。

    Args:
        auth_code: MCP 授权码
        username: 用户名
        password: 密码
    """
    code = auth_code or get_auth_code()
    session = get_session(code) if code else None

    if session and session["token"] and not auth_code and not username:
        user = session["user"]
        return f"当前已登录: {user.get('name', '')} ({'管理员' if user.get('is_admin') else '普通用户'})"

    try:
        if auth_code:
            result = await do_login(auth_code=auth_code)
        elif username and password:
            result = await do_login(username=username, password=password)
        elif code:
            result = await do_login(auth_code=code)
        else:
            raise RuntimeError("请提供 auth_code 或 username+password")

        target = get_session(code) if code else session
        if target is None:
            raise RuntimeError("无法确定会话")

        target["token"] = result["token"]
        target["user"] = result["user"]
        target["auth_code"] = code

        user = result["user"]
        role = "管理员" if user.get("is_admin") else "普通用户"
        return f"登录成功！用户: {user.get('name', '')} | 角色: {role} | 部门: {user.get('department', '-')}"
    except Exception as e:
        return f"登录失败: {e}"


@mcp.tool()
async def list_rooms(keyword: str = "") -> str:
    """查询会议室列表。

    Args:
        keyword: 搜索关键词（可选）
    """
    params = {"keyword": keyword} if keyword else {}
    rooms = await api_call("GET", "/api/rooms", params=params)
    if not rooms:
        return "未找到会议室"
    lines = [f"共 {len(rooms)} 个会议室：\n"]
    for r in rooms:
        status = "启用" if r.get("is_active", True) else "停用"
        remark = f" - {r['remark']}" if r.get("remark") else ""
        lines.append(f"- {r['name']} ({r['room_code']}) [{status}]{remark}")
    return "\n".join(lines)


@mcp.tool()
async def check_availability(room_name_or_code: str = "", target_date: str = "") -> str:
    """查询会议室时段预订情况。

    Args:
        room_name_or_code: 会议室名称或编号（可选）
        target_date: 日期 YYYY-MM-DD（可选，默认今天）
    """
    if not target_date:
        target_date = date.today().isoformat()

    bookings = await api_call("GET", "/api/bookings", params={"date": target_date})
    rooms = await api_call("GET", "/api/rooms")

    if room_name_or_code:
        rooms = [r for r in rooms if room_name_or_code.lower() in r["name"].lower() or room_name_or_code.lower() in r["room_code"].lower()]

    if not rooms:
        return f"未找到会议室" + (f"（关键词: {room_name_or_code}）" if room_name_or_code else "")

    time_slots = [f"{h:02d}:00" for h in range(9, 20)]
    lines = [f"{target_date} 会议室预订情况：\n"]

    for room in rooms:
        room_bks = [b for b in bookings if b.get("room_id") == room["id"]]
        occupied = set()
        for b in room_bks:
            for slot in time_slots:
                if b["start_time"] <= slot < b["end_time"]:
                    occupied.add(slot)
        slot_strs = [f"[{s} X]" if s in occupied else f"{s} OK" for s in time_slots]
        remark = f" ({room['remark']})" if room.get("remark") else ""
        lines.append(f">> {room['name']} ({room['room_code']}){remark}")
        lines.append(f"   可用: {len(time_slots)-len(occupied)}/{len(time_slots)}")
        lines.append(f"   {' '.join(slot_strs)}\n")

    return "\n".join(lines)


@mcp.tool()
async def create_booking(room_name_or_code: str, booking_date: str, start_time: str, end_time: str, meeting_content: str = "") -> str:
    """预订会议室。

    Args:
        room_name_or_code: 会议室名称或编号
        booking_date: 日期 YYYY-MM-DD
        start_time: 开始时间 HH:MM
        end_time: 结束时间 HH:MM
        meeting_content: 会议内容（可选）
    """
    rooms = await api_call("GET", "/api/rooms")
    target = None
    for r in rooms:
        if room_name_or_code.lower() in r["name"].lower() or room_name_or_code.lower() == r["room_code"].lower():
            target = r
            break
    if not target:
        room_list = ", ".join(f"{r['name']}({r['room_code']})" for r in rooms)
        raise RuntimeError(f"未找到会议室 '{room_name_or_code}'。可选: {room_list}")

    result = await api_call("POST", "/api/bookings", json_data={
        "room_id": target["id"], "booking_date": booking_date,
        "start_time": start_time, "end_time": end_time, "meeting_content": meeting_content,
    })
    return f"预订成功！ID: {result.get('id')} | {target['name']} | {booking_date} {start_time}-{end_time}" + (f" | {meeting_content}" if meeting_content else "")


@mcp.tool()
async def cancel_booking(booking_id: int) -> str:
    """取消预订。

    Args:
        booking_id: 预订ID
    """
    await api_call("DELETE", f"/api/bookings/{booking_id}")
    return f"预订 {booking_id} 已取消"


@mcp.tool()
async def my_bookings() -> str:
    """查询我的有效预订。"""
    bookings = await api_call("GET", "/api/bookings/my")
    if not bookings:
        return "您当前没有有效预订"
    lines = [f"您有 {len(bookings)} 个有效预订：\n"]
    for b in bookings:
        lines.append(f"- {format_booking(b)}")
    return "\n".join(lines)


@mcp.tool()
async def booking_history(status: str = "", page: int = 1, page_size: int = 10) -> str:
    """查询预订历史。

    Args:
        status: 状态筛选 active/cancelled（可选）
        page: 页码
        page_size: 每页数量
    """
    params = {"page": page, "page_size": min(page_size, 50)}
    if status:
        params["status"] = status
    result = await api_call("GET", "/api/bookings/my/history", params=params)
    items = result.get("items", [])
    total = result.get("total", 0)
    if not items:
        return "没有预订记录"
    lines = [f"预订历史（第{page}页，共{total}条）：\n"]
    for b in items:
        lines.append(f"- {format_booking(b)}")
    return "\n".join(lines)


@mcp.tool()
async def get_user_info() -> str:
    """获取当前登录用户信息。"""
    user = await api_call("GET", "/api/users/me")
    role = "管理员" if user.get("is_admin") else "普通用户"
    return f"用户: {user.get('name', '')} | 账号: {user.get('username', '')} | 角色: {role} | 部门: {user.get('department', '-')} | 电话: {user.get('phone', '-')}"


@mcp.tool()
async def get_stats() -> str:
    """获取预订统计。"""
    stats = await api_call("GET", "/api/stats/overview")
    lines = [
        f"今日预订: {stats.get('today_count', 0)}",
        f"会议室数: {stats.get('total_rooms', 0)}",
        f"总预订数: {stats.get('total_bookings', 0)}",
    ]
    recent = stats.get("recent_bookings", [])
    if recent:
        lines.append("\n最近预订:")
        for b in recent[:5]:
            lines.append(f"  {b.get('room_name', '')} | {b.get('booking_date', '')} {b.get('start_time', '')}-{b.get('end_time', '')} | {b.get('user_name', '')}")
    return "\n".join(lines)


def create_app(streamable_http_path: str = "/mcp", host: str = "0.0.0.0"):
    """创建应用：在 MCP 的 Starlette app 上添加 ASGI 中间件，每个请求提取授权码写入 contextvars"""
    mcp_app = mcp.streamable_http_app(streamable_http_path=streamable_http_path, host=host)

    class AuthMiddleware:
        """ASGI 中间件：从 URL query / 请求头提取授权码并注入 contextvars"""

        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                code = _extract_auth_code(scope)
                token = current_auth_code.set(code)
                try:
                    await self.app(scope, receive, send)
                finally:
                    current_auth_code.reset(token)
            else:
                await self.app(scope, receive, send)

    mcp_app.add_middleware(AuthMiddleware)
    return mcp_app


def _extract_auth_code(scope) -> str:
    """从请求 scope 提取授权码"""
    # 1. URL query 参数 auth_code
    query = parse_qs(scope.get("query_string", b"").decode("latin-1"))
    if query.get("auth_code") and query["auth_code"][0]:
        return query["auth_code"][0]
    # 2. 请求头 X-Auth-Code
    headers = {k.lower(): v for k, v in scope.get("headers", [])}
    if headers.get(b"x-auth-code"):
        return headers[b"x-auth-code"].decode("utf-8", errors="replace")
    # 3. 请求头 Authorization: Bearer xxx（兼容已有配置）
    auth = headers.get(b"authorization", b"")
    if auth.startswith(b"Bearer "):
        return auth[len(b"Bearer "):].decode("utf-8", errors="replace")
    return ""


def main():
    parser = argparse.ArgumentParser(description="会议室预订系统 MCP 服务端")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="streamable-http")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    logger.info(f"MCP 服务端启动 - 多用户模式")
    logger.info(f"API 地址: {API_BASE}")

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        logger.info(f"监听地址: http://{args.host}:{args.port}/mcp")
        logger.info("授权码传递: URL参数 ?auth_code=xxx 或 请求头 X-Auth-Code")
        app = create_app(host=args.host)
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
