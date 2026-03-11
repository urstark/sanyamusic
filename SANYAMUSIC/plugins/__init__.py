
import glob
from os.path import dirname, isfile


def __list_all_modules():
    work_dir = dirname(__file__)
    mod_paths = glob.glob(work_dir + "/*/*.py")

    # List of modules to exclude from loading to reduce CPU/Memory usage
    # These typically contain global message watchers that are not required for music.
    EXCLUDE_MODULES = [
        "misc.filters",
        "tools.couples",
    ]

    all_modules = []
    for f in mod_paths:
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py"):
            mod_name = (f.replace(work_dir, "").replace("/", ".").replace("\\", "."))[1:-3]
            if mod_name not in EXCLUDE_MODULES:
                all_modules.append(mod_name)

    return all_modules


ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]
