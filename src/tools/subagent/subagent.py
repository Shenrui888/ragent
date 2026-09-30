def run_subagent(prompt: str)->str:
    print("\n[子智能体启动]")
    messages = [
        {"role": "user", "content": prompt}
    ]
    for _ in range(30):
        response = client.messages.create(
            model=MODEL, system=SUB_SYSTEM, messages= messages,
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
    return "30轮子智能体调用完成"