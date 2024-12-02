import httpx
from typing import Optional, List, Dict, Any, Union

class ClickUpAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        self._setup_client()
    
    def _setup_client(self):
        """Setup the HTTP client with proper timeout and retry settings"""
        timeout = httpx.Timeout(30.0, connect=10.0)  # 30s timeout, 10s connect timeout
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=timeout,
            limits=limits
        )
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get all accessible teams/workspaces"""
        response = await self.client.get(f"{self.base_url}/team")
        response.raise_for_status()
        return response.json()["teams"]
    
    async def get_spaces(self, team_id: str):
        """Get spaces in a team"""
        response = await self.client.get(f"{self.base_url}/team/{team_id}/space")
        response.raise_for_status()
        return response.json()["spaces"]
    
    async def create_space(self, team_id: str, name: str, **kwargs):
        """Create a space"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/space",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def get_lists(self, space_id: str):
        """Get lists in a space"""
        response = await self.client.get(f"{self.base_url}/space/{space_id}/list")
        response.raise_for_status()
        return response.json()["lists"]
    
    async def create_list(self, space_id: str, name: str, **kwargs):
        """Create a list"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/space/{space_id}/list",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def create_task(self, list_id: str, name: str, **kwargs):
        """Create a task"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/list/{list_id}/task",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def get_tasks(self, list_id: str, **kwargs):
        """Get tasks from a list"""
        response = await self.client.get(
            f"{self.base_url}/list/{list_id}/task",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()["tasks"]
    
    async def update_task(self, task_id: str, **kwargs):
        """Update a task"""
        response = await self.client.put(
            f"{self.base_url}/task/{task_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    async def create_task_comment(self, task_id: str, comment_text: str, **kwargs):
        """Create a comment on a task"""
        data = {"comment_text": comment_text, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/task/{task_id}/comment",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def start_time_entry(self, task_id: str, **kwargs):
        """Start time tracking for a task"""
        response = await self.client.post(
            f"{self.base_url}/task/{task_id}/time",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    async def stop_time_entry(self, task_id: str, **kwargs):
        """Stop time tracking for a task"""
        response = await self.client.put(
            f"{self.base_url}/task/{task_id}/time",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    async def get_accessible_custom_fields(self, list_id: str):
        """Get custom fields accessible in a list"""
        response = await self.client.get(
            f"{self.base_url}/list/{list_id}/field"
        )
        response.raise_for_status()
        return response.json()["fields"]
    
    async def create_checklist(self, task_id: str, name: str):
        """Create a checklist in a task"""
        response = await self.client.post(
            f"{self.base_url}/task/{task_id}/checklist",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()
    
    async def edit_checklist(self, checklist_id: str, name: str):
        """Edit a checklist"""
        response = await self.client.put(
            f"{self.base_url}/checklist/{checklist_id}",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_checklist(self, checklist_id: str):
        """Delete a checklist"""
        response = await self.client.delete(f"{self.base_url}/checklist/{checklist_id}")
        response.raise_for_status()
        return response.json()
    
    async def create_checklist_item(self, checklist_id: str, name: str, **kwargs):
        """Create an item in a checklist"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/checklist/{checklist_id}/checklist_item",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def get_space_tags(self, space_id: str):
        """Get all tags in a space"""
        response = await self.client.get(f"{self.base_url}/space/{space_id}/tag")
        response.raise_for_status()
        return response.json()["tags"]
    
    async def create_space_tag(self, space_id: str, name: str, **kwargs):
        """Create a new tag in a space"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/space/{space_id}/tag",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def get_task_watchers(self, task_id: str):
        """Get task watchers"""
        response = await self.client.get(f"{self.base_url}/task/{task_id}/watching")
        response.raise_for_status()
        return response.json()["watchers"]
    
    async def add_task_watcher(self, task_id: str, watcher_id: str):
        """Add a watcher to a task"""
        response = await self.client.post(
            f"{self.base_url}/task/{task_id}/watching",
            json={"watcher_id": watcher_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def add_task_dependency(self, task_id: str, depends_on: str, dependency_type: str = "waiting_on") -> dict:
        """Add a dependency to a task."""
        data = {
            "depends_on": depends_on,
            "dependency_type": dependency_type
        }
        response = await self.client.post(f"{self.base_url}/task/{task_id}/dependency", json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_task_dependencies(self, task_id: str) -> dict:
        """Get dependencies for a task."""
        response = await self.client.get(f"{self.base_url}/task/{task_id}/dependency")
        response.raise_for_status()
        return response.json()["dependencies"]
    
    async def delete_comment(self, comment_id: str) -> dict:
        """Delete a comment."""
        response = await self.client.delete(f"{self.base_url}/comment/{comment_id}")
        response.raise_for_status()
        return response.json()
    
    async def get_comments(self, task_id: str) -> list:
        """Get comments for a task."""
        response = await self.client.get(f"{self.base_url}/task/{task_id}/comment")
        response.raise_for_status()
        return response.json()["comments"]
    
    async def update_comment(self, comment_id: str, comment_text: str, **kwargs) -> dict:
        """Update a comment."""
        data = {"comment_text": comment_text, **kwargs}
        response = await self.client.put(f"{self.base_url}/comment/{comment_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    async def remove_task_dependency(self, task_id: str, dependency_id: str) -> dict:
        """Remove a dependency from a task."""
        response = await self.client.delete(f"{self.base_url}/task/{task_id}/dependency/{dependency_id}")
        response.raise_for_status()
        return response.json()
    
    async def get_authorized_user(self):
        """Get information about the currently authorized user"""
        response = await self.client.get(f"{self.base_url}/user")
        response.raise_for_status()
        return response.json()["user"]

    async def create_folder(self, space_id: str, name: str, **kwargs):
        """Create a folder in a space"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/space/{space_id}/folder",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def create_folderless_list(self, space_id: str, name: str, **kwargs):
        """Create a list directly in a space without a folder"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/space/{space_id}/list",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def create_goal(self, team_id: str, name: str, **kwargs):
        """Create a goal in a team"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/goal",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def create_key_result(self, goal_id: str, name: str, **kwargs):
        """Create a key result for a goal"""
        data = {"name": name, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/goal/{goal_id}/key_result",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def invite_guest(self, team_id: str, email: str, **kwargs: Any) -> Dict[str, Any]:
        """Invite a guest to workspace"""
        data = {"email": email, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/guest",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def get_task_members(self, task_id: str) -> List[Dict[str, Any]]:
        """Get members of a task"""
        response = await self.client.get(
            f"{self.base_url}/task/{task_id}/member"
        )
        response.raise_for_status()
        return response.json()["members"]

    async def get_list_members(self, list_id: str) -> List[Dict[str, Any]]:
        """Get members of a list"""
        response = await self.client.get(
            f"{self.base_url}/list/{list_id}/member"
        )
        response.raise_for_status()
        return response.json()["members"]

    async def get_custom_roles(self, team_id: str) -> List[Dict[str, Any]]:
        """Get custom roles in a workspace"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/customRoles"
        )
        response.raise_for_status()
        return response.json()["roles"]

    async def get_task_templates(self, team_id: str, page: int = 0) -> List[Dict[str, Any]]:
        """Get task templates"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/taskTemplate",
            params={"page": page}
        )
        response.raise_for_status()
        return response.json()["templates"]

    async def create_task_from_template(self, list_id: str, template_id: str, name: str):
        """Create a task from a template"""
        response = await self.client.post(
            f"{self.base_url}/list/{list_id}/taskTemplate/{template_id}",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()

    async def get_time_entries(self, team_id: str, start_date: Optional[int] = None, end_date: Optional[int] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """Get time entries within a date range"""
        params = {k: v for k, v in kwargs.items()}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/time_entries",
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_time_entry_history(self, team_id: str, timer_id: str) -> List[Dict[str, Any]]:
        """Get time entry history"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/time_entries/{timer_id}/history"
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_single_time_entry(self, team_id: str, time_entry_id: str) -> Dict[str, Any]:
        """Get a single time entry"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/time_entries/{time_entry_id}"
        )
        response.raise_for_status()
        return response.json()

    async def get_running_time_entry(self, team_id: str) -> Dict[str, Any]:
        """Get currently running time entry"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/time_entries/current"
        )
        response.raise_for_status()
        return response.json()

    async def create_time_entry(self, team_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a time entry"""
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/time_entries",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def update_time_entry(self, team_id: str, timer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Update a time entry"""
        response = await self.client.put(
            f"{self.base_url}/team/{team_id}/time_entries/{timer_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def delete_time_entry(self, team_id: str, time_entry_id: str) -> Dict[str, Any]:
        """Delete a time entry"""
        response = await self.client.delete(
            f"{self.base_url}/team/{team_id}/time_entries/{time_entry_id}"
        )
        response.raise_for_status()
        return response.json()

    async def start_time_entry_v2(self, team_id: str, timer_id: str) -> Dict[str, Any]:
        """Start a time entry (v2)"""
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/time_entries/start/{timer_id}"
        )
        response.raise_for_status()
        return response.json()

    async def stop_time_entry_v2(self, team_id: str) -> Dict[str, Any]:
        """Stop current time entry (v2)"""
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/time_entries/stop"
        )
        response.raise_for_status()
        return response.json()

    # Time Entry Tags
    async def get_time_entry_tags(self, team_id: str) -> Dict[str, Any]:
        """Get all tags from time entries"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/time_entries/tags"
        )
        response.raise_for_status()
        return response.json()

    async def add_tags_to_time_entries(self, team_id: str, time_entry_ids: List[str], tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """Add tags to time entries"""
        data = {
            "time_entry_ids": time_entry_ids,
            "tags": tags
        }
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/time_entries/tags",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def remove_tags_from_time_entries(self, team_id: str, time_entry_ids: List[str], tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """Remove tags from time entries"""
        data = {
            "time_entry_ids": time_entry_ids,
            "tags": tags
        }
        response = await self.client.delete(
            f"{self.base_url}/team/{team_id}/time_entries/tags",
            params=data  # Changed from json to params for DELETE request
        )
        response.raise_for_status()
        return response.json()

    async def update_time_entry_tag(self, team_id: str, name: str, new_name: str, tag_bg: str, tag_fg: str) -> Dict[str, Any]:
        """Change tag names from time entries"""
        data = {
            "name": name,
            "new_name": new_name,
            "tag_bg": tag_bg,
            "tag_fg": tag_fg
        }
        response = await self.client.put(
            f"{self.base_url}/team/{team_id}/time_entries/tags",
            json=data
        )
        response.raise_for_status()
        return response.json()

    # Guests
    async def edit_guest(self, team_id: str, guest_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Edit a guest on workspace"""
        response = await self.client.put(
            f"{self.base_url}/team/{team_id}/guest/{guest_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def remove_guest(self, team_id: str, guest_id: str) -> Dict[str, Any]:
        """Remove a guest from workspace"""
        response = await self.client.delete(
            f"{self.base_url}/team/{team_id}/guest/{guest_id}"
        )
        response.raise_for_status()
        return response.json()

    async def get_guest(self, team_id: str, guest_id: str) -> Dict[str, Any]:
        """Get guest information"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/guest/{guest_id}"
        )
        response.raise_for_status()
        return response.json()

    async def add_guest_to_task(self, task_id: str, guest_id: str, permission_level: str) -> Dict[str, Any]:
        """Add a guest to a task"""
        data = {"permission_level": permission_level}
        response = await self.client.post(
            f"{self.base_url}/task/{task_id}/guest/{guest_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def remove_guest_from_task(self, task_id: str, guest_id: str) -> Dict[str, Any]:
        """Remove a guest from a task"""
        response = await self.client.delete(
            f"{self.base_url}/task/{task_id}/guest/{guest_id}"
        )
        response.raise_for_status()
        return response.json()

    async def add_guest_to_list(self, list_id: str, guest_id: str, permission_level: str) -> Dict[str, Any]:
        """Add a guest to a list"""
        data = {"permission_level": permission_level}
        response = await self.client.post(
            f"{self.base_url}/list/{list_id}/guest/{guest_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def remove_guest_from_list(self, list_id: str, guest_id: str) -> Dict[str, Any]:
        """Remove a guest from a list"""
        response = await self.client.delete(
            f"{self.base_url}/list/{list_id}/guest/{guest_id}"
        )
        response.raise_for_status()
        return response.json()

    async def add_guest_to_folder(self, folder_id: str, guest_id: str, permission_level: str) -> Dict[str, Any]:
        """Add a guest to a folder"""
        data = {"permission_level": permission_level}
        response = await self.client.post(
            f"{self.base_url}/folder/{folder_id}/guest/{guest_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def remove_guest_from_folder(self, folder_id: str, guest_id: str) -> Dict[str, Any]:
        """Remove a guest from a folder"""
        response = await self.client.delete(
            f"{self.base_url}/folder/{folder_id}/guest/{guest_id}"
        )
        response.raise_for_status()
        return response.json()

    # Views
    async def create_team_view(self, team_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a team view"""
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/view",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    # Teams (User Groups)
    async def create_team_group(self, team_id: str, name: str, member_ids: List[int]) -> Dict[str, Any]:
        """Create a team (user group)"""
        data = {
            "name": name,
            "member_ids": member_ids
        }
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/group",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def get_team_groups(self, team_id: str) -> Dict[str, Any]:
        """Get teams (user groups)"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/group"
        )
        response.raise_for_status()
        return response.json()

    async def update_team_group(self, group_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Update a team (user group)"""
        response = await self.client.put(
            f"{self.base_url}/group/{group_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def delete_team_group(self, group_id: str) -> Dict[str, Any]:
        """Delete a team (user group)"""
        response = await self.client.delete(
            f"{self.base_url}/group/{group_id}"
        )
        response.raise_for_status()
        return response.json()

    # Teams (Workspaces)
    async def get_workspace_seats(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace seats"""
        response = await self.client.get(
            f"{self.base_url}/team/{workspace_id}/seats"
        )
        response.raise_for_status()
        return response.json()

    # Bulk Operations
    async def get_task_time_in_status(self, task_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Get task's time in status"""
        response = await self.client.get(
            f"{self.base_url}/task/{task_id}/time_in_status",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def get_bulk_tasks_time_in_status(self, task_ids: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Get bulk tasks' time in status"""
        task_ids_str = ",".join(task_ids)
        response = await self.client.get(
            f"{self.base_url}/task/bulk_time_in_status/{task_ids_str}",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    # Shared Hierarchy
    async def get_shared_hierarchy(self, team_id: str) -> Dict[str, Any]:
        """Get shared hierarchy"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/shared"
        )
        response.raise_for_status()
        return response.json()

    # Users
    async def invite_user(self, team_id: str, email: str, **kwargs: Any) -> Dict[str, Any]:
        """Invite a user to a workspace"""
        data = {"email": email, **kwargs}
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/user",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def edit_user(self, team_id: str, user_id: int, **kwargs: Any) -> Dict[str, Any]:
        """Edit a user in a workspace"""
        response = await self.client.put(
            f"{self.base_url}/team/{team_id}/user/{user_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def remove_user(self, team_id: str, user_id: int) -> Dict[str, Any]:
        """Remove a user from a workspace"""
        response = await self.client.delete(
            f"{self.base_url}/team/{team_id}/user/{user_id}"
        )
        response.raise_for_status()
        return response.json()

    async def get_user(self, team_id: str, user_id: int) -> Dict[str, Any]:
        """Get user information"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/user/{user_id}"
        )
        response.raise_for_status()
        return response.json()

    # Webhooks
    async def create_webhook(self, team_id: str, endpoint: str, events: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Create a webhook"""
        data = {
            "endpoint": endpoint,
            "events": events,
            **kwargs
        }
        response = await self.client.post(
            f"{self.base_url}/team/{team_id}/webhook",
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def get_webhooks(self, team_id: str) -> Dict[str, Any]:
        """Get webhooks"""
        response = await self.client.get(
            f"{self.base_url}/team/{team_id}/webhook"
        )
        response.raise_for_status()
        return response.json()

    async def update_webhook(self, webhook_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Update a webhook"""
        response = await self.client.put(
            f"{self.base_url}/webhook/{webhook_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook"""
        response = await self.client.delete(
            f"{self.base_url}/webhook/{webhook_id}"
        )
        response.raise_for_status()
        return response.json()

    async def __aenter__(self) -> "ClickUpAPI":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.client.aclose()