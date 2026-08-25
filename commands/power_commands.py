"""
Matrix Admin Plugin - Power Commands
权限管理相关命令
"""

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from .base import AdminCommandMixin


class PowerCommandsMixin(AdminCommandMixin):
    """权限管理命令：promote, demote, power, admins"""

    async def _require_client_and_room(
        self, event: AstrMessageEvent, room_id: str = ""
    ) -> tuple:
        """统一获取 client 和 target_room_id"""
        client = self._get_matrix_client(event)
        ok, msg = self._validate_client(client)
        if not ok:
            return None, None, msg
        target_room_id = self._resolve_target_room_id(event, room_id)
        ok, msg = self._validate_room_id(target_room_id)
        if not ok:
            return None, None, msg
        return client, target_room_id, None

    async def cmd_promote(
        self,
        event: AstrMessageEvent,
        user: str,
        level: str = "mod",
        room_id: str = "",
    ):
        """提升用户权限

        用法：/admin power promote <用户 ID> [级别] [room_id]

        级别：
            mod - 管理员 (50)
            admin - 房主 (100)

        示例：
            /admin power promote @user:example.com
            /admin power promote @user:example.com admin
        """
        client, target_room_id, error = await self._require_client_and_room(
            event, room_id
        )
        if error:
            yield event.plain_result(error)
            return

        level_text = str(level or "").strip().lower()
        if not target_room_id and level_text.startswith("!") and ":" in level_text:
            target_room_id = level_text
            level_text = "mod"

        user_id = self._parse_user_id(user, event, target_room_id)
        ok, _ = self._validate_user_id(user_id)
        if not ok:
            yield event.plain_result("无效的用户 ID")
            return

        level_map = {
            "mod": 50,
            "moderator": 50,
            "admin": 100,
            "owner": 100,
        }

        power_level = level_map.get(level_text, 50)
        level_name = "管理员" if power_level == 50 else "房主"

        try:
            await client.set_user_power_level(target_room_id, user_id, power_level)
            yield event.plain_result(
                f"已将 {user_id} 提升为{level_name} (权限等级：{power_level})\n"
                f"房间：{target_room_id}"
            )
        except Exception as e:
            logger.error(f"提升权限失败：{e}")
            yield event.plain_result(self._format_error("提升权限失败", str(e)))

    async def cmd_demote(self, event: AstrMessageEvent, user: str, room_id: str = ""):
        """降低用户权限为普通成员

        用法：/admin power demote <用户 ID> [room_id]

        示例：
            /admin power demote @user:example.com
            /admin power demote @user:example.com !roomid:example.com
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
            await client.set_user_power_level(target_room_id, user_id, 0)
            yield event.plain_result(
                f"已将 {user_id} 降级为普通成员\n房间：{target_room_id}"
            )
        except Exception as e:
            logger.error(f"降级失败：{e}")
            yield event.plain_result(self._format_error("降级失败", str(e)))

    async def cmd_power(
        self,
        event: AstrMessageEvent,
        user: str,
        level: int,
        room_id: str = "",
    ):
        """设置用户权限等级

        用法：/admin power power <用户 ID> <等级> [room_id]

        等级说明：
            0 - 普通成员
            50 - 管理员
            100 - 房主

        示例：
            /admin power power @user:example.com 50
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
            await client.set_user_power_level(target_room_id, user_id, level)
            yield event.plain_result(
                f"已将 {user_id} 的权限等级设置为 {level}\n房间：{target_room_id}"
            )
        except Exception as e:
            logger.error(f"设置权限失败：{e}")
            yield event.plain_result(self._format_error("设置权限失败", str(e)))

    async def cmd_admins(self, event: AstrMessageEvent, room_id: str = ""):
        """列出房间管理员

        用法：/admin power admins [room_id]
        """
        client, target_room_id, error = await self._require_client_and_room(
            event, room_id
        )
        if error:
            yield event.plain_result(error)
            return

        try:
            power_levels = await client.get_power_levels(target_room_id)
            users = power_levels.get("users", {})

            admins = []
            mods = []

            for uid, level in users.items():
                if level >= 100:
                    admins.append((uid, level))
                elif level >= 50:
                    mods.append((uid, level))

            lines = [f"**房间权限列表** ({target_room_id})\n"]

            if admins:
                lines.append("**房主 (100+):**")
                for uid, level in admins:
                    lines.append(f"  - {uid} ({level})")
                lines.append("")

            if mods:
                lines.append("**管理员 (50+):**")
                for uid, level in mods:
                    lines.append(f"  - {uid} ({level})")

            if not admins and not mods:
                lines.append("没有设置特殊权限的用户")

            yield event.plain_result("\n".join(lines))

        except Exception as e:
            logger.error(f"获取管理员列表失败：{e}")
            yield event.plain_result(self._format_error("获取管理员列表失败", str(e)))
