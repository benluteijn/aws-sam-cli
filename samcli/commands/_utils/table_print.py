"""
Utilities for table pretty printing using click
"""
from itertools import count, zip_longest
import textwrap
from functools import wraps

import click


def pprint_column_names(format_string, format_kwargs, margin=None, table_header=None, color="yellow"):
    """

    :param format_string: format string to be used that has the strings, minimum width to be replaced
    :param format_kwargs: dictionary that is supplied to the format_string to format the string
    :param margin: margin that is to be reduced from column width for columnar text.
    :param table_header: Supplied table header
    :param color: color supplied for table headers and column names.
    :return: boilerplate table string
    """

    min_width = 100
    min_margin = 2

    def pprint_wrap(func):
        # Calculate terminal width, number of columns in the table
        width, _ = click.get_terminal_size()
        # For UX purposes, set a minimum width for the table to be usable
        # and usable_width keeps margins in mind.
        width = max(width, min_width)

        total_args = len(format_kwargs)
        if not total_args:
            raise ValueError("Number of arguments supplied should be > 0 , format_kwargs: {}".format(format_kwargs))

        # Get width to be a usable number so that we can equally divide the space for all the columns.
        # Can be refactored, to allow for modularity in the shaping of the columns.
        width = width - (width % total_args)
        usable_width_no_margin = int(width) - 1
        usable_width = int((usable_width_no_margin - (margin if margin else min_margin)))
        if total_args > int(usable_width / 2):
            raise ValueError("Total number of columns exceed available width")
        width_per_column = int(usable_width / total_args)

        # The final column should not roll over into the next line
        final_arg_width = width_per_column - 1

        # the format string contains minimumwidth that need to be set.
        # eg: "{a:{0}}} {b:<{1}}} {c:{2}}}"
        format_args = [width_per_column for _ in range(total_args - 1)]
        format_args.extend([final_arg_width])

        # format arguments are now ready for setting minimumwidth

        @wraps(func)
        def wrap(*args, **kwargs):
            # The table is setup with the column names, format_string contains the column names.
            if table_header:
                click.secho("\n" + table_header)
            click.secho("-" * usable_width, fg=color)
            click.secho(format_string.format(*format_args, **format_kwargs), fg=color)
            click.secho("-" * usable_width, fg=color)
            # format_args which have the minimumwidth set per {} in the format_string is passed to the function
            # which this decorator wraps, so that the function has access to the correct format_args
            kwargs["format_args"] = format_args
            kwargs["width"] = width_per_column
            kwargs["margin"] = margin if margin else min_margin
            result = func(*args, **kwargs)
            # Complete the table
            click.secho("-" * usable_width, fg=color)
            return result

        return wrap

    return pprint_wrap


def wrapped_text_generator(texts, width, margin):
    """

    Return a generator where the contents are wrapped text to a specified width.

    :param texts: list of text that needs to be wrapped at specified width
    :param width: width of the text to be wrapped
    :param margin: margin to be reduced from width for cleaner UX
    :return: generator of wrapped text
    """
    for text in texts:
        yield textwrap.wrap(text, width=width - margin)


def pprint_columns(columns, width, margin, format_string, format_args, columns_dict, color="yellow"):
    """

    Print columns based on list of columnar text, associated formatting string and associated format arguments.

    :param columns: list of columnnar text that go into columns as specified by the format_string
    :param width: width of the text to be wrapped
    :param margin: margin to be reduced from width for cleaner UX
    :param format_string: A format string that has both width and text specifiers set.
    :param format_args: list of offset specifiers
    :param columns_dict: arguments dictionary that have dummy values per column
    :param color: color supplied for rows within the table.
    :return:
    """
    for columns_text in zip_longest(*wrapped_text_generator(columns, width, margin), fillvalue=""):
        counter = count()
        # Generate columnar data that correspond to the column names and update them.
        for k, _ in columns_dict.items():
            columns_dict[k] = columns_text[next(counter)]

        click.secho(format_string.format(*format_args, **columns_dict), fg=color)
