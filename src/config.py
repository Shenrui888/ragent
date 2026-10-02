import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTO_TOKEN", None)
WORKDIR = Path(r'D:\develop\projects\Agent\Rgent\ragent\workspace')
MODEL = os.environ["MODEL_ID"]
SYSTEM = (f"你是一个在{WORKDIR}代码Agent，"
          "在你开始多步骤任务之前，使用todo_write来计划步骤，"
          "每次执行步骤后更新任务状态。"
          )

SUB_MODEL = os.environ["MODEL_ID"]
SUB_SYSTEM = (f"You are a coding agent at {WORKDIR}. "
    "Complete the given task, then return a concise final answer.")