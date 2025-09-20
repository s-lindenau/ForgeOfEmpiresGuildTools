import logging


class Table:
    def __init__(self, table_name: str, rows: list[dict] = None):
        """
        Initialize the table with a name and rows.

        Args:
            table_name (str): The name of the table.
            rows (list[dict], optional): A list of rows (dictionaries) representing the table data. Defaults to an empty list.
        """
        self.table_name = table_name
        self.rows = rows if rows is not None else []

    def add_row(self, row: dict):
        """
        Add a row to the table.

        Args:
            row (dict): A dictionary representing a row of data.
        """
        self.rows.append(row)

    def get_rows(self) -> list[dict]:
        """
        Retrieve all rows in the table.

        Returns:
            list[dict]: A list of rows in the table.
        """
        return self.rows

    def get_sorted_values_from_rows_by_key(self, key: str, sort_direction: bool = True):
        return Table.get_sorted_values_from_table_rows_by_key(self.rows, key, sort_direction)

    def get_row_where_key_matches_value(self, key: str, value) -> dict:
        return Table.get_table_row_where_key_matches_value(self.rows, key, value)

    @staticmethod
    def get_sorted_values_from_table_rows_by_key(rows: list[dict], key: str, sort_direction: bool = True):
        """
        Extracts all {key} values from the rows of the given table
        and sorts them in descending order.

        Args:
            rows: A list of dicts containing rows with {key} keys.
            key: The key to search for in the table rows
            sort_direction: Sort order of result. True = High to Low (DESC), False = Low to High (ASC)

        Returns:
            list: A list of sorted {key} values in descending order.
        """
        values_for_key = [row.get(key) for row in rows if key in row]
        return sorted(values_for_key, reverse=sort_direction)

    @staticmethod
    def get_table_row_where_key_matches_value(rows: list[dict], key: str, value) -> dict:
        """
        Find the first row in the table where the {key} has value {value}
        :param rows: A list of dicts with rows to search
        :param key: The key that should be present in the table row
        :param value: The value of {key} entry to look for
        :return: The row if found, None otherwise
        """
        return next((r for r in rows if r.get(key) == value), None)


class Database:
    def __init__(self, format_name: str, format_version: str, database_name: str, database_version: int):
        """
        Initialize the database with a format name, format version, database name, database version and an empty list of tables.

        Args:
            format_name (str): The name of the database format.
            format_version (str): The version of the database format.
            database_name (str): The name of the database.
            database_version (int): The version of the database.
        """
        self.format_name = format_name
        self.format_version = format_version
        self.database_name = database_name
        self.database_version = database_version
        self.tables = []

    def add_table(self, table_name: str, rows: list[dict]):
        """
        Add a table to the database.

        Args:
            table_name (str): The name of the table.
            rows (list[dict]): A list of rows (dictionaries) representing the table data.
        """
        table = Table(table_name, rows)
        self.tables.append(table)

    def get_table(self, table_name: str) -> Table:
        """
        Retrieve a table by its name.

        Args:
            table_name (str): The name of the table to retrieve.

        Returns:
            dict: The table data if found, otherwise an empty Table instance.
        """
        for table in self.tables:
            if table.table_name == table_name:
                return table

        logging.error(f"Table '{table_name}' not found in the database!")
        return Table(table_name, [])
