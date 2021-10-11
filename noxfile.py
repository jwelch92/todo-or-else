import tempfile

import nox  # type:ignore
from nox.sessions import Session  # type:ignore

nox.options.sessions = "lint", "tests", "mypy"

locations = "todo_or_else", "noxfile.py"
python_versions = ["3.8", "3.9"]


def install_with_constraints(session, *args, **kwargs):
    """
    Shoutout to HyperModern python for this helper
    https://cjolowicz.github.io/posts/hypermodern-python-03-linting/
    """
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=python_versions)
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python=python_versions)
def lint(session):
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-import-order",
    )
    # We need to install ourselves though
    session.run("poetry", "install", external=True)
    session.run("flake8", *args)


@nox.session(python="3.9")
def black(session: Session):
    args = session.posargs or locations
    install_with_constraints(session, "black", "isort")
    session.run("isort", *args)
    session.run("black", *args)


@nox.session(python=python_versions)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    install_with_constraints(session, "mypy", "types-python-dateutil")
    session.run("mypy", *args)
