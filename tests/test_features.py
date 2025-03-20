from tests.step_defs.test_grep_info_steps import *
from tests.step_defs.test_grep_tool_steps import *

from pytest_bdd import scenarios

scenarios('features/')
