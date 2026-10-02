from .base_tools import *
from .manager.todomanager import TASK_HANDLER,TASK_TOOL
from .subagent.subagent import SUBAGENT_TOOL, SUBAGENT_HANDLER
# .表示当前文所在包
TOOLS = [
    *BASE_TOOLS,*TASK_TOOL,*SUBAGENT_TOOL
]
TOOL_HANDLERS = {
    **BASE_HANDLERS,**TASK_HANDLER,**SUBAGENT_HANDLER
}