# AstrBot Matrix Admin Plugin

Matrix 管理插件，提供用户管理、权限控制、封禁踢出、设备验证与适配器运维命令。

## 依赖

- `astrbot_plugin_matrix_adapter`

## 配置

### 推荐：多适配器多房间通知（temple list）

```json
{
  "matrix_admin_verify_temple_list": [
    {
      "adapter_name": "matrix_main",
      "rooms": ["!ops:example.org", "!security:example.org"]
    },
    {
      "adapter_name": "matrix_backup",
      "rooms": ["!backup-ops:example.org"]
    }
  ],
  "matrix_admin_verify_room_id": "!fallback:example.org"
}
```

- `matrix_admin_verify_temple_list`：主配置。每项由 `adapter_name + rooms[]` 构成。
- `matrix_admin_verify_room_id`：旧配置兼容兜底；当 `temple_list` 未命中当前 adapter 时仍可通知此单房间。
- 代码兼容读取 `matrix_admin_verify_template_list`（仅兼容，不作为主字段）。

## 命令概览

所有命令以 `/admin` 作为命令组前缀：

- 用户管理 (user)：`kick`, `ban`, `unban`, `invite`, `whois`, `search`
- 权限管理 (power)：`promote`, `demote`, `power`, `admins`
- 房间管理 (room)：`create`, `list`, `info`, `banlist`, `name set`, `topic set`, `set name`, `set avatar`, `dm`, `forget`, `knock`, `upgrade`, `refresh`
- Space (space)：`create`, `link`, `unlink`, `children`, `hierarchy`
- 别名 (alias)：`set`, `del`, `get`
- Bot 资料 (set)：`name`, `avatar`, `status`, `statusmsg`
- 消息清理 (purge)：`self`
- 屏蔽 (ignore)：`add`, `del`, `list`
- 验证 (verify)：`qr`, `sas`
- 适配器运维 (matrix)：`status`, `reconnect`, `resendpending`
- 其他：`publicrooms`, `help`

## 使用示例

```text
/admin user kick @user:example.org 违规
/admin user ban @user:example.org spam
/admin user unban @user:example.org
/admin user invite @user:example.org
/admin user whois @user:example.org
/admin user search alice 10
/admin power promote @user:example.org mod
/admin power demote @user:example.org
/admin power power @user:example.org 50
/admin power admins
/admin ignore add @user:example.org
/admin ignore list
/admin room create "My Room" yes
/admin room list
/admin room info !roomid:example.org
/admin alias set #myroom:example.org !roomid:example.org
/admin alias get #myroom:example.org
/admin publicrooms example.org 20
/admin room upgrade 10 !roomid:example.org
/admin space hierarchy !roomid:example.org 20
/admin room knock #room:example.org hi
/admin set name AstrBot
/admin set avatar mxc://matrix.org/AbCdEf
/admin verify sas DEVICEID123
/admin verify qr @alice:matrix.org DEVICEID123 /tmp/element-verify-qr.png
/admin matrix status
/admin matrix reconnect
/admin matrix resendpending matrix-main 20
/admin purge self
/admin purge self @user:example.org
/admin room name set 新房间名
/admin room topic set 新主题
/admin room set name 房间内的机器人名
/admin room set avatar mxc://matrix.org/AbCdEf
/admin room refresh
/admin room refresh all
```

## 运行态命令

### `/admin verify qr`

扫描同账号设备验证二维码，并发送 `m.reciprocate.v1`。若在网页中使用，可直接在消息里附带二维码图片，或引用一张历史二维码图片。

**用法**：
```text
/admin verify qr <user_id> <device_id> <二维码图片路径或 base64 载荷> [matrix_platform_id|webhook_uuid]
```

### `/admin matrix status`

查看 Matrix 适配器运行状态、同步统计与最近错误。

**用法**：
```text
/admin matrix status [matrix_platform_id|webhook_uuid]
```

### `/admin matrix reconnect`

主动中断当前 `/sync` 长轮询并立即重连。

**用法**：
```text
/admin matrix reconnect [matrix_platform_id|webhook_uuid]
```

### `/admin matrix resendpending`

重试最近失败或挂起的出站消息记录。

**用法**：
```text
/admin matrix resendpending [matrix_platform_id|webhook_uuid] [limit]
```

## 说明

- 命令仅在 Matrix 平台生效。
- 若命令来自与某个 Matrix 适配器共用统一 Webhook 的会话，可自动匹配该适配器进行扫码/状态操作。
- `matrix_platform_id` 参数也可直接填写对应适配器的 `webhook_uuid`。
- 具体权限要求依赖房间的 power level 配置。
