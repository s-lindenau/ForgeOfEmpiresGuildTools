import json
from model.players import Players
from model.guild_info import GuildInfo


class FoeGuildToolsData:

    def __init__(self, player_profile_link_template: str, guild_info: GuildInfo, players: Players):
        self.player_profile_link_template = player_profile_link_template
        self.guild_info = guild_info
        self.players = players

    @classmethod
    def empty(cls):
        return FoeGuildToolsData(
            "",
            GuildInfo.from_dict({}),
            Players()
        )

    @classmethod
    def from_dict(cls, data: dict):
        if data is None:
            raise json.JSONDecodeError("No data in dictionary", "root", 0)

        return FoeGuildToolsData(
            data.get("player_profile_link_template"),
            GuildInfo.from_dict(data.get("guild_info")),
            Players.from_dict(data.get("players"))
        )
