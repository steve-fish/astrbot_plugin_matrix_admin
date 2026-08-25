"""
Matrix Admin Plugin - Bot Commands
Bot 资料管理相关命令
"""

import time

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
from astrbot.core.star.filter.command import GreedyStr

from .base import AdminCommandMixin


class BotCommandsMixin(AdminCommandMixin):
    """Bot 资料管理命令：set name, set avatar, set status"""

    # 状态映射
    STATUS_MAP = {
        "online": ("online", "在线"),
        "在线": ("online", "在线"),
        "away": ("unavailable", "离开"),
        "离开": ("unavailable", "离开"),
        "unavailable": ("unavailable", "离开"),
        "busy": ("unavailable", "忙碌"),
        "忙碌": ("unavailable", "忙碌"),
        "offline": ("offline", "离线"),
        "离线": ("offline", "离线"),
    }

    async def cmd_setname(self, event: AstrMessageEvent, name: GreedyStr):
        """修改 Bot 的显示名称

        用法：/admin set name <新名称>

        示例：
            /admin set name MyBot
            /admin set name 我的机器人
        """
        client = self._get_matrix_client(event)
        if not client:
            yield event.plain_result("此命令仅在 Matrix 平台可用")
            return

        if not name or not name.strip():
            yield event.plain_result("请提供有效的名称")
            return

        try:
            await client.set_display_name(name.strip())
            yield event.plain_result(f"已将 Bot 名称修改为：**{name.strip()}**")
        except Exception as e:
            logger.error(f"修改 Bot 名称失败：{e}")
            yield event.plain_result(f"修改 Bot 名称失败：{e}")

    async def cmd_setavatar(self, event: AstrMessageEvent, mxc_url: str = ""):
        """修改 Bot 的头像（支持 mxc:// URL 或引用图片）

        用法：/admin set avatar [mxc:// URL]

        示例：
            /admin set avatar mxc://matrix.org/AbCdEf
            或引用一条包含图片的消息后发送 /admin set avatar
        """
        client = self._get_matrix_client(event)
        if not client:
            yield event.plain_result("此命令仅在 Matrix 平台可用")
            return

        # 直接提供 mxc:// URL 时跳过引用解析
        direct_mxc = str(mxc_url or "").strip()
        if direct_mxc:
            if not direct_mxc.startswith("mxc://"):
                yield event.plain_result("头像 URL 必须以 mxc:// 开头")
                return
            try:
                await client.set_avatar_url(direct_mxc)
                yield event.plain_result(
                    f"已成功修改 Bot 头像\n头像 URL: `{direct_mxc}`"
                )
            except Exception as e:
                logger.error(f"修改 Bot 头像失败：{e}")
                yield event.plain_result(f"修改 Bot 头像失败：{e}")
            return

        # 获取原始消息中的引用信息
        room_id = self._resolve_event_room_id(event)
        if not room_id:
            yield event.plain_result("无法获取房间 ID")
            return

        image_mxc_url, error = await self._resolve_reply_image_mxc(
            client, event, room_id
        )
        if error or not image_mxc_url:
            yield event.plain_result(error or "无法获取图片 URL")
            return

        try:
            await client.set_avatar_url(image_mxc_url)
            yield event.plain_result(
                f"已成功修改 Bot 头像\n头像 URL: `{image_mxc_url}`"
            )
        except Exception as e:
            logger.error(f"修改 Bot 头像失败：{e}")
            yield event.plain_result(f"修改 Bot 头像失败：{e}")

    async def cmd_setstatus(
        self, event: AstrMessageEvent, status: str = "", message: str = ""
    ):
        """修改 Bot 的在线状态

        用法：/admin set status <状态> [状态消息]

        状态：
            online / 在线 - 在线
            away / 离开 / busy / 忙碌 - 离开/忙碌
            offline / 离线 - 离线

        示例：
            /admin set status online
            /admin set status away 暂时离开
            /admin set status 忙碌 正在处理任务
        """
        client = self._get_matrix_client(event)
        if not client:
            yield event.plain_result("此命令仅在 Matrix 平台可用")
            return

        if not status:
            # 显示帮助信息
            yield event.plain_result(
                "**修改 Bot 状态**\n\n"
                "用法：/admin set status <状态> [状态消息]\n\n"
                "可用状态:\n"
                "  - `online` / `在线` - 在线\n"
                "  - `away` / `离开` / `busy` / `忙碌` - 离开\n"
                "  - `offline` / `离线` - 离线\n\n"
                "示例:\n"
                "  /admin set status online\n"
                "  /admin set status away 暂时离开"
            )
            return

        # 解析状态
        status_key = status.lower().strip()
        if status_key not in self.STATUS_MAP:
            valid_statuses = ", ".join(
                [
                    f"`{k}`"
                    for k in ["online", "away", "offline", "在线", "离开", "离线"]
                ]
            )
            yield event.plain_result(
                f"无效的状态：`{status}`\n\n可用状态：{valid_statuses}"
            )
            return

        matrix_status, status_display = self.STATUS_MAP[status_key]
        now_ms = int(time.time() * 1000)
        currently_active = matrix_status == "online"

        try:
            await client.set_presence(
                matrix_status,
                message.strip() if message else None,
                last_active_ts=now_ms,
                currently_active=currently_active,
            )
            result_msg = f"已将 Bot 状态设置为：**{status_display}**"
            if message:
                result_msg += f"\n状态消息：{message.strip()}"
            yield event.plain_result(result_msg)
        except Exception as e:
            logger.error(f"修改 Bot 状态失败：{e}")
            yield event.plain_result(f"修改 Bot 状态失败：{e}")

    async def cmd_statusmsg(self, event: AstrMessageEvent, message: str = ""):
        """设置或清除 Bot 的状态消息（不改变在线状态）

        用法：/admin set statusmsg [消息]

        示例：
            /admin set statusmsg 正在处理任务
            /admin set statusmsg 休息中，稍后回复
            /admin set statusmsg  (留空则清除状态消息)
        """
        client = self._get_matrix_client(event)
        if not client:
            yield event.plain_result("此命令仅在 Matrix 平台可用")
            return

        try:
            # 使用 online 状态，只更新状态消息
            status_msg = message.strip() if message else None
            await client.set_presence(
                "online",
                status_msg,
                last_active_ts=int(time.time() * 1000),
                currently_active=True,
            )

            if status_msg:
                yield event.plain_result(f"已设置状态消息：**{status_msg}**")
            else:
                yield event.plain_result("已清除状态消息")
        except Exception as e:
            logger.error(f"设置状态消息失败：{e}")
            yield event.plain_result(f"设置状态消息失败：{e}")

    async def cmd_purge_messages(
        self, event: AstrMessageEvent, target: str = "", room_id: str = ""
    ):
        """清理自己或指定用户在房间内发送的全部历史消息（直到对话开头）

        用法：/admin purge self [@用户ID|room_id] [room_id]

        示例：
            /admin purge self
            /admin purge self @user:example.org
            /admin purge self @user:example.org !roomid:example.org
        """
        client = self._get_matrix_client(event)
        if not client:
            yield event.plain_result("此命令仅在 Matrix 平台可用")
            return

        target_text = str(target or "").strip()
        target_room_id = str(room_id or "").strip()
        # 第一个参数直接给房间 ID 时视为目标房间
        if target_text.startswith("!"):
            target_room_id = target_room_id or target_text
            target_text = ""

        target_room_id = target_room_id or str(event.get_session_id() or "").strip()
        if not target_room_id:
            yield event.plain_result("无法获取房间 ID")
            return

        if target_text:
            purge_user_id = self._parse_user_id(target_text, event, target_room_id)
            if not purge_user_id:
                yield event.plain_result(f"无效的用户 ID：{target_text}")
                return
        else:
            purge_user_id = getattr(client, "user_id", None)
            if not purge_user_id:
                try:
                    whoami = await client.whoami()
                    purge_user_id = whoami.get("user_id")
                except Exception as e:
                    yield event.plain_result(f"获取 Bot 用户 ID 失败：{e}")
                    return

        scanned = 0
        redacted = 0
        failed = 0
        from_token = None

        # 从最新消息向前分页，直到房间历史开头
        while True:
            try:
                resp = await client.room_messages(
                    room_id=target_room_id,
                    from_token=from_token,
                    direction="b",
                    limit=100,
                )
            except Exception as e:
                yield event.plain_result(f"拉取房间消息失败：{e}")
                return

            chunk = resp.get("chunk", []) or []
            if not chunk:
                break

            for msg in chunk:
                scanned += 1
                if msg.get("sender") != purge_user_id:
                    continue
                event_id = msg.get("event_id")
                if not event_id:
                    continue
                try:
                    await client.redact_event(
                        target_room_id, event_id, reason="admin purge messages"
                    )
                    redacted += 1
                except Exception:
                    failed += 1

            from_token = resp.get("end")
            if not from_token:
                break

        yield event.plain_result(
            f"清理完成：扫描 {scanned} 条，撤回 {redacted} 条，失败 {failed} 条"
        )
