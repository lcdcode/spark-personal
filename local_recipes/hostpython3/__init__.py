from pythonforandroid.recipes.hostpython3 import HostPython3Recipe as BaseHostPython3Recipe


class HostPython3Recipe(BaseHostPython3Recipe):
    """
    Modified hostpython3 recipe to use Python 3.11 instead of 3.14.

    Python 3.14 has compilation issues on Android (remote debugging module).
    Python 3.11 is stable and tested for Android deployment.
    """
    version = '3.11.11'


recipe = HostPython3Recipe()
