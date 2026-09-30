class TodoManager:
    def __init__(self):
        # 模型可看到的内容
        self.items: list[dict] = []

    def update(self, todos: list | str)->str:
        #
        if isinstance(todos, str):
            try:
                todos = json.loads(todos)
            except json.JSONDecodeError:
                todos = ast.literal_eval(todos)
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
        # lines -> 终端给用户的内容
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

