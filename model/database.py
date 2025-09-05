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

    def to_dict(self) -> dict:
        """
        Convert the table to a dictionary representation.

        Returns:
            dict: The dictionary representation of the table.
        """
        return {
            "tableName": self.table_name,
            "rows": self.rows
        }


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

    def to_dict(self) -> dict:
        """
        Convert the database to a dictionary representation.

        Returns:
            dict: The dictionary representation of the database.
        """
        return {
            "formatName": self.format_name,
            "formatVersion": self.format_version,
            "tables": self.tables
        }
