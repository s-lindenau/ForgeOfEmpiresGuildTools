class SortDirection:
    ASCENDING = "ASC"
    DESCENDING = "DESC"

    @staticmethod
    def get_sort_direction(direction: str):
        if SortDirection.is_ascending(direction):
            return False
        if SortDirection.is_descending(direction):
            return True
        raise ValueError(f"Invalid sort direction: {direction}.")

    @staticmethod
    def is_ascending(direction: str) -> bool:
        return direction == SortDirection.ASCENDING

    @staticmethod
    def is_descending(direction: str) -> bool:
        return direction == SortDirection.DESCENDING