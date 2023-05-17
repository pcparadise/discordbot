# Contributing
## Adding new features
Before adding a new feature or cog, or modifying a cog for any purpose other then bug-fixes or cleaning up code, we do ask that you open up a [Github issue with the RFC tag](https://github.com/pcparadise/discordbot/issues/5). This is done so that we can decide we want a feature before someone writes up code - only to end up not merging it. RFC's are open for anyone to contribute and discuss, however we do ask that everyone remains civil and remain on topic. Reference this repository if you haven't created a contribution previously github.com/firstcontributions/first-contributions.

## Code quality
We do ask that everyone uses [PEP8 standards](https://www.python.org/dev/peps/pep-0008/). On top of this we also ask that the code passes [Pylint](https://www.pylint.org/), and should also be formatted by the [Black Autoformatter](https://github.com/psf/black) for consistency. This is done so the code can remain consistent and easy to understand (different files should look stylistically similar and follow the same conventions). It's worth noting that the pylint version is currently pinned to 2.7.4 and black's version is pinned to 20.8b1, which currently is the latest of each. This is likely to remain the versions we use for a long while and we won't be updating these tools super regularly - nor will we be on the latest version from now on. IMPORTANT NOTE: These are now contained in pyproject.toml so I'd just require use that with poetry and you should be golden. In the future we might make a poetry command to run pylint and black for you.

## Python compatibility
This repo will be running on a NixOS server instance, and will be using the latest available version of python in the main stable repositories. At the time of this writing, the current running version will be python 3.10. This message will be updated accordingly on a python version update.

## Dependencies
We use pyproject.toml and poetry to manage dependencies. We do ask that if a library uses semver, to use the ^ operator, and otherwise use any code stability guarentees they give you. We also ask that you stick with large, reputable dependencies only, and only add dependencies when it is required to do so as the behavior from the dependency isn't trivial to implement yourself.

## Updating the database
Please update the schema and throw in some barebone testing data into the in repo database, if you add new tables or fields. This makes it trivial to work with. The production database will *not* be in this repo. 

## Error Handling
To handle new errors, you need to add a new error class to the ``src/utils/errors.py`` file. The error class should inherit from ``commands.CommandError`` and include a message attribute with the error message. Here's an example: 
```py
# src/utils/errors.py
from discord.ext import commands

class NewCommandError(commands.CommandError): # change the class name, can be anything
    """Error raised for a new command error."""
    message = "New command error message." # add a custom error message 
```
Then, in your code, when you want to raise this error, you can use:
```py
# Raise the new command error
raise errors.NewCommandError() # This should be contained under a check of some form
```
Make sure to import the errors module where you want to use it with ``import src.utils.errors``. _(The error will be caught by the ``on_command_error`` method in the ``CommandErrorHandler`` class under ``src/cogs/error_handler.py``, and the corresponding error message will be sent.)_

*Remember to customize the error message and class name in each error class to fit your specific needs.*

## Code of Conduct
We don't have a formal code of conduct, but we do ask that everyone remains civil. Arguing will not be tolerated, and we ask that everyone respects the final decision made. That's not to say we can't revisit old issues - but please add something new to the topic when doing so.
