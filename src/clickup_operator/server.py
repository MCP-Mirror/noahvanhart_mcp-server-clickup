import asyncio
from typing import Optional, Any, Sequence
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities
from mcp.server import Server
import mcp.server.stdio
from . import clickup
import os
from dotenv import load_dotenv

# Initialize server
app = Server("clickup-operator")
clickup_client: Optional[clickup.ClickUpAPI] = None

# Initialize client first
async def initialize():
    """Initialize the ClickUp client with API token from environment."""
    global clickup_client
    
    load_dotenv()
    api_key = os.getenv("CLICKUP_API_TOKEN")
    if not api_key:
        raise ValueError("CLICKUP_API_TOKEN environment variable not set")
    
    clickup_client = clickup.ClickUpAPI(api_key)

@app.list_tools()
async def list_tools():
    """List available tools for ClickUp operations."""
    return [
        types.Tool(
            name="get-teams",
            description="Get all accessible teams/workspaces",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get-spaces",
            description="Get spaces in a team/workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="create-space",
            description="Create a new space in a team",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "name": {"type": "string"},
                    "multiple_assignees": {"type": "boolean", "optional": True},
                    "features": {"type": "object", "optional": True}
                },
                "required": ["team_id", "name"]
            }
        ),
        types.Tool(
            name="get-lists",
            description="Get lists in a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"}
                },
                "required": ["space_id"]
            }
        ),
        types.Tool(
            name="create-list",
            description="Create a new list in a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"},
                    "name": {"type": "string"},
                    "content": {"type": "string", "optional": True},
                    "due_date": {"type": "integer", "optional": True},
                    "priority": {"type": "integer", "optional": True}
                },
                "required": ["space_id", "name"]
            }
        ),
        types.Tool(
            name="create-task",
            description="Create a new task in a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string", "optional": True},
                    "priority": {"type": "integer", "optional": True},
                    "due_date": {"type": "integer", "optional": True},
                    "assignees": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "tags": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "status": {"type": "string", "optional": True},
                    "notify_all": {"type": "boolean", "optional": True}
                },
                "required": ["list_id", "name"]
            }
        ),
        types.Tool(
            name="get-tasks",
            description="Get tasks in a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "archived": {"type": "boolean", "optional": True},
                    "page": {"type": "integer", "optional": True},
                    "order_by": {"type": "string", "optional": True},
                    "reverse": {"type": "boolean", "optional": True},
                    "subtasks": {"type": "boolean", "optional": True},
                    "statuses": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "assignees": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "includes": {"type": "array", "items": {"type": "string"}, "optional": True}
                },
                "required": ["list_id"]
            }
        ),
        types.Tool(
            name="update-task",
            description="Update a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "name": {"type": "string", "optional": True},
                    "description": {"type": "string", "optional": True},
                    "status": {"type": "string", "optional": True},
                    "priority": {"type": "integer", "optional": True},
                    "due_date": {"type": "integer", "optional": True},
                    "assignees": {"type": "array", "items": {"type": "string"}, "optional": True}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="start-time",
            description="Start time tracking for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "billable": {"type": "boolean", "optional": True}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="stop-time",
            description="Stop time tracking for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="get-custom-fields",
            description="Get custom fields accessible in a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"}
                },
                "required": ["list_id"]
            }
        ),
        types.Tool(
            name="create-comment",
            description="Create a comment on a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "comment_text": {"type": "string"},
                    "assignee": {"type": "string", "optional": True},
                    "notify_all": {"type": "boolean", "optional": True}
                },
                "required": ["task_id", "comment_text"]
            }
        ),
        types.Tool(
            name="create-checklist",
            description="Create a checklist in a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "name": {"type": "string"}
                },
                "required": ["task_id", "name"]
            }
        ),
        types.Tool(
            name="create-checklist-item",
            description="Create an item in a checklist",
            inputSchema={
                "type": "object",
                "properties": {
                    "checklist_id": {"type": "string"},
                    "name": {"type": "string"},
                    "assignee": {"type": "string", "optional": True},
                    "due_date": {"type": "string", "optional": True}
                },
                "required": ["checklist_id", "name"]
            }
        ),
        types.Tool(
            name="get-space-tags",
            description="Get all tags in a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"}
                },
                "required": ["space_id"]
            }
        ),
        types.Tool(
            name="create-space-tag",
            description="Create a new tag in a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"},
                    "name": {"type": "string"},
                    "tag_fg": {"type": "string", "optional": True},
                    "tag_bg": {"type": "string", "optional": True}
                },
                "required": ["space_id", "name"]
            }
        ),
        types.Tool(
            name="get-task-dependencies",
            description="Get task dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="add-task-dependency",
            description="Add a dependency to a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "depends_on": {"type": "string"},
                    "dependency_type": {"type": "string", "enum": ["blocks", "waiting_on"]}
                },
                "required": ["task_id", "depends_on"]
            }
        ),
        types.Tool(
            name="remove-task-dependency",
            description="Remove a dependency from a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "dependency_id": {"type": "string"}
                },
                "required": ["task_id", "dependency_id"]
            }
        ),
        types.Tool(
            name="get-comments",
            description="Get comments on a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="update-comment",
            description="Update a comment",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment_id": {"type": "string"},
                    "comment_text": {"type": "string"},
                    "assignee": {"type": "string", "optional": True},
                    "resolved": {"type": "boolean", "optional": True}
                },
                "required": ["comment_id", "comment_text"]
            }
        ),
        types.Tool(
            name="delete-comment",
            description="Delete a comment",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment_id": {"type": "string"}
                },
                "required": ["comment_id"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict[str, Any] | None
) -> Sequence[types.TextContent | types.ImageContent]:
    """Handle ClickUp tool execution requests."""
    global clickup_client
    
    # Initialize client if not already initialized
    if not clickup_client:
        await initialize()
        if not clickup_client:  # Double check initialization worked
            raise RuntimeError("Failed to initialize ClickUp client")
            
    if name == "get-teams":
        teams = await clickup_client.get_teams()
        teams_text = "\n".join([
            f"- {team['name']} (ID: {team['id']})"
            for team in teams
        ])
        return [types.TextContent(
            type="text",
            text=f"Available teams:\n{teams_text}"
        )]

    elif name == "get-spaces":
        if not arguments:
            raise ValueError("Missing arguments")
        spaces = await clickup_client.get_spaces(arguments["team_id"])
        spaces_text = "\n".join([
            f"- {space['name']} (ID: {space['id']})"
            for space in spaces
        ])
        return [types.TextContent(
            type="text",
            text=f"Spaces in team:\n{spaces_text}"
        )]

    elif name == "create-space":
        if not arguments:
            raise ValueError("Missing arguments")
        space = await clickup_client.create_space(
            team_id=arguments["team_id"],
            name=arguments["name"],
            multiple_assignees=arguments.get("multiple_assignees"),
            features=arguments.get("features", {})
        )
        return [types.TextContent(
            type="text",
            text=f"Created space: {space['name']} (ID: {space['id']})"
        )]

    elif name == "get-lists":
        if not arguments:
            raise ValueError("Missing arguments")
        lists = await clickup_client.get_lists(arguments["space_id"])
        lists_text = "\n".join([
            f"- {lst['name']} (ID: {lst['id']})"
            for lst in lists
        ])
        return [types.TextContent(
            type="text",
            text=f"Lists in space:\n{lists_text}"
        )]

    elif name == "create-list":
        if not arguments:
            raise ValueError("Missing arguments")
        lst = await clickup_client.create_list(
            space_id=arguments["space_id"],
            name=arguments["name"],
            content=arguments.get("content"),
            due_date=arguments.get("due_date"),
            priority=arguments.get("priority")
        )
        return [types.TextContent(
            type="text",
            text=f"Created list: {lst['name']} (ID: {lst['id']})"
        )]

    elif name == "create-task":
        if not arguments:
            raise ValueError("Missing arguments")
        task = await clickup_client.create_task(
            list_id=arguments["list_id"],
            name=arguments["name"],
            description=arguments.get("description"),
            priority=arguments.get("priority"),
            due_date=arguments.get("due_date"),
            assignees=arguments.get("assignees", []),
            tags=arguments.get("tags", []),
            status=arguments.get("status"),
            notify_all=arguments.get("notify_all", False)
        )
        return [types.TextContent(
            type="text",
            text=f"Created task: {task['name']} (ID: {task['id']})"
        )]

    elif name == "get-tasks":
        if not arguments:
            raise ValueError("Missing arguments")
        tasks = await clickup_client.get_tasks(
            list_id=arguments["list_id"],
            archived=arguments.get("archived", False),
            page=arguments.get("page"),
            order_by=arguments.get("order_by"),
            reverse=arguments.get("reverse"),
            subtasks=arguments.get("subtasks"),
            statuses=arguments.get("statuses", []),
            assignees=arguments.get("assignees", []),
            include=arguments.get("includes", [])
        )
        tasks_text = "\n".join([
            f"- {task['name']} (ID: {task['id']})"
            for task in tasks
        ])
        return [types.TextContent(
            type="text",
            text=f"Tasks in list:\n{tasks_text}"
        )]

    elif name == "update-task":
        if not arguments:
            raise ValueError("Missing arguments")
        task_id = arguments.pop("task_id")
        task = await clickup_client.update_task(task_id=task_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Updated task: {task['name']} (ID: {task['id']})"
        )]

    elif name == "start-time":
        if not arguments:
            raise ValueError("Missing arguments")
        time_entry = await clickup_client.start_time_entry(
            task_id=arguments["task_id"],
            billable=arguments.get("billable", False)
        )
        return [types.TextContent(
            type="text",
            text=f"Started time tracking for task {arguments['task_id']}"
        )]

    elif name == "stop-time":
        if not arguments:
            raise ValueError("Missing arguments")
        time_entry = await clickup_client.stop_time_entry(arguments["task_id"])
        return [types.TextContent(
            type="text",
            text=f"Stopped time tracking for task {arguments['task_id']}"
        )]

    elif name == "get-custom-fields":
        if not arguments:
            raise ValueError("Missing arguments")
        fields = await clickup_client.get_accessible_custom_fields(arguments["list_id"])
        fields_text = "\n".join([
            f"- {field['name']} ({field['type']})"
            for field in fields
        ])
        return [types.TextContent(
            type="text",
            text=f"Custom fields in list:\n{fields_text}"
        )]

    elif name == "create-comment":
        if not arguments:
            raise ValueError("Missing arguments")
        comment = await clickup_client.create_task_comment(
            task_id=arguments["task_id"],
            comment_text=arguments["comment_text"],
            assignee=arguments.get("assignee"),
            notify_all=arguments.get("notify_all", False)
        )
        return [types.TextContent(
            type="text",
            text=f"Created comment on task {arguments['task_id']}"
        )]

    elif name == "create-checklist":
        if not arguments:
            raise ValueError("Missing arguments")
        checklist = await clickup_client.create_checklist(
            task_id=arguments["task_id"],
            name=arguments["name"]
        )
        return [types.TextContent(
            type="text",
            text=f"Created checklist: {checklist['name']} (ID: {checklist['id']})"
        )]

    elif name == "create-checklist-item":
        if not arguments:
            raise ValueError("Missing arguments")
        item = await clickup_client.create_checklist_item(
            checklist_id=arguments["checklist_id"],
            name=arguments["name"],
            assignee=arguments.get("assignee"),
            due_date=arguments.get("due_date")
        )
        return [types.TextContent(
            type="text",
            text=f"Created checklist item: {item['name']}"
        )]

    elif name == "get-space-tags":
        if not arguments:
            raise ValueError("Missing arguments")
        tags = await clickup_client.get_space_tags(arguments["space_id"])
        tags_text = "\n".join([
            f"- {tag['name']}"
            for tag in tags
        ])
        return [types.TextContent(
            type="text",
            text=f"Tags in space:\n{tags_text}"
        )]

    elif name == "create-space-tag":
        if not arguments:
            raise ValueError("Missing arguments")
        tag = await clickup_client.create_space_tag(
            space_id=arguments["space_id"],
            name=arguments["name"],
            tag_fg=arguments.get("tag_fg"),
            tag_bg=arguments.get("tag_bg")
        )
        return [types.TextContent(
            type="text",
            text=f"Created tag: {tag['name']}"
        )]

    elif name == "get-task-dependencies":
        if not arguments:
            raise ValueError("Missing arguments")
        dependencies = await clickup_client.get_task_dependencies(arguments["task_id"])
        deps_text = "\n".join([
            f"- {dep['name']} (ID: {dep['id']})"
            for dep in dependencies
        ])
        return [types.TextContent(
            type="text",
            text=f"Dependencies for task:\n{deps_text}"
        )]

    elif name == "add-task-dependency":
        if not arguments:
            raise ValueError("Missing arguments")
        await clickup_client.add_task_dependency(
            task_id=arguments["task_id"],
            depends_on=arguments["depends_on"],
            dependency_type=arguments.get("dependency_type", "waiting_on")
        )
        return [types.TextContent(
            type="text",
            text=f"Added dependency to task {arguments['task_id']}"
        )]

    elif name == "remove-task-dependency":
        if not arguments:
            raise ValueError("Missing arguments")
        await clickup_client.remove_task_dependency(
            task_id=arguments["task_id"],
            dependency_id=arguments["dependency_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed dependency from task {arguments['task_id']}"
        )]

    elif name == "get-comments":
        if not arguments:
            raise ValueError("Missing arguments")
        comments = await clickup_client.get_comments(arguments["task_id"])
        comments_text = "\n".join([
            f"- {comment['comment_text']} (ID: {comment['id']})"
            for comment in comments
        ])
        return [types.TextContent(
            type="text",
            text=f"Comments on task:\n{comments_text}"
        )]

    elif name == "update-comment":
        if not arguments:
            raise ValueError("Missing arguments")
        comment = await clickup_client.update_comment(
            comment_id=arguments["comment_id"],
            comment_text=arguments["comment_text"],
            assignee=arguments.get("assignee"),
            resolved=arguments.get("resolved")
        )
        return [types.TextContent(
            type="text",
            text=f"Updated comment: {comment['id']}"
        )]

    elif name == "delete-comment":
        if not arguments:
            raise ValueError("Missing arguments")
        await clickup_client.delete_comment(arguments["comment_id"])
        return [types.TextContent(
            type="text",
            text=f"Deleted comment {arguments['comment_id']}"
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point for the server."""
    async with mcp.server.stdio.stdio_server() as (input_stream, output_stream):
        await app.run(
            input_stream,
            output_stream,
            InitializationOptions(
                server_name="clickup-operator",
                server_version="0.1.0",
                capabilities=ServerCapabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())


