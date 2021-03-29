# Contributing
## Adding new features
Before adding a new feature or cog, or modifying a cog for any purpose other then bug-fixes or cleaning up code, we do ask that you open up a Github issue with the RFC tag. This is done so that we can decide we want a feature before someone writes up code - only to end up not merging it. RFC's are open for anyone to contribute and discuss, however we do ask that everyone remains civil and remain on topic. Reference this repository if you haven't created a contribution previously github.com/firstcontributions/first-contributions.

## Code quality
We do ask that everyone uses [PEP8 standards](https://www.python.org/dev/peps/pep-0008/). On top of this we also ask that the code passes [Pylint](https://www.pylint.org/), all code will be automatically formatted via github CI actions with the [Black Autoformatter](https://github.com/psf/black) for consistency. This is done so the code can remain consistent and easy to understand (different files should look stylistically similar and follow the same conventions).

## Python compatibility
This repo will be running on a NixOS server instance, and will be using the latest available version of python in the main stable repositories. At the time of this writing, the current running version will be python 3.9. This message will be updated accordingly on a python version update.

## Dependencies
We do ask that you add all dependencies to the ``requirements.txt``. On top of this we also ask that you **pin the dependency version** so as to not break compatibility due to different library versions. We also ask that you stick with large, reputable dependencies only, and only add dependencies when it is required to do so as the behavior from the dependency isn't trivial to implement yourself.

## Updating the database
Please update the schema and throw in some barebone testing data into the in repo database, if you add new tables or fields. This makes it trivial to work with. The production database will *not* be in this repo. 

## Code of Conduct
We don't have a formal code of conduct, but we do ask that everyone remains civil. Arguing will not be tolerated, and we ask that everyone respects the final decision made. That's not to say we can't revisit old issues - but please add something new to the topic when doing so.
