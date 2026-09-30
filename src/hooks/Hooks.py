'''
    包职责：定义各类hooks，并实现登记与触发函数
'''
import re
from config import WORKDIR
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



def register_hook(event:str, callback):
    HOOKS[event].append(callback)

def trigger_hook(event: str, *args) -> str | None:
    for callback in HOOKS.get(event):
        output = callback(*args)
        if output:
            return output
    return None

# Permission Hooks
DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if="]
DESTRUCTIVE_COMMAND_WORD = re.compile(
    r"(?i)(?:^|[;&|()\n])\s*(?:rm|del)(?=\s|$|[;&|()])"
)
DESTRUCTIVE = ["rm ", "> /etc/", "chmod 777"]
def contains_destructive_command(command: str) -> bool:
    return bool(DESTRUCTIVE_COMMAND_WORD.search(command))

def permission_hook(block) -> str:
    '''
        event: PreToolUse
        功能：检查工具调用中命令是否越权
        具体内容
            检查bash:
                1.严令禁止的命令，无需审查，直接拒绝
                2.可询问用户的命令
            检查read/write/edit操作：
                1.检查路径是否越工作区
                2.询问用户越区操作是否执行
        触发场景：
            如果返回字符串 -> 阻止工具调用
            如果返回None/不返回值 -> 允许工具调用
    '''      
    # 对命令进行处理   
    if block.name == "bash":
        command = block.input.get("command", "")
        for pattern in DENY_LIST:
            if pattern in command:
                print(f"\n[blocked] {pattern}")
                return "Permission denied by deny list"
        if contains_destructive_command(command) or any(
            kw in command for kw in DESTRUCTIVE
        ):
            print(f"[通行提示] 存在有潜在破坏性的代码")
            print(f"    Tool: {block.name} {block.input}")
            choice = input("    Allow? [y/N] ").strip().lower()
            if choice not in ("y", "yes"):
                return "用户不允许执行该命令"
    # 对路径进行处理
    if block.name in ["read_file", "write_file", "edit_file"]:
        path = block.input.get("path", "")
        if not (WORKDIR / path).resolve.is_relative_to(WORKDIR):
            print(f"[通行提示] 操作超出工作区")
            choice = input("    允许？[y/N]").strip().lower()
            if not choice in ["yes", "y"]:
                return "用户不允许超出工作区的文件读写操作"
    return None

# 将主循环“打印”命令职责转移到log_hook函数
def log_hook(block):
    '''PreToolUse: 记录每次工具调用'''
    args_preview = str(list(block.input.valuse())[:2])[:60]
    print(f"[钩子] {block.name}({args_preview})")
    return None

def large_out_put(block, output):
    '''PostToolUse: 对超出文本量输出进行提示'''
    if len(str(output)) > 100000:
        print(f"[钩子] {block.name}输出了 {len(str(output))} 字符 ")
    return None

def context_inject_hook(query):
    '''提醒用户Agent在哪里工作，query无实际调用处，仅作钩子匹配用'''
    print(f"[钩子] 在{WORKDIR}中工作")
    return None

def summary_hook(messages: list):
    '''总结工具调用次数'''
    tool_count = sum(1 for m in messages
        for b in (m.get("content", "") if isinstance(m.get("content"), list) else [])
        if isinstance(b, dict) and b.get("type") == "tool_result")
    print(f"[HOOK] Stop: 对话进行了{tool_count}次工具调用")
    return None

register_hook("UserPromptSubmit", context_inject_hook)
register_hook("PreToolUse", log_hook)
register_hook("PreToolUse", permission_hook)
register_hook("PostToolUse", large_out_put)
register_hook("Stop", summary_hook)