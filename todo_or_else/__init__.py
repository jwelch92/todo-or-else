import functools
import re
from datetime import datetime
from typing import Union, Callable, Optional, Tuple

from dateutil.parser import parse as dt_parse

By = Optional[Union[datetime, str, float, int]]
When = Optional[Union[bool, Callable[..., bool]]]

# TODO-OR-ELSE:10/13/2021 Add linting, CI, and packaging


class OrElseException(Exception):
    def __init__(self, msg: str, reason: str) -> None:
        # TODO-OR-ELSE:10/17/2021 Update the wording to be more spooky
        message = f"""
        You made a pact to complete this TODO: '{msg}' 
        The time has come because {reason}
        Complete this TODO or face the consequences.
        """
        super().__init__(message)


class TodoOrElse:
    def __call__(self, pact: str, *, by: By = None, when: When = None):
        if by is None and when is None:
            raise ValueError(
                "Invalid arguments, you must specify at least one of (by, when) or we cannot bind you to "
                "this pact."
            )
        self._evaluate_by(pact, by)
        self._evaluate_when(pact, when)

    def _evaluate_by(self, pact: str, by: By):
        now = datetime.utcnow()
        due = self._parse_date(by)
        if due is not None:
            if now > due:
                raise OrElseException(
                    pact,
                    f"you agreed to complete this TODO by {due} and it is now {now}",
                )
        return None

    def _evaluate_when(self, pact: str, when: When):
        if when is not None:
            if isinstance(when, bool) and when:
                raise OrElseException(
                    pact,
                    f"you agreed to complete this TODO when the condition was True and it has "
                    f"come to pass.",
                )
            elif callable(when) and when():
                raise OrElseException(
                    pact,
                    f"you agreed to complete this TODO when the function returned True and it "
                    f"has come to pass.",
                )
        return None

    def by(self, pact: str, by: By) -> None:
        self._evaluate_by(pact, by)

    def when(self, pact: str, when: When) -> None:
        self._evaluate_when(pact, when)

    def wrap(self, pact: str, by: By = None, when: When = None):
        self.__call__(pact, by=by, when=when)

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def _parse_date(
        d: Optional[Union[datetime, str, float, int]]
    ) -> Optional[datetime]:
        if d is None:
            return None
        elif isinstance(d, datetime):
            return d
        elif isinstance(d, str):
            return dt_parse(d)
        elif isinstance(d, float) or isinstance(d, int):
            return datetime.fromtimestamp(float(d))
        else:
            raise ValueError("Invalid date")


# TODO-OR-ELSE:10/21/2021 Move the flake8 stuff to it's own file

RX_TODO_OR_ELSE = re.compile(r"\b(TODO-OR-ELSE):([^\s]+)(.*)$")

CODE = "DIE001"


def flake8_entrypoint(physical_line: str) -> Optional[Tuple[int, str]]:
    match = RX_TODO_OR_ELSE.search(physical_line)
    if match:
        t = TodoOrElse()
        by = match.group(2)
        pact = match.group(3).strip()
        try:
            t.by(pact, by=by)
        except OrElseException as e:
            return match.start(), f"{CODE} {e}"
    return None


flake8_entrypoint.name = "todo_or_else"
flake8_entrypoint.version = "0.1.0"

todo_or_else = TodoOrElse()
