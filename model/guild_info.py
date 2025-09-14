import json


class GuildInfo:
    def __init__(self, language: str, server: str, world: str, guild_id: int, guild_name: str):
        self.language = language
        self.server = server
        self.world = world
        self.guild_id = guild_id
        self.guild_name = guild_name

    @classmethod
    def from_dict(cls, data: dict):
        if data is None:
            raise json.JSONDecodeError("No GuildInfo in dictionary", "guild_info", 1)

        return GuildInfo(
            data.get("language"),
            data.get("server"),
            data.get("world"),
            data.get("guild_id"),
            data.get("guild_name")
        )

    def get_guild_name(self):
        if self.guild_name is None:
            return "unknown"
        if len(self.guild_name) < 1:
            return "unknown"
        return self.guild_name

    def __str__(self):
        return str(self.__dict__)
