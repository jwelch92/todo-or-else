from datetime import datetime
from typing import Any

import pytest
from freezegun import freeze_time
from todo_or_else import TodoOrElse, OrElseException


@freeze_time("2021-01-14")
def test_by() -> None:
    toe = TodoOrElse()

    with pytest.raises(OrElseException):
        toe.by("this will fail", "10/1/2020")

    toe.by("this will not fail", "10/1/2021")


def test_todo_or_else_by() -> None:
    toe = TodoOrElse()
    with freeze_time("10/01/2021"):
        toe("this will pass", by="12/21/2021")

    with freeze_time("10/01/2021"):
        with pytest.raises(OrElseException):
            toe("this will fail", by="12/21/2020")


def test_todo_or_else_when() -> None:
    toe = TodoOrElse()
    toe("this will pass", when=False)
    with pytest.raises(OrElseException):
        toe("this will fail", when=True)


def test_todo_or_else_both() -> None:
    toe = TodoOrElse()
    with freeze_time("10/21/2021"):
        toe("this will pass", by="12/31/2021 12PM", when=False)

    # this will pass by but fail when
    with freeze_time("10/21/2021"):
        with pytest.raises(OrElseException):
            toe("this will pass", by="12/31/2021 12PM", when=True)
    # this will fail by but fail when
    with freeze_time("10/21/2021"):
        with pytest.raises(OrElseException):
            toe("this will pass", by="12/31/2020 12PM", when=False)


def test_todo_or_else_invalid_args() -> None:
    toe = TodoOrElse()
    with pytest.raises(ValueError):
        toe("this pact has no conditions")


@freeze_time("10/31/2021")
def test_date_parsing() -> None:
    # not using pytest parameterize so that it's easier to use freezegun
    table = [
        (datetime.now(), datetime.now()),
        ("10/31/2021", datetime(2021, 10, 31, 0, 0, 0, 0)),
        (
            datetime.now().timestamp(),
            datetime.now(),
        ),
        (
            int(datetime.now().timestamp()),
            datetime.now(),
        ),
        (None, None),
    ]

    for date, expected in table:
        assert TodoOrElse()._parse_date(date) == expected


def test_date_parsing_error() -> None:
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        TodoOrElse()._parse_date({})  # type:ignore


def test_when() -> None:
    toe = TodoOrElse()

    with pytest.raises(OrElseException):
        toe.when("this will fail", True)

    toe.when("this will not fail", False)


def test_when_callable() -> None:
    toe = TodoOrElse()
    with pytest.raises(OrElseException):
        toe.when("this will fail", lambda: True)

    toe.when("this will not fail", lambda: False)
