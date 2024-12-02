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
            name="get-authorized-user",
            description="Get information about the currently authorized user",
            inputSchema={
                "type": "object",
                "properties": {}
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
            name="create-folder",
            description="Create a new folder in a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"},
                    "name": {"type": "string"}
                },
                "required": ["space_id", "name"]
            }
        ),
        types.Tool(
            name="create-folderless-list",
            description="Create a list directly in a space without a folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"},
                    "name": {"type": "string"},
                    "content": {"type": "string", "optional": True},
                    "due_date": {"type": "integer", "optional": True},
                    "priority": {"type": "integer", "optional": True},
                    "assignee": {"type": "integer", "optional": True},
                    "status": {"type": "string", "optional": True}
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
                    "assignees": {"type": "array", "items": {"type": "integer"}, "optional": True},
                    "tags": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "status": {"type": "string", "optional": True},
                    "priority": {"type": "integer", "optional": True},
                    "due_date": {"type": "integer", "optional": True},
                    "time_estimate": {"type": "integer", "optional": True},
                    "notify_all": {"type": "boolean", "optional": True}
                },
                "required": ["list_id", "name"]
            }
        ),
        types.Tool(
            name="create-task-comment",
            description="Create a comment on a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "comment_text": {"type": "string"},
                    "assignee": {"type": "integer", "optional": True},
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
            name="get-custom-fields",
            description="Get accessible custom fields in a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"}
                },
                "required": ["list_id"]
            }
        ),
        types.Tool(
            name="start-time-entry",
            description="Start time tracking for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "description": {"type": "string", "optional": True},
                    "billable": {"type": "boolean", "optional": True}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="create-goal",
            description="Create a new goal in a team",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "name": {"type": "string"},
                    "due_date": {"type": "integer", "optional": True},
                    "description": {"type": "string", "optional": True},
                    "multiple_owners": {"type": "boolean", "optional": True},
                    "owners": {"type": "array", "items": {"type": "integer"}, "optional": True},
                    "color": {"type": "string", "optional": True}
                },
                "required": ["team_id", "name"]
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
            name="add-task-dependency",
            description="Add a dependency between tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "depends_on": {"type": "string"},
                    "dependency_type": {"type": "string", "optional": True}
                },
                "required": ["task_id", "depends_on"]
            }
        ),
        types.Tool(
            name="get-task-members",
            description="Get members assigned to a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="invite-guest",
            description="Invite a guest to a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "email": {"type": "string"},
                    "can_edit_tags": {"type": "boolean", "optional": True},
                    "can_see_time_estimated": {"type": "boolean", "optional": True},
                    "can_see_time_spent": {"type": "boolean", "optional": True}
                },
                "required": ["team_id", "email"]
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
            
    # Authorization endpoints
    if name == "get-authorized-user":
        user = await clickup_client.get_authorized_user()
        return [types.TextContent(
            type="text",
            text=f"Authorized user: {user['username']} (ID: {user['id']})"
        )]

    # Spaces endpoints
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

    # Folders endpoints
    elif name == "create-folder":
        if not arguments:
            raise ValueError("Missing arguments")
        folder = await clickup_client.create_folder(
            space_id=arguments["space_id"],
            name=arguments["name"]
        )
        return [types.TextContent(
            type="text",
            text=f"Created folder: {folder['name']} (ID: {folder['id']})"
        )]

    # Lists endpoints
    elif name == "create-folderless-list":
        if not arguments:
            raise ValueError("Missing arguments")
        lst = await clickup_client.create_folderless_list(
            space_id=arguments["space_id"],
            name=arguments["name"],
            content=arguments.get("content"),
            due_date=arguments.get("due_date"),
            priority=arguments.get("priority"),
            assignee=arguments.get("assignee"),
            status=arguments.get("status")
        )
        return [types.TextContent(
            type="text",
            text=f"Created list: {lst['name']} (ID: {lst['id']})"
        )]

    # Tasks endpoints
    elif name == "create-task":
        if not arguments:
            raise ValueError("Missing arguments")
        task = await clickup_client.create_task(
            list_id=arguments["list_id"],
            name=arguments["name"],
            description=arguments.get("description"),
            assignees=arguments.get("assignees", []),
            tags=arguments.get("tags", []),
            status=arguments.get("status"),
            priority=arguments.get("priority"),
            due_date=arguments.get("due_date"),
            time_estimate=arguments.get("time_estimate"),
            notify_all=arguments.get("notify_all", False)
        )
        return [types.TextContent(
            type="text",
            text=f"Created task: {task['name']} (ID: {task['id']})"
        )]

    # Comments endpoints
    elif name == "create-task-comment":
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
            text=f"Created comment: {comment['id']}"
        )]

    # Checklists endpoints
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

    # Custom fields endpoints
    elif name == "get-custom-fields":
        if not arguments:
            raise ValueError("Missing arguments")
        fields = await clickup_client.get_accessible_custom_fields(arguments["list_id"])
        fields_text = "\n".join([
            f"- {field['name']} (Type: {field['type']}, ID: {field['id']})"
            for field in fields
        ])
        return [types.TextContent(
            type="text",
            text=f"Custom fields:\n{fields_text}"
        )]

    # Time tracking endpoints
    elif name == "start-time-entry":
        if not arguments:
            raise ValueError("Missing arguments")
        entry = await clickup_client.start_time_entry(
            task_id=arguments["task_id"],
            description=arguments.get("description"),
            billable=arguments.get("billable")
        )
        return [types.TextContent(
            type="text",
            text=f"Started time entry: {entry['id']}"
        )]

    # Goals endpoints
    elif name == "create-goal":
        if not arguments:
            raise ValueError("Missing arguments")
        goal = await clickup_client.create_goal(
            team_id=arguments["team_id"],
            name=arguments["name"],
            due_date=arguments.get("due_date"),
            description=arguments.get("description"),
            multiple_owners=arguments.get("multiple_owners"),
            owners=arguments.get("owners", []),
            color=arguments.get("color")
        )
        return [types.TextContent(
            type="text",
            text=f"Created goal: {goal['name']} (ID: {goal['id']})"
        )]

    # Tags endpoints
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

    # Dependencies endpoints
    elif name == "add-task-dependency":
        if not arguments:
            raise ValueError("Missing arguments")
        dependency = await clickup_client.add_task_dependency(
            task_id=arguments["task_id"],
            depends_on=arguments["depends_on"],
            dependency_type=arguments.get("dependency_type", "waiting_on")
        )
        return [types.TextContent(
            type="text",
            text=f"Added dependency: {dependency['id']}"
        )]

    # Members endpoints
    elif name == "get-task-members":
        if not arguments:
            raise ValueError("Missing arguments")
        members = await clickup_client.get_task_members(arguments["task_id"])
        members_text = "\n".join([
            f"- {member.get('username', 'Unknown')} (ID: {member.get('id', 'Unknown')})"
            for member in members
        ])
        return [types.TextContent(
            type="text",
            text=f"Task members:\n{members_text}"
        )]

    # Guests endpoints
    elif name == "invite-guest":
        if not arguments:
            raise ValueError("Missing arguments")
        guest = await clickup_client.invite_guest(
            team_id=arguments["team_id"],
            email=arguments["email"],
            can_edit_tags=arguments.get("can_edit_tags"),
            can_see_time_estimated=arguments.get("can_see_time_estimated"),
            can_see_time_spent=arguments.get("can_see_time_spent")
        )
        return [types.TextContent(
            type="text",
            text=f"Invited guest: {guest['email']}"
        )]

    # Teams endpoints
    elif name == "get-teams":
        teams = await clickup_client.get_teams()
        teams_text = "\n".join([
            f"- {team.get('name', 'Unknown')} (ID: {team.get('id', 'Unknown')})"
            for team in teams
        ])
        return [types.TextContent(
            type="text",
            text=f"Available teams:\n{teams_text}"
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


