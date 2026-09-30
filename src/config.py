import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

WORKDIR = Path(r'D:\develop\projects\Agent\Rgent\ragent\workspace')
MODEL = os.environ["MODEL_ID"]
SYSTEM = (f"你是一个在{WORKDIR}代码Agent，"
          "在你开始多步骤任务之前，使用todo_write来计划步骤，"
          "每次执行步骤后更新任务状态。"
          )
