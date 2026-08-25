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

- 用户管理：`kick`, `ban`, `unban`, `invite`, `promote`, `demote`, `power`
- 信息查询：`admins`, `whois`, `search`
- 忽略列表：`ignore`, `unignore`, `ignorelist`
- 创建：`create room`, `create space`
- 房间管理：`dm`, `alias set`, `alias del`, `alias get`, `publicrooms`, `forget`, `upgrade`, `hierarchy`, `knock`, `room refresh`
- Space：`space create`, `space link`, `space unlink`, `space children`
- Bot 管理：`set name`, `set avatar`, `set status`, `set statusmsg`, `purge self`
- 房间资料：`room name set`, `room topic set`, `room set name`, `room set avatar`
- 验证：`verify sas`, `verify qr`
- 适配器运维：`matrix status`, `reconnect`, `resendpending`

## 使用示例

```text
/admin kick @user:example.org 违规
/admin ban @user:example.org spam
/admin unban @user:example.org
/admin invite @user:example.org
/admin promote @user:example.org mod
/admin demote @user:example.org
/admin power @user:example.org 50
/admin admins
/admin whois @user:example.org
/admin search alice 10
/admin ignore @user:example.org
/admin ignorelist
/admin create room "My Room" yes
/admin create space "My Space" yes
/admin dm @user:example.org
/admin alias set #myroom:example.org !roomid:example.org
/admin alias get #myroom:example.org
/admin publicrooms example.org 20
/admin upgrade 10 !roomid:example.org
/admin hierarchy !roomid:example.org 20
/admin knock #room:example.org hi
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
