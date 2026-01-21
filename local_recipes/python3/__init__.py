from pythonforandroid.recipes.python3 import Python3Recipe as BasePython3Recipe


class Python3Recipe(BasePython3Recipe):
    """
    Modified python3 recipe to use Python 3.11 instead of 3.14.

    Python 3.14 has compilation issues on Android (remote debugging module).
    Python 3.11 is stable and tested for Android deployment.
    """
    version = '3.11.11'


recipe = Python3Recipe()
