"""
Matrix Admin Plugin - 提供 Matrix 房间管理命令

此插件依赖于 astrbot_plugin_matrix_adapter 提供的 Matrix 客户端。
提供用户管理、权限控制、房间管理及适配器运维命令。
"""

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter.command import GreedyStr
from astrbot.core.star.filter.permission import PermissionType

from .commands import (
    BotCommandsMixin,
    IgnoreCommandsMixin,
    PowerCommandsMixin,
    QueryCommandsMixin,
    RoomCommandsMixin,
    RuntimeCommandsMixin,
    UserCommandsMixin,
)
from .tool import (
    apply_admin_room_config,
    normalize_verify_room_templates,
    split_reason_and_room_id,
)


@register(
    "astrbot_plugin_matrix_admin",
    "stevessr",
    "Matrix 管理插件，提供房间管理、设备验证与适配器运维命令",
    "0.3.0",
)
class Matrix_Admin_Plugin(
    Star,
    UserCommandsMixin,
    PowerCommandsMixin,
    QueryCommandsMixin,
    IgnoreCommandsMixin,
    RoomCommandsMixin,
    BotCommandsMixin,
    RuntimeCommandsMixin,
):
    def __init__(self, context: Context, config: dict | None = None) -> None:
        super().__init__(context, config)
        self.context = context
        self.config = config or {}
        self.verify_room_id = str(
            self.config.get("matrix_admin_verify_room_id", "") or ""
        ).strip()
        self.verify_room_templates = normalize_verify_room_templates(
            self.config.get("matrix_admin_verify_temple_list")
            or self.config.get("matrix_admin_verify_template_list")
        )

    def _maybe_apply_admin_room_config(self):
        apply_admin_room_config(self)

    @filter.on_astrbot_loaded()
    async def on_astrbot_loaded(self):
        self._maybe_apply_admin_room_config()

    @filter.on_platform_loaded()
    async def on_platform_loaded(self):
        self._maybe_apply_admin_room_config()

    # ========== Command Bindings ==========
    # 装饰器必须定义在 main.py 中，否则 handler 的 __module__ 不匹配

    @filter.command_group("admin")
    def admin_group(self):
        """Matrix 房间管理命令"""

    @admin_group.command("kick")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_kick(
        self,
        event: AstrMessageEvent,
        user: str,
        reason_or_room: GreedyStr = "",
    ):
        """踢出用户"""
        reason, room_id = split_reason_and_room_id(reason_or_room)
        async for result in self.cmd_kick(event, user, reason, room_id):
            yield result

    @admin_group.command("ban")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_ban(
        self,
        event: AstrMessageEvent,
        user: str,
        reason_or_room: GreedyStr = "",
    ):
        """封禁用户"""
        reason, room_id = split_reason_and_room_id(reason_or_room)
        async for result in self.cmd_ban(event, user, reason, room_id):
            yield result

    @admin_group.command("unban")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_unban(self, event: AstrMessageEvent, user: str, room_id: str = ""):
        """解除封禁"""
        async for result in self.cmd_unban(event, user, room_id):
            yield result

    @admin_group.command("invite")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_invite(self, event: AstrMessageEvent, user: str, room_id: str = ""):
        """邀请用户加入房间"""
        async for result in self.cmd_invite(event, user, room_id):
            yield result

    @admin_group.command("promote")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_promote(
        self,
        event: AstrMessageEvent,
        user: str,
        level: str = "mod",
        room_id: str = "",
    ):
        """提升用户权限"""
        async for result in self.cmd_promote(event, user, level, room_id):
            yield result

    @admin_group.command("demote")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_demote(self, event: AstrMessageEvent, user: str, room_id: str = ""):
        """降低用户权限为普通成员"""
        async for result in self.cmd_demote(event, user, room_id):
            yield result

    @admin_group.command("power")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_power(
        self, event: AstrMessageEvent, user: str, level: int, room_id: str = ""
    ):
        """设置用户权限等级"""
        async for result in self.cmd_power(event, user, level, room_id):
            yield result

    @admin_group.command("admins")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_list_admins(self, event: AstrMessageEvent, room_id: str = ""):
        """列出房间管理员"""
        async for result in self.cmd_admins(event, room_id):
            yield result

    @admin_group.command("whois")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_whois(self, event: AstrMessageEvent, user: str):
        """查询用户信息"""
        async for result in self.cmd_whois(event, user):
            yield result

    @admin_group.command("search")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_search(
        self, event: AstrMessageEvent, keyword: str, limit: int = 10
    ):
        """搜索用户"""
        async for result in self.cmd_search(event, keyword, limit):
            yield result

    @admin_group.command("ignore")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_ignore(self, event: AstrMessageEvent, user: str):
        """屏蔽用户"""
        async for result in self.cmd_ignore(event, user):
            yield result

    @admin_group.command("unignore")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_unignore(self, event: AstrMessageEvent, user: str):
        """取消屏蔽用户"""
        async for result in self.cmd_unignore(event, user):
            yield result

    @admin_group.command("ignorelist")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_ignorelist(self, event: AstrMessageEvent):
        """查看屏蔽列表"""
        async for result in self.cmd_ignorelist(event):
            yield result

    @admin_group.command("createroom")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_createroom(
        self, event: AstrMessageEvent, name: str, is_public: str = "no"
    ):
        """创建新房间"""
        async for result in self.cmd_createroom(event, name, is_public):
            yield result

    @admin_group.command("dm")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_dm(self, event: AstrMessageEvent, user: str):
        """创建与用户的私聊房间"""
        async for result in self.cmd_dm(event, user):
            yield result

    @admin_group.command("aliasset")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_alias_set(
        self, event: AstrMessageEvent, alias: str, room_id: str = ""
    ):
        """设置房间别名"""
        async for result in self.cmd_alias_set(event, alias, room_id):
            yield result

    @admin_group.command("aliasdel")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_alias_del(self, event: AstrMessageEvent, alias: str):
        """删除房间别名"""
        async for result in self.cmd_alias_del(event, alias):
            yield result

    @admin_group.command("aliasget")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_alias_get(self, event: AstrMessageEvent, alias: str):
        """解析房间别名"""
        async for result in self.cmd_alias_get(event, alias):
            yield result

    @admin_group.command("publicrooms")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_publicrooms(
        self, event: AstrMessageEvent, server: str = "", limit: int = 20
    ):
        """列出公共房间"""
        async for result in self.cmd_publicrooms(event, server, limit):
            yield result

    @admin_group.command("forget")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_forget(self, event: AstrMessageEvent, room_id: str = ""):
        """忘记房间"""
        async for result in self.cmd_forget(event, room_id):
            yield result

    @admin_group.command("upgrade")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_upgrade(
        self, event: AstrMessageEvent, new_version: str, room_id: str = ""
    ):
        """升级房间版本"""
        async for result in self.cmd_upgrade(event, new_version, room_id):
            yield result

    @admin_group.command("hierarchy")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_hierarchy(
        self, event: AstrMessageEvent, room_id: str = "", limit: int = 20
    ):
        """获取房间层级"""
        async for result in self.cmd_hierarchy(event, room_id, limit):
            yield result

    @admin_group.command("spacecreate")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_spacecreate(
        self,
        event: AstrMessageEvent,
        name: str,
        is_public: str = "no",
        topic: str = "",
    ):
        """创建 Space"""
        async for result in self.cmd_space_create(event, name, is_public, topic):
            yield result

    @admin_group.command("spacelink")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_spacelink(
        self,
        event: AstrMessageEvent,
        space_id: str,
        child_room_id: str,
        suggested: str = "yes",
    ):
        """挂载 Space 子房间"""
        async for result in self.cmd_space_link(
            event,
            space_id,
            child_room_id,
            suggested,
        ):
            yield result

    @admin_group.command("spaceunlink")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_spaceunlink(
        self,
        event: AstrMessageEvent,
        space_id: str,
        child_room_id: str,
    ):
        """移除 Space 子房间"""
        async for result in self.cmd_space_unlink(event, space_id, child_room_id):
            yield result

    @admin_group.command("spacechildren")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_spacechildren(
        self,
        event: AstrMessageEvent,
        space_id: str,
        limit: int = 20,
    ):
        """查看 Space 子房间"""
        async for result in self.cmd_space_children(event, space_id, limit):
            yield result

    @admin_group.command("knock")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_knock(
        self, event: AstrMessageEvent, room_id_or_alias: str, reason: str = ""
    ):
        """敲门请求加入房间"""
        async for result in self.cmd_knock(event, room_id_or_alias, reason):
            yield result

    @admin_group.command("roomrefresh")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_roomrefresh(self, event: AstrMessageEvent, room_id: str = ""):
        """重新获取房间信息"""
        async for result in self.cmd_room_refresh(event, room_id):
            yield result

    @admin_group.command("rooms")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_rooms(self, event: AstrMessageEvent):
        """列出 Bot 已加入的所有房间"""
        async for result in self.cmd_rooms(event):
            yield result

    @admin_group.command("roominfo")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_roominfo(self, event: AstrMessageEvent, room_id: str = ""):
        """查看房间详细信息"""
        async for result in self.cmd_room_info(event, room_id):
            yield result

    @admin_group.command("banlist")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_banlist(self, event: AstrMessageEvent, room_id: str = ""):
        """查看房间封禁列表"""
        async for result in self.cmd_banlist(event, room_id):
            yield result

    @admin_group.command("setroomname")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_setroomname(
        self, event: AstrMessageEvent, name: GreedyStr, room_id: str = ""
    ):
        """设置房间名称"""
        async for result in self.cmd_setroomname(event, name, room_id):
            yield result

    @admin_group.command("setroomtopic")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_setroomtopic(
        self, event: AstrMessageEvent, topic: GreedyStr, room_id: str = ""
    ):
        """设置房间主题"""
        async for result in self.cmd_setroomtopic(event, topic, room_id):
            yield result

    @admin_group.command("setname")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_setname(self, event: AstrMessageEvent, name: GreedyStr):
        """修改 Bot 的显示名称"""
        async for result in self.cmd_setname(event, name):
            yield result

    @admin_group.command("setavatar")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_setavatar(self, event: AstrMessageEvent):
        """通过引用图片修改 Bot 的头像"""
        async for result in self.cmd_setavatar(event):
            yield result

    @admin_group.command("setstatus")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_setstatus(
        self, event: AstrMessageEvent, status: str = "", message: str = ""
    ):
        """修改 Bot 的在线状态"""
        async for result in self.cmd_setstatus(event, status, message):
            yield result

    @admin_group.command("statusmsg")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_statusmsg(self, event: AstrMessageEvent, message: str = ""):
        """设置或清除 Bot 的状态消息"""
        async for result in self.cmd_statusmsg(event, message):
            yield result

    @admin_group.command("purgebot")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_purgebot(
        self, event: AstrMessageEvent, limit: int = 100, room_id: str = ""
    ):
        """清理机器人历史消息"""
        async for result in self.cmd_purge_bot_messages(event, limit, room_id):
            yield result

    @admin_group.command("scanqr")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_scanqr(
        self,
        event: AstrMessageEvent,
        user_id: str,
        device_id: str,
        qr_input: str = "",
        matrix_platform_id: str = "",
    ):
        """扫描 Matrix 设备验证二维码。"""
        async for result in self.cmd_scanqr(
            event,
            user_id,
            device_id,
            qr_input,
            matrix_platform_id,
        ):
            yield result

    @admin_group.command("matrixstatus")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_matrixstatus(
        self,
        event: AstrMessageEvent,
        matrix_platform_id: str = "",
    ):
        """查看 Matrix 适配器运行状态。"""
        async for result in self.cmd_matrixstatus(event, matrix_platform_id):
            yield result

    @admin_group.command("reconnect")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_reconnect(
        self,
        event: AstrMessageEvent,
        matrix_platform_id: str = "",
    ):
        """主动中断当前 /sync 长轮询并立即重连。"""
        async for result in self.cmd_reconnect(event, matrix_platform_id):
            yield result

    @admin_group.command("resendpending")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_resendpending(
        self,
        event: AstrMessageEvent,
        matrix_platform_id: str = "",
        limit: str = "20",
    ):
        """重试最近失败或挂起的出站消息记录。"""
        async for result in self.cmd_resendpending(event, matrix_platform_id, limit):
            yield result

    @admin_group.command("verify")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_verify(self, event: AstrMessageEvent, device_id: str):
        """手动确认 SAS 验证（支持按 adapter 推送到多房间）"""
        if str(event.get_platform_name() or "").strip().lower() != "matrix":
            yield event.plain_result("此命令仅在 Matrix 平台可用")
            return

        self._maybe_apply_admin_room_config()

        matrix_utils_cls = self._get_matrix_utils_cls()
        if matrix_utils_cls is None:
            yield event.plain_result("未检测到 Matrix 适配器插件")
            return

        e2ee_manager = None
        try:
            target_platform_id = str(event.get_platform_id() or "")
            e2ee_manager = matrix_utils_cls.get_matrix_e2ee_manager(
                self.context,
                target_platform_id,
            )
        except Exception as e:
            yield event.plain_result(f"获取适配器失败：{e}")
            return

        if not e2ee_manager or not getattr(e2ee_manager, "_verification", None):
            yield event.plain_result("端到端加密未启用或验证模块未初始化")
            return

        ok, message = await e2ee_manager._verification.approve_device(device_id)
        if ok:
            yield event.plain_result(f"✅ {message}")
        else:
            yield event.plain_result(f"❌ {message}")

    @admin_group.command("help")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_help(self, event: AstrMessageEvent):
        """显示所有可用命令的帮助信息"""
        help_text = (
            "**Matrix Admin 管理命令帮助**\n\n"
            "**用户管理：**\n"
            "  `/admin kick <用户> [原因] [room_id]` - 踢出用户\n"
            "  `/admin ban <用户> [原因] [room_id]` - 封禁用户\n"
            "  `/admin unban <用户> [room_id]` - 解除封禁\n"
            "  `/admin invite <用户> [room_id]` - 邀请用户\n"
            "  `/admin whois <用户>` - 查询用户信息\n"
            "  `/admin search <关键词> [数量]` - 搜索用户\n"
            "  `/admin banlist [room_id]` - 查看封禁列表\n\n"
            "**权限管理：**\n"
            "  `/admin promote <用户> [级别] [room_id]` - 提升权限\n"
            "  `/admin demote <用户> [room_id]` - 降低权限\n"
            "  `/admin power <用户> <等级> [room_id]` - 设置权限等级\n"
            "  `/admin admins [room_id]` - 列出管理员\n\n"
            "**房间管理：**\n"
            "  `/admin rooms` - 列出已加入的房间\n"
            "  `/admin roominfo [room_id]` - 查看房间详情\n"
            "  `/admin createroom <名称> [是否公开]` - 创建房间\n"
            "  `/admin setroomname <名称> [room_id]` - 设置房间名称\n"
            "  `/admin setroomtopic <主题> [room_id]` - 设置房间主题\n"
            "  `/admin dm <用户>` - 创建私聊\n"
            "  `/admin forget [room_id]` - 忘记房间\n"
            "  `/admin knock <room_id> [原因]` - 请求加入\n"
            "  `/admin roomrefresh [room_id|all]` - 刷新房间缓存\n\n"
            "**空间 (Space) 管理：**\n"
            "  `/admin spacecreate <名称> [是否公开] [主题]` - 创建 Space\n"
            "  `/admin spacelink <space_id> <room_id> [推荐]` - 挂载子房间\n"
            "  `/admin spaceunlink <space_id> <room_id>` - 移除子房间\n"
            "  `/admin spacechildren <space_id> [limit]` - 查看子房间\n"
            "  `/admin hierarchy [room_id] [limit]` - 查看层级\n\n"
            "**别名管理：**\n"
            "  `/admin aliasset <别名> [room_id]` - 设置别名\n"
            "  `/admin aliasdel <别名>` - 删除别名\n"
            "  `/admin aliasget <别名>` - 解析别名\n"
            "  `/admin publicrooms [server] [limit]` - 公共房间列表\n\n"
            "**Bot 管理：**\n"
            "  `/admin setname <名称>` - 修改显示名称\n"
            "  `/admin setavatar` - 修改头像（引用图片）\n"
            "  `/admin setstatus <状态> [消息]` - 修改在线状态\n"
            "  `/admin statusmsg [消息]` - 设置状态消息\n"
            "  `/admin purgebot [数量] [room_id]` - 清理历史消息\n\n"
            "**屏蔽管理：**\n"
            "  `/admin ignore <用户>` - 屏蔽用户\n"
            "  `/admin unignore <用户>` - 取消屏蔽\n"
            "  `/admin ignorelist` - 查看屏蔽列表\n\n"
            "**运行态命令：**\n"
            "  `/admin scanqr <用户ID> <设备ID> [二维码] [platform_id]` - 扫描\n"
            "  `/admin matrixstatus [platform_id]` - 适配器运行状态\n"
            "  `/admin reconnect [platform_id]` - 重连 /sync\n"
            "  `/admin resendpending [platform_id] [limit]` - 重试挂起消息\n"
            "  `/admin verify <device_id>` - 手动确认 SAS 验证\n\n"
            "**房间升级：**\n"
            "  `/admin upgrade <版本> [room_id]` - 升级房间版本\n\n"
            "提示：`[room_id]` 可选，默认使用当前房间。"
            "`[platform_id]` 可选，多适配器时指定。"
        )
        yield event.plain_result(help_text)
