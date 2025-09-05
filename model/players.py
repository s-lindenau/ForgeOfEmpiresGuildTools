class Players:
    def __init__(self):
        # Initialize an empty dictionary to store players
        self._players = {}
        self._by_id = {}

    def add_player(self, player_id, player_name, player_data):
        """
        Add a player to the dictionary.

        :param player_id: Unique identifier for the player
        :param player_name: Name of the player
        :param player_data: Dictionary containing player details
        """
        self._players[player_name] = player_data
        self._by_id[player_id] = player_data

    def get_player_by_id(self, player_id):
        """
        Retrieve a player by their ID.

        :param player_id: Unique identifier for the player.
        :return: Player data if found, None otherwise
        """
        return self._by_id.get(player_id)

    def get_all_players(self):
        """
        Retrieve all players.

        :return: Dictionary of all players
        """
        return self._players
