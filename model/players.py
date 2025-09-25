import json
from util.sort_direction import SortDirection

class Players:
    def __init__(self):
        # Initialize an empty dictionary to store players
        self.players_by_id = {}
        self.players_by_name = {}

    def add_player(self, player_id, player_name, player_data):
        """
        Add a player to the dictionary.

        :param player_id: Unique identifier for the player
        :param player_name: Name of the player
        :param player_data: Dictionary containing player details
        """
        self.players_by_name[player_name] = player_data
        self.players_by_id[player_id] = player_data.get("player_name")

    def get_player_by_name(self, player_name) -> dict:
        """
        Retrieve a player by their name.

        :param player_name: Name for the player.
        :return: Player data if found, None otherwise
        """
        return self.players_by_name.get(player_name)

    def get_player_by_id(self, player_id) -> dict:
        """
        Retrieve a player by their ID.

        :param player_id: Unique identifier for the player.
        :return: Player data if found, None otherwise
        """
        player_name_for_id = self.players_by_id.get(player_id)
        return self.players_by_name.get(player_name_for_id)

    def get_all_players(self) -> dict:
        """
        Retrieve all players.

        :return: Dictionary of all players
        """
        return self.players_by_name

    def get_sorted_by_key(self, key_to_sort_on: str, sort_direction: str = SortDirection.ASCENDING) -> dict:
        """
        Get all players sorted by a specific key in the player data.
        :param key_to_sort_on: the key in the player data to sort by
        :param sort_direction: a string representing the sort direction, see `SortDirection` class
        :return: A dictionary of players sorted by the specified key in the specified order
        """
        return {k: v for k, v in sorted(self.get_all_players().items(), key=lambda d: d[1][key_to_sort_on], reverse=SortDirection.get_sort_direction(sort_direction))}

    @classmethod
    def from_dict(cls, data: dict):
        if data is None:
            raise json.JSONDecodeError("No Players in dictionary", "players", 1)

        players = Players()
        players_by_name = data.get("players_by_name")
        for player in players_by_name:
            player_data = players_by_name[player]
            players.add_player(
                player_data.get("player_id"),
                player_data.get("player_name"),
                player_data,
            )
        return players
