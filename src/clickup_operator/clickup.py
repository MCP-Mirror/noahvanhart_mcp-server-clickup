import httpx

class ClickUpAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers)
    
    async def get_teams(self):
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