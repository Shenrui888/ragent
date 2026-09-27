from anthropic import Anthropic
from dotenv import load_dotenv
import os
import subprocess
import json
import ast
from pathlib import Path

try:
    import readline
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass

load_dotenv(override=True)

WORKDIR = Path.cwd()
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTO_TOKEN", None)
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]
SYSTEM = (f"你是一个在{WORKDIR}代码Agent"
          "在你开始多步骤任务之前，使用todo_write来计划步骤"
          "每次执行步骤后更新任务状态"
          )
# tool_moudle

def run_bash(command:str)->str:
    bash_run = subprocess.run(
        command, shell=True, cwd=WORKDIR,
        capture_output=True, text=True, errors="replace",
        timeout=120
    )
    output = (bash_run.stderr + bash_run.stdout).strip()
    return output[:500] if output else "No output"

    # manager
class TodoManager:
    def __init__(self):
        self.items: list[dict] = []

    def update(self, todos: list | str)->str:
        if isinstance(todos, str):
            try:
                todos = json.loads(todos)
            except json.JSONDecodeError:
                todo = ast.literal_eval(todos)
        elif not isinstance(todos, list):
            raise ValueError("todos must be a list pr JSON string")
        validate = []
        in_progress_count = 0
        for index, todo in enumerate(todos):
            content = str(todo.get("content", "")).strip()
            status = str(todo.get("status", "pending")).lower()
            if status == "in_progress":
                in_progress_count += 1
            validate.append({
                "content":content, "status":status
            })
        self.items = validate
        return self.render()

    def render(self)->str:
        lines = []
        for todo in self.items:
            maker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]",
            }[todo["status"]]
            lines.append(
                f"{maker} {todo['content']}"
            )
        done = sum(todo["status"] == "completed" for todo in self.items)
        lines.append(
            f"\n{done} / {len(self.items)} completed"
        )
        return "\n".join(lines)
TODO = TodoManager()

def run_todo_write(todos: list | str)->str:
    output = TODO.update(todos)
    print(output)
    return output

TOOLS = [
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
    {
        "name": "todo_write",
        "description":"Create and manage a task list for your current coding session.",
        "input_schema":
        {
            "type": "object",
            "properties": 
            {
                "todos":
                {
                    "type": "array",
                    "maxItems": 20,
                    "items": 
                    {
                        "type": "object",
                        "properties":
                        {
                            "content":
                            {
                                "type": "string",
                                "minLength": 1,
                            },
                            "status":
                            {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                            },
                        },
                        "required":["content", "status"],
                    },
                },
            },
            "required": ["todos"],
        },
    },
]

TOOL_HANDLERS = {
    "bash": run_bash,
    "todo_write": run_todo_write,
}

# hook_moudle

'''
    HOOK -> 扩展在时间轴上 ->到什么节点了，就该做什么事情
    状态机/工作流 -> 扩展在流程结构上 ->到什么节点了，如何做这件事
'''
HOOKS = {
    "UserPromptSubmit": [],
    "PreToolUse": [],
    "PostToolUse": [],
    "Stop": [],
}

def register_hooks(event:str, callback):
    HOOKS[event].append(callback)

# *args表示接收任意参数 当作”元组“处理
def trigger_hooks(event:str, *args)->str:
    for callback in HOOKS[event]:
        result = callback(*args)
        if result is not None:
            return result
    return None


# loop_moudle

def agent_loop(messages: list):
    rounds_since_todo = 0
    while True:
        response = client.messages.create(
            model=MODEL, tools=TOOLS, system=SYSTEM,
            max_tokens=8000, messages=messages
        )
        messages.append({
            "role":"assistant", "content":response.content
        })

        tool_calls = [
            block for block in response.content if block.type == "tool_use"
        ]

        if not tool_calls:
            return

        results = []
        used_todo = False
        for block in tool_calls:
            blocked = trigger_hooks("PreToolUse",block)
            if blocked:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(blocked),
                })
            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input) if handler else "No such tool"
            trigger_hooks("PostToolUse",block)

            if block.name == "todo_write":
                used_todo = True
    
            results.append({
                "type":"tool_result",
                "tool_use_id":block.id,
                "content":str(output), 
            })
            print(output[:200])

        rounds_since_todo = 0 if used_todo else rounds_since_todo+1
        if rounds_since_todo >= 3:
            results.append({
                "type": "text",
                "text": "<reminder>Update your todos.</reminder>"
            })
            rounds_since_todo = 0
        messages.append(
            {"role":"user", "content":results}
        )


if __name__ == "__main__":
    history = []
    while(True):
        messages = input("消息：").strip()
        trigger_hooks("UserPromptSubmit",messages)
        history.append({"role":"user", "content":messages})
        agent_loop(history)
        for block in history[-1]["content"]:
            if getattr(block, "type", None) == "text":
                print(block.text)