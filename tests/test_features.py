"""BDD tests for grep functionality."""
from pytest_bdd import scenarios

# Import step definitions
from tests.step_defs.test_grep_info_steps import *
from tests.step_defs.test_grep_tool_steps import *

# Auto-discover and run all scenarios
scenarios('.')
