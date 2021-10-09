# TODO OR ELSE

Make a pact to complete your TODOs on time or else. This _will_ throw errors and break your code if you let it get to production.

Inspired by [chedeuzot/py-todo-or-die](https://github.com/achedeuzot/py-todo-or-die) which is in turn inspired by 

- [davidpdrsn/todo-or-die](https://github.com/davidpdrsn/todo-or-die) (Rust)
- [searls/todo_or_die](https://github.com/searls/todo_or_die) (Ruby)

## Features

And sort of a todo list for myself to finish the rest of the stuff required for a usable Python package. 

- [x] Use as a library
- [x] Flake8 plugin
- [ ] Fully tested
- [ ] CI with linting and tests
- [ ] Fully typed and type checked
- [ ] Published on PyPi
- [ ] Release notes and versioning
- [ ] Better Python version support (only tested on 3.9 right now)

Possible future features

- Short circuit on first error. Stop throwing errors after the first one. This would assume there's telemetry in place to alert if the error throws.
- More spooky wordings
- Actual consequences: charge money, delete files, send a mean email. 
- Nice mode: warn when getting close instead of failing after the date or condition has passed

## Usage

### In code

```python
import datetime
from todo_or_else import todo_or_else

# raise an OrElseException past a certain date
todo_or_else("You must fix this", by=datetime.datetime(2021, 10, 31, 12, 11, 11))
# arbitrary date string parsing courtesy of python-dateutil
todo_or_else("You must fix this", by="10/31/2021 12PM")
# it accepts int/float unix timestamps as well
todo_or_else("You must fix this", by=1634426452.915833)
# you can also use an alias
todo_or_else.by("you must fix this", "10/31/2021 12PM")

def f() -> bool:
    return True

# raise an exception when a given condition is met
todo_or_else("You must fix this", when=f)

todo_or_else("You must fix this", when=something > something_else)
# alias works here too 
todo_or_else.when("You must fix this", something > something_else)

# You can combine conditions, the first to fail will be the resulting error
todo_or_else("You must fix this", by="10/31/2021 12PM", when=something < something_else)

# wrap a function

@todo_or_else.wrap("update this to return something", by="10/31/2021")
def some_func(some_arg: str) -> None:
    print(some_arg)
```

### With the flake8 plugin

The error code is `DIE001`. 

Use it in your TODO comments. The syntax is somewhat picky, `-` was chosen because using `_` breaks some IDE # TODO comment highlighting. 

`# TODO-OR-ELSE:<by some date, accepts same formats todo_or_else.by> <some message which is interpreted as the pact>`

```python

def some_func(some_arg: str) -> None:
    # TODO-OR-ELSE:10/31/2021 update this to return something
    print(some_arg)
```

```bash
poetry run flake8 .
./tests/__init__.py:5:7: DIE001 
        You made a pact to complete this TODO: 'update this to return something' 
        The time has come because you agreed to complete this TODO by 2021-10-01 00:00:00 and it is now 2021-10-09 23:25:55.846791
        Complete this TODO or face the consequences.
```


## Tips for success

- Use the flake8 plugin to avoid runtime errors.
- Exercise your code in tests which will catch todo_or_else before your code is running
- Instrument your code so that you can see when you hit an `OrElse` error
- Use your best judgement, this tool might cause more headaches than it saves ¯\_(ツ)_/¯

