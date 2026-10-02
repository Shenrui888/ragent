import json
import ast
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
                try:
                    todos = ast.literal_eval(todos)
                except (SyntaxError, ValueError) as e:
                    raise ValueError("todos must be a list or JSON array string") from e
        if not isinstance(todos, list):
            raise ValueError("todos must be a list")
        if len(todos) > 20:
            raise ValueError("Max 20 todos allowed")
        
        validate = []
        in_progress_count = 0
        for index, todo in enumerate(todos):
            if not isinstance(todo, dict):
                raise ValueError(f"todos[{index}] must be a dict")
            content = str(todo.get("content", "")).strip()
            status = str(todo.get("status", "pending")).lower()
            if not content:
                raise ValueError(f"todos[{index}] requires content")
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"todos[{index}] has invalid status '{status}")
            if status == "in_progress":
                in_progress_count += 1
            validate.append({
                "content":content, "status":status
            })

        if in_progress_count > 1:
            raise ValueError("Only one todo can be in_progress at a time")
        self.items = validate
        return self.render()

    def render(self)->str:
        if not self.items:
            return "No todos"
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

TODO = TodoManager()

def run_todo_write(todos: list | str) -> str:
    try:
        output = TODO.update(todos)
    except ValueError as e:
        return f"Error: {e}"
    print(f"\nCurrent Tasks\n{output}")
    return output

TASK_TOOL = [
    {"name": "todo_write", 
     "description": "Create and manage a task list for your current coding session.",
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
                                                "minLength": 1
                                            }, 
                                        "status": 
                                            {
                                                "type": "string", 
                                                "enum": ["pending", "in_progress", "completed"]
                                            }
                                    }, 
                                "required": ["content", "status"]
                            }
                    }
                }, 
            "required": ["todos"]
        }
    },
]
TASK_HANDLER = {
    "todo_write": run_todo_write
}