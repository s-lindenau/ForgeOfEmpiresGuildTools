import logging


class TableModel:
    def __init__(self, rows: dict):
        """
        Initialize the table model with rows.

        Args:
            rows (dict): A dict of rows (dictionaries) representing the table data. Must have at least 1 row.
        """
        self.column_names = []
        self.column_functions = []
        self.rows = rows if rows is not None else {}
        if len(rows) < 1:
            raise ValueError("The rows for this TableModel should not be empty!")

    def add_column(self, column_name: str, column_function):
        """
        Add a column to the table model.

        Args:
            column_name (str): the name of the column
            column_function: the function that extracts the value for this column from each row in the table. Takes as input argument the dict of each row
        """
        self.test_column(column_name, column_function)
        self.column_names.append(column_name)
        self.column_functions.append(column_function)

    def test_column(self, column_name: str, column_function):
        # Test column name
        assert len(column_name) > 0
        # Test column function
        for row in self.rows:
            try:
                column_function(self.rows.get(row))
                # test on one row, if OK then return
                return
            except Exception as e:
                logging.error(f"Error evaluating column '{column_name}' function: {e}", exc_info=e)
                raise ValueError(f"Function for column is invalid: {column_name}")

    def get_rows(self) -> dict:
        return self.rows

    def get_columns_names(self) -> list:
        return self.column_names

    def get_columns_functions(self) -> list:
        return self.column_functions

    def get_column_count(self) -> int:
        return len(self.column_names)
