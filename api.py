from __future__ import annotations
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from db_driver import AssistantDatabaseDriver
from livekit.agents import llm
import logging

logger = logging.getLogger("AssistantFnc")

class AssistantFnc:

    ai_functions = {}

    def __init__(self):
        """Initialize the Assistant Function context with database driver."""
        self.db = AssistantDatabaseDriver()
        logger.info("AssistantFnc initialized with database connection")

        for name in dir(self):
            method = getattr(self,name)
            if hasattr(method, '_is_ai_callable'):
                self.ai_functions[name] = method

    @llm.ai_callable()
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        user = self.db.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        return user

    @llm.ai_callable()
    def create_or_update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        return self.db.create_or_update_user(user_id, name, preferences)

    @llm.ai_callable()
    def save_conversation(
        self,
        user_id: str,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:

        try:
            self.db.save_conversation(user_id, query, response, context)
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    @llm.ai_callable()
    def get_recent_conversations(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:

        return self.db.get_recent_conversations(user_id, limit)

    @llm.ai_callable()
    def add_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: Literal["low", "medium", "high"] = "medium",
        category: Optional[str] = None
    ) -> int:

        # Convert string due_date to datetime if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
            except ValueError:
                logger.warning(f"Invalid date format for {due_date}, using None")

        return self.db.add_task(user_id, title, description, parsed_due_date, priority, category)

    @llm.ai_callable()
    def get_pending_tasks(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        return self.db.get_pending_tasks(user_id, category)

    @llm.ai_callable()
    def complete_task(self, task_id: int) -> bool:

        return self.db.complete_task(task_id)

    @llm.ai_callable()
    def add_contact(
        self,
        user_id: str,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        relationship: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:

        return self.db.add_contact(user_id, name, phone, email, relationship, notes)

    @llm.ai_callable()
    def get_contacts(
        self,
        user_id: str,
        name_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        return self.db.get_contacts(user_id, name_filter)

    @llm.ai_callable()
    def update_user_settings(
        self,
        user_id: str,
        setting_type: Literal["voice_settings", "notification_preferences", "privacy_settings"],
        settings: Dict[str, Any]
    ) -> bool:

        try:
            self.db.update_user_settings(user_id, setting_type, settings)
            return True
        except Exception as e:
            logger.error(f"Failed to update user settings: {e}")
            return False

    @llm.ai_callable()
    def get_user_settings(self, user_id: str) -> Dict[str, Any]:

        settings = self.db.get_user_settings(user_id)
        if not settings:
            return {"error": "Settings not found"}
        return settings

    @llm.ai_callable()
    def generate_summary(self, user_id: str) -> Dict[str, Any]:

        try:
            user = self.db.get_user(user_id)
            pending_tasks = self.db.get_pending_tasks(user_id)
            recent_convos = self.db.get_recent_conversations(user_id, 3)

            return {
                "user_name": user.get("name") if user else "User",
                "last_interaction": user.get("last_interaction") if user else None,
                "pending_task_count": len(pending_tasks),
                "upcoming_tasks": [t for t in pending_tasks if t.get("due_date") is not None][:3],
                "recent_interactions": recent_convos
            }
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {"error": f"Failed to generate summary: {str(e)}"}
