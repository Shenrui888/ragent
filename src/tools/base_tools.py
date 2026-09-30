import subprocess
import os
from config import WORKDIR


def run_bash(command: str) -> str:
    # 解决工具输出乱码
    if os.name == "nt":
        subprocess.run(
            "chcp 65001 >nul", shell=True
        )
    try:
        # 子进程职责：执行命令，处理输出字符
        bash_run = subprocess.run(
            command, shell=True, cwd=WORKDIR,
            capture_output=True, text=True, errors="replace",
            timeout=120,encoding='utf-8'
        )
    except TimeoutError:
        return "Error: Time out(120s)"
    output = (bash_run.stderr + bash_run.stdout).strip()
    return output[:500] if output else "No output"

BASE_TOOLS = [
    {
        "name":"bash",
        "description":"run a shell command",
        "input_schema":{
            "type":"object",
            "properties":{
                "command":{
                    "type":"string"
                }
            },
            "required":["command"]
        } 
    },
]

BASE_HANDLERS = {
    "bash": run_bash,
}

def execute_tool(block, handlers:dict)->str:
    '''输入工具块与函数路由'''
    handler = handlers.get(block.name)
    output = handler(**block.input) if handler else "No such tool"
    return str(output)
