# 会议室预订系统 MCP 服务端

## 简介

基于 MCP (Model Context Protocol) 的服务端，允许大模型 Agent 通过自然语言与会议室预订系统交互。

采用 **Streamable HTTP** 传输协议，Agent 通过 HTTP 连接到 MCP 服务端。

## 功能

| 工具 | 说明 |
|------|------|
| `login` | 登录认证（必须先调用，支持授权码或用户名密码） |
| `logout` | 退出登录 |
| `list_rooms` | 查询会议室列表 |
| `check_availability` | 查询会议室时段预订情况 |
| `create_booking` | 预订会议室 |
| `cancel_booking` | 取消预订 |
| `my_bookings` | 查询我的有效预订 |
| `booking_history` | 查询预订历史 |
| `get_user_info` | 获取当前用户信息 |
| `get_stats` | 获取统计数据概览 |

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 启动服务

```bash
# 启动 Flask 后端 (端口 5000)
python app.py

# 启动 MCP 服务端 (端口 8080)
python mcp_server.py

# 自定义端口
python mcp_server.py --port 9090
```

启动后 MCP 端点地址: `http://0.0.0.0:8080/mcp`

## 获取 MCP 授权码

1. 登录会议室预订系统 Web 端
2. 进入「个人信息」页面
3. 点击「生成MCP授权码」按钮
4. 复制生成的授权码

> 授权码是您在 MCP 客户端中的身份凭证，请妥善保管。
> 如需撤销授权，可点击「删除MCP授权码」。

## 配置 Agent 客户端

每个 Agent 在**自己的配置**中携带授权码，MCP 服务端会自动识别该 Agent 对应的用户身份，无需手动登录。
不同 Agent 使用不同授权码时，各自以不同用户身份操作，互不影响，防止越权。

### Claude Desktop

编辑配置文件:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "meeting-room": {
      "url": "http://127.0.0.1:8080/mcp?auth_code=你的授权码"
    }
  }
}
```

### OpenCode (`opencode.json` 或 `~/.config/opencode/opencode.json`)

不同 Agent 配置不同的授权码：

```json
{
  "mcp": {
    "会议室-管理员": {
      "type": "remote",
      "url": "http://127.0.0.1:8080/mcp?auth_code=管理员的授权码"
    },
    "会议室-张三": {
      "type": "remote",
      "url": "http://127.0.0.1:8080/mcp?auth_code=张三的授权码"
    }
  }
}
```

### 远程连接

```json
{
  "mcpServers": {
    "meeting-room": {
      "url": "http://<server-ip>:8080/mcp?auth_code=你的授权码"
    }
  }
}
```

确保防火墙开放 8080 端口。

### 备选方式：通过请求头传递授权码

如果客户端不支持 URL 查询参数，可通过请求头 `X-Auth-Code` 传递：

```json
{
  "mcpServers": {
    "meeting-room": {
      "url": "http://127.0.0.1:8080/mcp",
      "headers": { "X-Auth-Code": "你的授权码" }
    }
  }
}
```

## 使用流程

1. 每个用户在 Web 端「个人信息」页面生成自己的 MCP 授权码
2. 将各自的授权码填入各自 Agent 的 MCP 配置（URL 参数 `?auth_code=xxx`）
3. 启动 Agent，MCP 服务端自动识别授权码并登录对应用户
4. 直接使用自然语言操作会议室预订系统，无需手动登录

## 自然语言示例

```
用户: 查询今天有哪些会议室可用
用户: 帮我预订 A栋301 会议室，明天下午2点到3点，开项目周会
用户: 查看我当前的预订
用户: 取消预订 123
```

## 多用户隔离机制

- 每个 Agent 的授权码写入各自 MCP 配置
- MCP 服务端按请求中的授权码自动认证，并按授权码缓存独立登录状态
- Agent A 的操作始终以授权码 A 对应的用户身份执行，与 Agent B 互不干扰
- 管理员授权码对应管理员身份，可执行管理操作；普通用户授权码仅具备本人权限，防止越权

## 授权码安全

- 每个用户有独立的授权码
- 授权码绑定用户身份和权限
- 可随时在 Web 端生成新的授权码（旧码自动失效）
- 可随时删除授权码以撤销 MCP 访问权限

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MEETING_ROOM_API_URL` | Flask 后端地址 | `http://127.0.0.1:5000` |
