import numpy as np


def product_numerator(df):
    # This is a function that gives the individual inputs a product index
    # Example output: series - [1 1 1 1 1 1 2 2 2 2 2 2 2 3 3 3 3 3 3 3 ... ]
    return df["product_no"].ne(df["product_no"].shift(1, fill_value = df.iloc[0]["product_no"])).cumsum() + 1


def input_indices(df):
    """
    :param BOM DataFrame:
    :return:
    This function gives an output of indices of process inputs
    Example output: index - [1, 6, 8, 12, 16, ...]
    """
    return df[df["level"].ge(df["level"].shift(-1, fill_value = df.iloc[-1]["level"]))].index