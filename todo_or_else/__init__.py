"""TODO OR ELSE -- a package for holding you accountable to your TODOs."""  # noqa
import functools
import re
from datetime import datetime
from typing import Any, Callable, Optional, Tuple, Union

from dateutil.parser import parse as dt_parse

By = Optional[Union[datetime, str, float, int]]
When = Optional[Union[bool, Callable[..., bool]]]


class PactViolatedException(Exception):
    """The PactViolatedException raised when you fail to complete your tasks.

    Attributes:
        pact(str): Holds the message passed into the Exception.
        reason(str): The reason why the exception was raised.
    """

    def __init__(self, pact: str, reason: str) -> None:
        """PactViolatedException.

        Args:
            pact(str): Pact message.
            reason(str): Why the pact was violated.
        """
        # TODO-OR-ELSE(10/17/2021) Update the wording to be more spooky
        self.pact = pact
        self.reason = reason
        message = f"""
        You made a pact to complete this TODO: '{pact}'
        The time has come because {reason}
        Complete this TODO or face the consequences.
        """
        super().__init__(message)

    def short(self) -> str:
        """Short form of the admonition error message used by the flake8 plugin error messages."""
        return f"Pact '{self.pact}' violated because {self.reason}"


class TodoOrElse:
    """TodoOrElse is the main API of todo_or_else."""

    def __call__(self, pact: str, *, by: By = None, when: When = None) -> None:
        """Entrypoint that supports both time and boolean conditions."""
        if by is None and when is None:
            raise ValueError(
                "Invalid arguments, you must specify at least " "one of (by, when) or we cannot bind you to this pact."
            )
        self._evaluate_by(pact, by)
        self._evaluate_when(pact, when)

    def _evaluate_by(self, pact: str, by: By) -> Optional[str]:
        """Helper for evaluating time based pacts."""
        now = datetime.utcnow()
        due = self._parse_date(by)
        if due is not None:
            if now > due:
                raise PactViolatedException(
                    pact,
                    f"you agreed to complete this TODO by {due.strftime('%Y-%m-%d')}.",
                )
        return None

    def _evaluate_when(self, pact: str, when: When) -> Optional[str]:
        """Helper for evaluating boolean pacts."""
        if when is not None:
            if isinstance(when, bool) and when:
                raise PactViolatedException(
                    pact,
                    "you agreed to complete this TODO when the condition was True and it has come to pass.",
                )
            elif callable(when) and when():
                raise PactViolatedException(
                    pact,
                    "you agreed to complete this TODO when the function returned True and it has come to pass.",
                )
        return None

    def by(self, pact: str, by: By) -> None:
        """Pact to be completed by a time. Shorthand for todo_or_else(msg, by=time)."""
        self._evaluate_by(pact, by)

    def when(self, pact: str, when: When) -> None:
        """Pact to be completed by a condition. Shorthand for todo_or_else(msg, when=bool)."""
        self._evaluate_when(pact, when)

    def wrap(self, pact: str, by: By = None, when: When = None) -> Callable:
        """Decorate a callable with a todo_or_else check."""
        self.__call__(pact, by=by, when=when)

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def _parse_date(d: Optional[Union[datetime, str, float, int]]) -> Optional[datetime]:
        """Helper to parse incoming dates."""
        if d is None:
            return None
        elif isinstance(d, datetime):
            return d
        elif isinstance(d, str):
            return dt_parse(d)
        elif isinstance(d, float) or isinstance(d, int):
            return datetime.fromtimestamp(float(d))
        else:
            raise TypeError("Invalid date")


RX_TODO_OR_ELSE = re.compile(r"\b(TODO-OR-ELSE|todo-or-else)\((.+)\)(.*)$")

CODE = "DIE001"


def flake8_entrypoint(physical_line: str) -> Optional[Tuple[int, str]]:
    """Flake8 plugin entrypoint that operates on physical lines."""
    match = RX_TODO_OR_ELSE.search(physical_line)
    if match:
        by = match.group(2)
        pact = match.group(3).strip()
        try:
            TodoOrElse().by(pact, by=by)
        except PactViolatedException as e:
            return match.start(), f"{CODE} {e.short()}"
    return None


flake8_entrypoint.name = "todo_or_else"  # type:ignore
flake8_entrypoint.version = "0.1.0"  # type:ignore

todo_or_else = TodoOrElse()
