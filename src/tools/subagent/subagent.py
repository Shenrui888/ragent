from anthropic import Anthropic
from tools.sub_tools import *
from config import SUB_MODEL, SUB_SYSTEM

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
def extract_text(content) -> str:
    if not isinstance(content, list):
        return str(content)
    return "\n".join(
        getattr(block, "text", "")
        for block in content
        if getattr(block, "type", None) == "text"
    )

def run_subagent(prompt: str)->str:
    print("\n[子智能体启动]")
    messages = [
        {"role": "user", "content": prompt}
    ]
    for _ in range(30):
        response = client.messages.create(
            model=SUB_MODEL, system=SUB_SYSTEM, messages= messages,
            max_tokens=8000, tools=SUB_TOOLS
        )
        messages.append(
            {"role": "assistant", "content": response.content}
        )
        tool_calls = [
            block for block in response.content if getattr(block, "type", "") == "tool_use"
        ]
        if not tool_calls:
            return extract_text(response.content) or "(no summary)"

        results = []
        for block in tool_calls:
            output = execute_tool(block, SUB_HANDLERS)
            print(f"[Sub]{block.name} {output[:100]}")
            results.append({
                "type": "tool_result",
                "tool_id": block.id,
                "content": output,
            })
        messages.append({
            "role": "user", "content": results
        })
    print("[子智能体结束]")
    return "子智能体调用完成"

SUBAGENT_TOOL = [
    {
        "name": "task",
        "description": "Run a subagent with fresh conversation context and return its final text.",
        "input_schema":
        {
            "type": "object",
            "properties": {"prompt": {"type": "string", "minLength": 1}},
            "required": ["prompt"],
        }
    }
]
SUBAGENT_HANDLER = {
    "task": run_subagent,
}