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
import httpx

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
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            clickup_client = clickup.ClickUpAPI(api_key)
            # Test the connection
            await clickup_client.get_authorized_user()
            return
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                raise RuntimeError(f"Failed to initialize ClickUp client after {max_retries} attempts: {str(e)}")
            await asyncio.sleep(1)  # Wait before retrying

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
        ),
        types.Tool(
            name="get-spaces",
            description="Get all spaces in a team",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="get-lists",
            description="Get all lists in a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string"}
                },
                "required": ["space_id"]
            }
        ),
        types.Tool(
            name="get-tasks",
            description="Get tasks from a list",
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
                    "include_closed": {"type": "boolean", "optional": True},
                    "assignees": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "due_date_gt": {"type": "integer", "optional": True},
                    "due_date_lt": {"type": "integer", "optional": True},
                    "date_created_gt": {"type": "integer", "optional": True},
                    "date_created_lt": {"type": "integer", "optional": True},
                    "date_updated_gt": {"type": "integer", "optional": True},
                    "date_updated_lt": {"type": "integer", "optional": True}
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
                    "time_estimate": {"type": "integer", "optional": True},
                    "assignees": {"type": "array", "items": {"type": "integer"}, "optional": True},
                    "archived": {"type": "boolean", "optional": True}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="get-task-watchers",
            description="Get watchers of a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="add-task-watcher",
            description="Add a watcher to a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "watcher_id": {"type": "string"}
                },
                "required": ["task_id", "watcher_id"]
            }
        ),
        types.Tool(
            name="get-task-dependencies",
            description="Get dependencies of a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
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
                    "assignee": {"type": "integer", "optional": True},
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
        ),
        types.Tool(
            name="edit-checklist",
            description="Edit a checklist",
            inputSchema={
                "type": "object",
                "properties": {
                    "checklist_id": {"type": "string"},
                    "name": {"type": "string"}
                },
                "required": ["checklist_id", "name"]
            }
        ),
        types.Tool(
            name="delete-checklist",
            description="Delete a checklist",
            inputSchema={
                "type": "object",
                "properties": {
                    "checklist_id": {"type": "string"}
                },
                "required": ["checklist_id"]
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
                    "assignee": {"type": "integer", "optional": True},
                    "due_date": {"type": "integer", "optional": True}
                },
                "required": ["checklist_id", "name"]
            }
        ),
        types.Tool(
            name="stop-time-entry",
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
            name="get-time-entries",
            description="Get time entries within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "start_date": {"type": "integer", "optional": True},
                    "end_date": {"type": "integer", "optional": True},
                    "assignee": {"type": "integer", "optional": True},
                    "include_task_tags": {"type": "boolean", "optional": True},
                    "include_location_names": {"type": "boolean", "optional": True},
                    "space_id": {"type": "string", "optional": True},
                    "folder_id": {"type": "string", "optional": True},
                    "list_id": {"type": "string", "optional": True},
                    "task_id": {"type": "string", "optional": True},
                    "custom_task_ids": {"type": "boolean", "optional": True}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="get-time-entry-history",
            description="Get time entry history",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "timer_id": {"type": "string"}
                },
                "required": ["team_id", "timer_id"]
            }
        ),
        types.Tool(
            name="get-single-time-entry",
            description="Get a single time entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "time_entry_id": {"type": "string"}
                },
                "required": ["team_id", "time_entry_id"]
            }
        ),
        types.Tool(
            name="get-running-time-entry",
            description="Get currently running time entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="update-time-entry",
            description="Update a time entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "timer_id": {"type": "string"},
                    "description": {"type": "string", "optional": True},
                    "start": {"type": "integer", "optional": True},
                    "duration": {"type": "integer", "optional": True},
                    "billable": {"type": "boolean", "optional": True},
                    "tags": {"type": "array", "items": {"type": "string"}, "optional": True}
                },
                "required": ["team_id", "timer_id"]
            }
        ),
        types.Tool(
            name="delete-time-entry",
            description="Delete a time entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "time_entry_id": {"type": "string"}
                },
                "required": ["team_id", "time_entry_id"]
            }
        ),
        types.Tool(
            name="get-time-entry-tags",
            description="Get all tags from time entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="add-tags-to-time-entries",
            description="Add tags to time entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "time_entry_ids": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "object", "properties": {
                        "name": {"type": "string"},
                        "tag_bg": {"type": "string", "optional": True},
                        "tag_fg": {"type": "string", "optional": True}
                    }}}
                },
                "required": ["team_id", "time_entry_ids", "tags"]
            }
        ),
        types.Tool(
            name="remove-tags-from-time-entries",
            description="Remove tags from time entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "time_entry_ids": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "object", "properties": {
                        "name": {"type": "string"}
                    }}}
                },
                "required": ["team_id", "time_entry_ids", "tags"]
            }
        ),
        types.Tool(
            name="update-time-entry-tag",
            description="Update a time entry tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "tag_bg": {"type": "string"},
                    "tag_fg": {"type": "string"}
                },
                "required": ["team_id", "name", "new_name", "tag_bg", "tag_fg"]
            }
        ),
        types.Tool(
            name="edit-guest",
            description="Edit a guest's permissions",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "guest_id": {"type": "string"},
                    "can_edit_tags": {"type": "boolean", "optional": True},
                    "can_see_time_estimated": {"type": "boolean", "optional": True},
                    "can_see_time_spent": {"type": "boolean", "optional": True}
                },
                "required": ["team_id", "guest_id"]
            }
        ),
        types.Tool(
            name="remove-guest",
            description="Remove a guest from workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "guest_id": {"type": "string"}
                },
                "required": ["team_id", "guest_id"]
            }
        ),
        types.Tool(
            name="get-guest",
            description="Get guest information",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "guest_id": {"type": "string"}
                },
                "required": ["team_id", "guest_id"]
            }
        ),
        types.Tool(
            name="add-guest-to-task",
            description="Add a guest to a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "guest_id": {"type": "string"},
                    "permission_level": {"type": "string"}
                },
                "required": ["task_id", "guest_id", "permission_level"]
            }
        ),
        types.Tool(
            name="remove-guest-from-task",
            description="Remove a guest from a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "guest_id": {"type": "string"}
                },
                "required": ["task_id", "guest_id"]
            }
        ),
        types.Tool(
            name="add-guest-to-list",
            description="Add a guest to a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "guest_id": {"type": "string"},
                    "permission_level": {"type": "string"}
                },
                "required": ["list_id", "guest_id", "permission_level"]
            }
        ),
        types.Tool(
            name="remove-guest-from-list",
            description="Remove a guest from a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "guest_id": {"type": "string"}
                },
                "required": ["list_id", "guest_id"]
            }
        ),
        types.Tool(
            name="add-guest-to-folder",
            description="Add a guest to a folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string"},
                    "guest_id": {"type": "string"},
                    "permission_level": {"type": "string"}
                },
                "required": ["folder_id", "guest_id", "permission_level"]
            }
        ),
        types.Tool(
            name="remove-guest-from-folder",
            description="Remove a guest from a folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string"},
                    "guest_id": {"type": "string"}
                },
                "required": ["folder_id", "guest_id"]
            }
        ),
        types.Tool(
            name="create-team-view",
            description="Create a team view",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "parent": {"type": "string", "optional": True}
                },
                "required": ["team_id", "name", "type"]
            }
        ),
        types.Tool(
            name="create-team-group",
            description="Create a team (user group)",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "name": {"type": "string"},
                    "member_ids": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["team_id", "name", "member_ids"]
            }
        ),
        types.Tool(
            name="get-team-groups",
            description="Get teams (user groups)",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="update-team-group",
            description="Update a team (user group)",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string"},
                    "name": {"type": "string", "optional": True},
                    "member_ids": {"type": "array", "items": {"type": "integer"}, "optional": True}
                },
                "required": ["group_id"]
            }
        ),
        types.Tool(
            name="delete-team-group",
            description="Delete a team (user group)",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string"}
                },
                "required": ["group_id"]
            }
        ),
        types.Tool(
            name="get-workspace-seats",
            description="Get workspace seats",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"}
                },
                "required": ["workspace_id"]
            }
        ),
        types.Tool(
            name="get-task-templates",
            description="Get task templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "page": {"type": "integer", "optional": True}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="create-task-from-template",
            description="Create a task from a template",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "template_id": {"type": "string"},
                    "name": {"type": "string"}
                },
                "required": ["list_id", "template_id", "name"]
            }
        ),
        types.Tool(
            name="invite-user",
            description="Invite a user to a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "email": {"type": "string"},
                    "admin": {"type": "boolean", "optional": True},
                    "custom_role_id": {"type": "integer", "optional": True}
                },
                "required": ["team_id", "email"]
            }
        ),
        types.Tool(
            name="edit-user",
            description="Edit a user in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "user_id": {"type": "integer"},
                    "username": {"type": "string", "optional": True},
                    "email": {"type": "string", "optional": True},
                    "color": {"type": "string", "optional": True},
                    "initials": {"type": "string", "optional": True},
                    "role": {"type": "integer", "optional": True}
                },
                "required": ["team_id", "user_id"]
            }
        ),
        types.Tool(
            name="remove-user",
            description="Remove a user from a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "user_id": {"type": "integer"}
                },
                "required": ["team_id", "user_id"]
            }
        ),
        types.Tool(
            name="get-user",
            description="Get user information",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "user_id": {"type": "integer"}
                },
                "required": ["team_id", "user_id"]
            }
        ),
        types.Tool(
            name="create-webhook",
            description="Create a webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "endpoint": {"type": "string"},
                    "events": {"type": "array", "items": {"type": "string"}},
                    "space_id": {"type": "string", "optional": True},
                    "list_id": {"type": "string", "optional": True},
                    "task_id": {"type": "string", "optional": True},
                    "health_check_url": {"type": "string", "optional": True}
                },
                "required": ["team_id", "endpoint", "events"]
            }
        ),
        types.Tool(
            name="get-webhooks",
            description="Get webhooks",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"}
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="update-webhook",
            description="Update a webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "webhook_id": {"type": "string"},
                    "endpoint": {"type": "string", "optional": True},
                    "events": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "space_id": {"type": "string", "optional": True},
                    "list_id": {"type": "string", "optional": True},
                    "task_id": {"type": "string", "optional": True},
                    "health_check_url": {"type": "string", "optional": True},
                    "status": {"type": "string", "optional": True}
                },
                "required": ["webhook_id"]
            }
        ),
        types.Tool(
            name="delete-webhook",
            description="Delete a webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "webhook_id": {"type": "string"}
                },
                "required": ["webhook_id"]
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

    # Spaces endpoints
    elif name == "get-spaces":
        if not arguments:
            raise ValueError("Missing arguments")
        spaces = await clickup_client.get_spaces(arguments["team_id"])
        spaces_text = "\n".join([
            f"- {space.get('name', 'Unknown')} (ID: {space.get('id', 'Unknown')})"
            for space in spaces
        ])
        return [types.TextContent(
            type="text",
            text=f"Available spaces:\n{spaces_text}"
        )]

    elif name == "get-lists":
        if not arguments:
            raise ValueError("Missing arguments")
        lists = await clickup_client.get_lists(arguments["space_id"])
        lists_text = "\n".join([
            f"- {lst.get('name', 'Unknown')} (ID: {lst.get('id', 'Unknown')})"
            for lst in lists
        ])
        return [types.TextContent(
            type="text",
            text=f"Available lists:\n{lists_text}"
        )]

    # Tasks endpoints
    elif name == "get-tasks":
        if not arguments:
            raise ValueError("Missing arguments")
        tasks = await clickup_client.get_tasks(arguments["list_id"], **{k: v for k, v in arguments.items() if k != "list_id"})
        tasks_text = "\n".join([
            f"- {task.get('name', 'Unknown')} (ID: {task.get('id', 'Unknown')})"
            for task in tasks
        ])
        return [types.TextContent(
            type="text",
            text=f"Tasks:\n{tasks_text}"
        )]

    elif name == "update-task":
        if not arguments:
            raise ValueError("Missing arguments")
        task_id = arguments.pop("task_id")
        task = await clickup_client.update_task(task_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Updated task: {task.get('name', 'Unknown')} (ID: {task.get('id', 'Unknown')})"
        )]

    elif name == "get-task-watchers":
        if not arguments:
            raise ValueError("Missing arguments")
        watchers = await clickup_client.get_task_watchers(arguments["task_id"])
        watchers_text = "\n".join([
            f"- {watcher.get('username', 'Unknown')} (ID: {watcher.get('id', 'Unknown')})"
            for watcher in watchers
        ])
        return [types.TextContent(
            type="text",
            text=f"Task watchers:\n{watchers_text}"
        )]

    elif name == "add-task-watcher":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.add_task_watcher(
            task_id=arguments["task_id"],
            watcher_id=arguments["watcher_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Added watcher to task"
        )]

    elif name == "get-task-dependencies":
        if not arguments:
            raise ValueError("Missing arguments")
        dependencies = await clickup_client.get_task_dependencies(arguments["task_id"])
        deps_text = "\n".join([
            f"- {dep.get('task_id', 'Unknown')} ({dep.get('type', 'Unknown')})"
            for dep in dependencies
        ])
        return [types.TextContent(
            type="text",
            text=f"Task dependencies:\n{deps_text}"
        )]

    elif name == "remove-task-dependency":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_task_dependency(
            task_id=arguments["task_id"],
            dependency_id=arguments["dependency_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed task dependency"
        )]

    # Comments endpoints
    elif name == "get-comments":
        if not arguments:
            raise ValueError("Missing arguments")
        comments = await clickup_client.get_comments(arguments["task_id"])
        comments_text = "\n".join([
            f"- {comment.get('comment_text', 'No text')} (ID: {comment.get('id', 'Unknown')})"
            for comment in comments
        ])
        return [types.TextContent(
            type="text",
            text=f"Task comments:\n{comments_text}"
        )]

    elif name == "update-comment":
        if not arguments:
            raise ValueError("Missing arguments")
        comment_id = arguments.pop("comment_id")
        comment_text = arguments.pop("comment_text")
        result = await clickup_client.update_comment(
            comment_id=comment_id,
            comment_text=comment_text,
            **arguments
        )
        return [types.TextContent(
            type="text",
            text=f"Updated comment"
        )]

    elif name == "delete-comment":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.delete_comment(arguments["comment_id"])
        return [types.TextContent(
            type="text",
            text=f"Deleted comment"
        )]

    # Checklists endpoints
    elif name == "edit-checklist":
        if not arguments:
            raise ValueError("Missing arguments")
        checklist = await clickup_client.edit_checklist(
            checklist_id=arguments["checklist_id"],
            name=arguments["name"]
        )
        return [types.TextContent(
            type="text",
            text=f"Updated checklist: {checklist.get('name', 'Unknown')} (ID: {checklist.get('id', 'Unknown')})"
        )]

    elif name == "delete-checklist":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.delete_checklist(arguments["checklist_id"])
        return [types.TextContent(
            type="text",
            text=f"Deleted checklist"
        )]

    elif name == "create-checklist-item":
        if not arguments:
            raise ValueError("Missing arguments")
        checklist_id = arguments.pop("checklist_id")
        name = arguments.pop("name")
        item = await clickup_client.create_checklist_item(
            checklist_id=checklist_id,
            name=name,
            **arguments
        )
        return [types.TextContent(
            type="text",
            text=f"Created checklist item: {item.get('name', 'Unknown')} (ID: {item.get('id', 'Unknown')})"
        )]

    # Time tracking endpoints
    elif name == "stop-time-entry":
        if not arguments:
            raise ValueError("Missing arguments")
        entry = await clickup_client.stop_time_entry(arguments["task_id"])
        return [types.TextContent(
            type="text",
            text=f"Stopped time entry: {entry.get('id', 'Unknown')}"
        )]

    elif name == "get-time-entries":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        entries = await clickup_client.get_time_entries(team_id, **arguments)
        entries_text = "\n".join([
            f"- {entry.get('description', 'No description')} ({entry.get('duration', 0)} seconds)"
            for entry in entries
        ])
        return [types.TextContent(
            type="text",
            text=f"Time entries:\n{entries_text}"
        )]

    elif name == "get-time-entry-history":
        if not arguments:
            raise ValueError("Missing arguments")
        history = await clickup_client.get_time_entry_history(
            team_id=arguments["team_id"],
            timer_id=arguments["timer_id"]
        )
        history_text = "\n".join([
            f"- {entry.get('action', 'Unknown')} at {entry.get('date', 'Unknown')}"
            for entry in history
        ])
        return [types.TextContent(
            type="text",
            text=f"Time entry history:\n{history_text}"
        )]

    elif name == "get-single-time-entry":
        if not arguments:
            raise ValueError("Missing arguments")
        entry = await clickup_client.get_single_time_entry(
            team_id=arguments["team_id"],
            time_entry_id=arguments["time_entry_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Time entry: {entry.get('description', 'No description')} ({entry.get('duration', 0)} seconds)"
        )]

    elif name == "get-running-time-entry":
        if not arguments:
            raise ValueError("Missing arguments")
        entry = await clickup_client.get_running_time_entry(arguments["team_id"])
        if entry:
            return [types.TextContent(
                type="text",
                text=f"Running time entry: {entry.get('description', 'No description')} ({entry.get('duration', 0)} seconds)"
            )]
        else:
            return [types.TextContent(
                type="text",
                text="No running time entry found"
            )]

    elif name == "update-time-entry":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        timer_id = arguments.pop("timer_id")
        entry = await clickup_client.update_time_entry(
            team_id=team_id,
            timer_id=timer_id,
            **arguments
        )
        return [types.TextContent(
            type="text",
            text=f"Updated time entry: {entry.get('description', 'No description')} ({entry.get('duration', 0)} seconds)"
        )]

    elif name == "delete-time-entry":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.delete_time_entry(
            team_id=arguments["team_id"],
            time_entry_id=arguments["time_entry_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Deleted time entry"
        )]

    # Time Entry Tags endpoints
    elif name == "get-time-entry-tags":
        if not arguments:
            raise ValueError("Missing arguments")
        tags = await clickup_client.get_time_entry_tags(arguments["team_id"])
        tags_text = "\n".join([
            f"- {tag}"
            for tag in tags
        ])
        return [types.TextContent(
            type="text",
            text=f"Time entry tags:\n{tags_text}"
        )]

    elif name == "add-tags-to-time-entries":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.add_tags_to_time_entries(
            team_id=arguments["team_id"],
            time_entry_ids=arguments["time_entry_ids"],
            tags=arguments["tags"]
        )
        return [types.TextContent(
            type="text",
            text=f"Added tags to time entries"
        )]

    elif name == "remove-tags-from-time-entries":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_tags_from_time_entries(
            team_id=arguments["team_id"],
            time_entry_ids=arguments["time_entry_ids"],
            tags=arguments["tags"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed tags from time entries"
        )]

    elif name == "update-time-entry-tag":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.update_time_entry_tag(
            team_id=arguments["team_id"],
            name=arguments["name"],
            new_name=arguments["new_name"],
            tag_bg=arguments["tag_bg"],
            tag_fg=arguments["tag_fg"]
        )
        return [types.TextContent(
            type="text",
            text=f"Updated time entry tag"
        )]

    # Guest management endpoints
    elif name == "edit-guest":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        guest_id = arguments.pop("guest_id")
        guest = await clickup_client.edit_guest(team_id, guest_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Updated guest permissions"
        )]

    elif name == "remove-guest":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_guest(
            team_id=arguments["team_id"],
            guest_id=arguments["guest_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed guest from workspace"
        )]

    elif name == "get-guest":
        if not arguments:
            raise ValueError("Missing arguments")
        guest = await clickup_client.get_guest(
            team_id=arguments["team_id"],
            guest_id=arguments["guest_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Guest: {guest.get('email', 'Unknown')} (ID: {guest.get('id', 'Unknown')})"
        )]

    elif name == "add-guest-to-task":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.add_guest_to_task(
            task_id=arguments["task_id"],
            guest_id=arguments["guest_id"],
            permission_level=arguments["permission_level"]
        )
        return [types.TextContent(
            type="text",
            text=f"Added guest to task"
        )]

    elif name == "remove-guest-from-task":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_guest_from_task(
            task_id=arguments["task_id"],
            guest_id=arguments["guest_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed guest from task"
        )]

    elif name == "add-guest-to-list":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.add_guest_to_list(
            list_id=arguments["list_id"],
            guest_id=arguments["guest_id"],
            permission_level=arguments["permission_level"]
        )
        return [types.TextContent(
            type="text",
            text=f"Added guest to list"
        )]

    elif name == "remove-guest-from-list":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_guest_from_list(
            list_id=arguments["list_id"],
            guest_id=arguments["guest_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed guest from list"
        )]

    elif name == "add-guest-to-folder":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.add_guest_to_folder(
            folder_id=arguments["folder_id"],
            guest_id=arguments["guest_id"],
            permission_level=arguments["permission_level"]
        )
        return [types.TextContent(
            type="text",
            text=f"Added guest to folder"
        )]

    elif name == "remove-guest-from-folder":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_guest_from_folder(
            folder_id=arguments["folder_id"],
            guest_id=arguments["guest_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed guest from folder"
        )]

    # Views endpoints
    elif name == "create-team-view":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        view = await clickup_client.create_team_view(team_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Created team view: {view.get('name', 'Unknown')} (ID: {view.get('id', 'Unknown')})"
        )]

    # Teams endpoints
    elif name == "create-team-group":
        if not arguments:
            raise ValueError("Missing arguments")
        group = await clickup_client.create_team_group(
            team_id=arguments["team_id"],
            name=arguments["name"],
            member_ids=arguments["member_ids"]
        )
        return [types.TextContent(
            type="text",
            text=f"Created team group: {group.get('name', 'Unknown')} (ID: {group.get('id', 'Unknown')})"
        )]

    elif name == "get-team-groups":
        if not arguments:
            raise ValueError("Missing arguments")
        groups = await clickup_client.get_team_groups(arguments["team_id"])
        groups_text = "\n".join([
            f"- {group.get('name', 'Unknown')} (ID: {group.get('id', 'Unknown')})"
            for group in groups.get("groups", [])
        ])
        return [types.TextContent(
            type="text",
            text=f"Team groups:\n{groups_text}"
        )]

    elif name == "update-team-group":
        if not arguments:
            raise ValueError("Missing arguments")
        group_id = arguments.pop("group_id")
        group = await clickup_client.update_team_group(group_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Updated team group: {group.get('name', 'Unknown')} (ID: {group.get('id', 'Unknown')})"
        )]

    elif name == "delete-team-group":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.delete_team_group(arguments["group_id"])
        return [types.TextContent(
            type="text",
            text=f"Deleted team group"
        )]

    elif name == "get-workspace-seats":
        if not arguments:
            raise ValueError("Missing arguments")
        seats = await clickup_client.get_workspace_seats(arguments["workspace_id"])
        return [types.TextContent(
            type="text",
            text=f"Workspace seats: {seats}"
        )]

    # Task Templates endpoints
    elif name == "get-task-templates":
        if not arguments:
            raise ValueError("Missing arguments")
        templates = await clickup_client.get_task_templates(
            team_id=arguments["team_id"],
            page=arguments.get("page", 0)
        )
        templates_text = "\n".join([
            f"- {template.get('name', 'Unknown')} (ID: {template.get('id', 'Unknown')})"
            for template in templates
        ])
        return [types.TextContent(
            type="text",
            text=f"Task templates:\n{templates_text}"
        )]

    elif name == "create-task-from-template":
        if not arguments:
            raise ValueError("Missing arguments")
        task = await clickup_client.create_task_from_template(
            list_id=arguments["list_id"],
            template_id=arguments["template_id"],
            name=arguments["name"]
        )
        return [types.TextContent(
            type="text",
            text=f"Created task from template: {task.get('name', 'Unknown')} (ID: {task.get('id', 'Unknown')})"
        )]

    # User management endpoints
    elif name == "invite-user":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        email = arguments.pop("email")
        user = await clickup_client.invite_user(team_id, email, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Invited user: {user.get('email', 'Unknown')}"
        )]

    elif name == "edit-user":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        user_id = arguments.pop("user_id")
        user = await clickup_client.edit_user(team_id, user_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Updated user: {user.get('username', 'Unknown')} (ID: {user.get('id', 'Unknown')})"
        )]

    elif name == "remove-user":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.remove_user(
            team_id=arguments["team_id"],
            user_id=arguments["user_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"Removed user from workspace"
        )]

    elif name == "get-user":
        if not arguments:
            raise ValueError("Missing arguments")
        user = await clickup_client.get_user(
            team_id=arguments["team_id"],
            user_id=arguments["user_id"]
        )
        return [types.TextContent(
            type="text",
            text=f"User: {user.get('username', 'Unknown')} (ID: {user.get('id', 'Unknown')})"
        )]

    # Webhook endpoints
    elif name == "create-webhook":
        if not arguments:
            raise ValueError("Missing arguments")
        team_id = arguments.pop("team_id")
        endpoint = arguments.pop("endpoint")
        events = arguments.pop("events")
        webhook = await clickup_client.create_webhook(team_id, endpoint, events, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Created webhook: {webhook.get('id', 'Unknown')}"
        )]

    elif name == "get-webhooks":
        if not arguments:
            raise ValueError("Missing arguments")
        webhooks = await clickup_client.get_webhooks(arguments["team_id"])
        webhooks_text = "\n".join([
            f"- {webhook.get('endpoint', 'Unknown')} (ID: {webhook.get('id', 'Unknown')})"
            for webhook in webhooks.get("webhooks", [])
        ])
        return [types.TextContent(
            type="text",
            text=f"Webhooks:\n{webhooks_text}"
        )]

    elif name == "update-webhook":
        if not arguments:
            raise ValueError("Missing arguments")
        webhook_id = arguments.pop("webhook_id")
        webhook = await clickup_client.update_webhook(webhook_id, **arguments)
        return [types.TextContent(
            type="text",
            text=f"Updated webhook: {webhook.get('id', 'Unknown')}"
        )]

    elif name == "delete-webhook":
        if not arguments:
            raise ValueError("Missing arguments")
        result = await clickup_client.delete_webhook(arguments["webhook_id"])
        return [types.TextContent(
            type="text",
            text=f"Deleted webhook"
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")
        
    # This should never be reached due to the else block above
    raise RuntimeError("Unexpected execution path")

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


