# global options:
# imported by top-level conftest.py (to get default)
# and by tests (to be able to use in ifskip decorations)

import os

class Opts:
    """
    string values: pass property names to is_set/set_bool; property
    values (which should match) are used as environment variables.
    """
    MC_API_TEST_FAST = "MC_API_TEST_FAST"

    @staticmethod
    def is_set(opt: str) -> bool:
        """
        Non-empty environment values are true.  Used both to get command
        line option defaults (in top-level conftest.py) AND in tests
        to check command line option value.
        """
        return bool(os.environ.get(opt))

    def set_bool(opt: str, val: bool) -> None:
        """
        Used to propogate command line options back to environment
        (in top-level conftest.py) for use in tests.
        """
        if val:
            os.environ[opt] = "1"
        else:
            os.environ.pop(opt, None)
