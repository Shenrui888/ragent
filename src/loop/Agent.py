from anthropic import Anthropic
import os
from config import MODEL,SYSTEM
from tools.main_tools import *
from hooks.Hooks import *

try:
    import readline
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))

# loop_moudle
def agent_loop(messages: list):
    round_since_todo = 0
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
            trigger_hook("Stop", messages)
            return

        results = []
        use_todo = False
        for block in tool_calls:
            blocked = trigger_hook("PreToolUse", block)
            if blocked:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(blocked),
                })
                continue
            try:
                output = execute_tool(block, TOOL_HANDLERS)
            except Exception as e:
                output = f"Error: {e}"
            trigger_hook("PostToolUse", block, output)
            if block.name == "todo_write":
                use_todo = True
            results.append({
                "type":"tool_result",
                "tool_use_id":block.id,
                "content":str(output), 
            })
        round_since_todo = 0 if use_todo else round_since_todo +1
        if round_since_todo >= 3:
            results.append({
                "type": "text",
                "text": "<reminder>Update your todos</reminder>"
            })
        
        messages.append(
            {"role":"user", "content":results}
        )


if __name__ == "__main__":
    history = []
    while True:
        messages = input("消息：").strip()
        history.append({"role":"user", "content":messages})
        trigger_hook("UserPromptSubmit", messages)
        agent_loop(history)
        for block in history[-1]["content"]:
            if getattr(block, "type", None) == "text":
                print(block.text)