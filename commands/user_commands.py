"""
Matrix Admin Plugin - User Commands
踢出/封禁/邀请用户相关命令
"""

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from .base import AdminCommandMixin


class UserCommandsMixin(AdminCommandMixin):
    """用户管理命令：kick, ban, unban, invite, members, banlist"""

    async def _require_client_and_room(
        self, event: AstrMessageEvent, room_id: str = ""
    ) -> tuple:
        """统一获取 client 和 target_room_id，失败时返回 (None, None, error_msg)"""
        client = self._get_matrix_client(event)
        ok, msg = self._validate_client(client)
        if not ok:
            return None, None, msg
        target_room_id = self._resolve_target_room_id(event, room_id)
        ok, msg = self._validate_room_id(target_room_id)
        if not ok:
            return None, None, msg
        return client, target_room_id, None

    async def cmd_kick(
        self,
        event: AstrMessageEvent,
        user: str,
        reason: str = "",
        room_id: str = "",
    ):
        """踢出用户

        用法：/admin user kick <用户 ID> [原因] [room_id]

        示例：
            /admin user kick @baduser:example.com
            /admin user kick @baduser:example.com 违规发言
            /admin user kick @baduser:example.com !roomid:example.com
        """
        client, target_room_id, error = await self._require_client_and_room(
            event, room_id
        )
        if error:
            yield event.plain_result(error)
            return

        reason_text = str(reason or "").strip()
        if not target_room_id and reason_text.startswith("!") and ":" in reason_text:
            target_room_id = reason_text
            reason_text = ""

        user_id = self._parse_user_id(user, event, target_room_id)
        ok, _ = self._validate_user_id(user_id)
        if not ok:
            yield event.plain_result("无效的用户 ID")
            return

        try:
            await client.kick_user(target_room_id, user_id, reason_text or None)
            msg = f"已将 {user_id} 踢出房间"
            if reason_text:
                msg += f"\n原因：{reason_text}"
            msg += f"\n房间：{target_room_id}"
            yield event.plain_result(msg)
        except Exception as e:
            logger.error(f"踢出用户失败：{e}")
            yield event.plain_result(self._format_error("踢出用户失败", str(e)))

    async def cmd_ban(
        self,
        event: AstrMessageEvent,
        user: str,
        reason: str = "",
        room_id: str = "",
    ):
        """封禁用户

        用法：/admin user ban <用户 ID> [原因] [room_id]

        示例：
            /admin user ban @spammer:example.com
            /admin user ban @spammer:example.com 垃圾广告
            /admin user ban @spammer:example.com !roomid:example.com
        """
        client, target_room_id, error = await self._require_client_and_room(
            event, room_id
        )
        if error:
            yield event.plain_result(error)
            return

        reason_text = str(reason or "").strip()
        if not target_room_id and reason_text.startswith("!") and ":" in reason_text:
            target_room_id = reason_text
            reason_text = ""

        user_id = self._parse_user_id(user, event, target_room_id)
        ok, _ = self._validate_user_id(user_id)
        if not ok:
            yield event.plain_result("无效的用户 ID")
            return

        try:
            await client.ban_user(target_room_id, user_id, reason_text or None)
            msg = f"已封禁 {user_id}"
            if reason_text:
                msg += f"\n原因：{reason_text}"
            msg += f"\n房间：{target_room_id}"
            yield event.plain_result(msg)
        except Exception as e:
            logger.error(f"封禁用户失败：{e}")
            yield event.plain_result(self._format_error("封禁用户失败", str(e)))

    async def cmd_unban(self, event: AstrMessageEvent, user: str, room_id: str = ""):
        """解除封禁

        用法：/admin user unban <用户 ID> [room_id]

        示例：
            /admin user unban @user:example.com
            /admin user unban @user:example.com !roomid:example.com
        """
        client, target_room_id, error = await self._require_client_and_room(
            event, room_id
        )
        if error:
            yield event.plain_result(error)
            return

        user_id = self._parse_user_id(user, event, target_room_id)
        ok, _ = self._validate_user_id(user_id)
        if not ok:
            yield event.plain_result("无效的用户 ID")
            return

        try:
            await client.unban_user(target_room_id, user_id)
            yield event.plain_result(f"已解除 {user_id} 的封禁\n房间：{target_room_id}")
        except Exception as e:
            logger.error(f"解除封禁失败：{e}")
            yield event.plain_result(self._format_error("解除封禁失败", str(e)))

    async def cmd_invite(self, event: AstrMessageEvent, user: str, room_id: str = ""):
        """邀请用户加入房间

        用法：/admin user invite <用户 ID> [room_id]

        示例：
            /admin user invite @friend:example.com
            /admin user invite @friend:example.com !roomid:example.com
        """
        client, target_room_id, error = await self._require_client_and_room(
            event, room_id
        )
        if error:
            yield event.plain_result(error)
            return

        user_id = self._parse_user_id(user, event, target_room_id)
        ok, _ = self._validate_user_id(user_id)
        if not ok:
            yield event.plain_result("无效的用户 ID")
            return

        try:
            await client.invite_user(target_room_id, user_id)
            yield event.plain_result(
                f"已邀请 {user_id} 加入房间\n房间：{target_room_id}"
            )
        except Exception as e:
            logger.error(f"邀请用户失败：{e}")
            yield event.plain_result(self._format_error("邀请用户失败", str(e)))
