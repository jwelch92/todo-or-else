from datetime import datetime
from typing import Optional

import pytest
from freezegun import freeze_time

import todo_or_else
from todo_or_else import OrElseException, TodoOrElse


@pytest.fixture(scope="session")
def todo() -> TodoOrElse:
    return TodoOrElse()


@freeze_time("2021-01-14")
def test_by(todo: TodoOrElse) -> None:
    with pytest.raises(OrElseException):
        todo.by("this will fail", "10/1/2020")

    todo.by("this will not fail", "10/1/2021")


def test_todo_or_else_by(todo: TodoOrElse) -> None:
    with freeze_time("10/01/2021"):
        todo("this will pass", by="12/21/2021")

    with freeze_time("10/01/2021"):
        with pytest.raises(OrElseException) as exc:
            todo("this will fail", by="12/21/2020")
        assert "you agreed to complete this TODO by" in str(exc.value)


def test_todo_or_else_when(todo: TodoOrElse) -> None:
    todo("this will pass", when=False)
    with pytest.raises(OrElseException) as exc:
        todo("this will fail", when=True)

    assert (
        exc.value.short()
        == "Pact 'this will fail' violated because you agreed to complete this TODO when the "
        "condition was True and it has come to pass."
    )


def test_todo_or_else_both(todo: TodoOrElse) -> None:
    with freeze_time("10/21/2021"):
        todo("this will pass", by="12/31/2021 12PM", when=False)

    # this will pass by but fail when
    with freeze_time("10/21/2021"):
        with pytest.raises(OrElseException):
            todo("this will pass", by="12/31/2021 12PM", when=True)
    # this will fail by but fail when
    with freeze_time("10/21/2021"):
        with pytest.raises(OrElseException):
            todo("this will pass", by="12/31/2020 12PM", when=False)


def test_todo_or_else_invalid_args(todo: TodoOrElse) -> None:
    with pytest.raises(ValueError):
        todo("this pact has no conditions")


@freeze_time("10/31/2021")
def test_date_parsing(todo: TodoOrElse) -> None:
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
        assert todo._parse_date(date) == expected


def test_date_parsing_error(todo: TodoOrElse) -> None:
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        todo._parse_date({})  # type:ignore


def test_when(todo: TodoOrElse) -> None:
    with pytest.raises(OrElseException):
        todo.when("this will fail", True)

    todo.when("this will not fail", False)


def test_when_callable(todo: TodoOrElse) -> None:
    with pytest.raises(OrElseException):
        todo.when("this will fail", lambda: True)

    todo.when("this will not fail", lambda: False)


def test_wrap(todo: TodoOrElse) -> None:
    @todo.wrap("fix this function or else", by="10/31/2021")
    def f(something: str) -> str:
        return something

    assert f("hello world") == "hello world"

    with freeze_time("12/31/2021"):
        with pytest.raises(OrElseException):

            @todo.wrap("fix this function or else", by="10/31/2021")
            def f(something: str) -> str:
                return something


@pytest.mark.parametrize(
    "line,expected",
    [
        ("def something():", None),
        ("# TODO-OR-ELSE(12/31/2021) it is done", None),
        (
            "# TODO-OR-ELSE(09/30/2021) do something",
            "DIE001 Pact 'do something' violated because you agreed to complete this TODO by 2021-09-30.",
        ),
    ],
)
@freeze_time("10/31/2021")
def test_flake8_plugin(line: str, expected: Optional[str]) -> None:
    value = todo_or_else.flake8_entrypoint(line)
    if value is None:
        assert value == expected
    else:
        _, msg = value
        assert msg == expected
    # noinspection PyUnresolvedReferences
    assert todo_or_else.flake8_entrypoint.name == "todo_or_else"  # noqa
