from __future__ import annotations
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from db_driver import AssistantDatabaseDriver
import logging

logger = logging.getLogger("AssistantFnc")

class AssistantFnc:
    """Function context for the AI voice assistant agent providing tools for user management,
    conversation tracking, task management, contact management, and settings management."""

    def __init__(self):
        """Initialize the Assistant Function context with database driver."""
        self.db = AssistantDatabaseDriver()
        logger.info("AssistantFnc initialized with database connection")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a user's profile information from the database.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing user profile data including preferences and last interaction
        """
        user = self.db.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        return user

    def create_or_update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user or update an existing user's profile.

        Args:
            user_id: Unique identifier for the user
            name: User's name
            preferences: Dictionary of user preferences

        Returns:
            Updated user profile information
        """
        return self.db.create_or_update_user(user_id, name, preferences)

    def save_conversation(
        self,
        user_id: str,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a conversation interaction to the database.

        Args:
            user_id: Unique identifier for the user
            query: User's input message
            response: Assistant's response message
            context: Additional contextual information

        Returns:
            True if successful
        """
        try:
            self.db.save_conversation(user_id, query, response, context)
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    def get_recent_conversations(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversations for a user.

        Args:
            user_id: Unique identifier for the user
            limit: Maximum number of conversations to retrieve

        Returns:
            List of conversation records ordered by most recent first
        """
        return self.db.get_recent_conversations(user_id, limit)

    def add_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: Literal["low", "medium", "high"] = "medium",
        category: Optional[str] = None
    ) -> int:
        """
        Add a new task or reminder for a user.

        Args:
            user_id: Unique identifier for the user
            title: Task title
            description: Detailed description of the task
            due_date: Due date in ISO format (YYYY-MM-DD HH:MM:SS)
            priority: Task priority (low, medium, high)
            category: Category for grouping tasks

        Returns:
            ID of the created task
        """
        # Convert string due_date to datetime if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
            except ValueError:
                logger.warning(f"Invalid date format for {due_date}, using None")

        return self.db.add_task(user_id, title, description, parsed_due_date, priority, category)

    def get_pending_tasks(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all pending tasks for a user, optionally filtered by category.

        Args:
            user_id: Unique identifier for the user
            category: Optional category to filter tasks

        Returns:
            List of pending task records
        """
        return self.db.get_pending_tasks(user_id, category)

    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to mark as completed

        Returns:
            True if task was successfully marked as completed
        """
        return self.db.complete_task(task_id)

    def add_contact(
        self,
        user_id: str,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        relationship: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Add a new contact for a user.

        Args:
            user_id: Unique identifier for the user
            name: Contact's name
            phone: Contact's phone number
            email: Contact's email address
            relationship: Relationship to the user
            notes: Additional notes about the contact

        Returns:
            ID of the created contact
        """
        return self.db.add_contact(user_id, name, phone, email, relationship, notes)

    def get_contacts(
        self,
        user_id: str,
        name_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all contacts for a user, optionally filtered by name.

        Args:
            user_id: Unique identifier for the user
            name_filter: Optional search term to filter contacts by name

        Returns:
            List of contact records
        """
        return self.db.get_contacts(user_id, name_filter)

    def update_user_settings(
        self,
        user_id: str,
        setting_type: Literal["voice_settings", "notification_preferences", "privacy_settings"],
        settings: Dict[str, Any]
    ) -> bool:
        """
        Update user settings (voice, notification, or privacy).

        Args:
            user_id: Unique identifier for the user
            setting_type: Type of settings to update (voice_settings, notification_preferences, privacy_settings)
            settings: Dictionary of settings to update

        Returns:
            True if settings were successfully updated
        """
        try:
            self.db.update_user_settings(user_id, setting_type, settings)
            return True
        except Exception as e:
            logger.error(f"Failed to update user settings: {e}")
            return False

    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get all settings for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing all user settings
        """
        settings = self.db.get_user_settings(user_id)
        if not settings:
            return {"error": "Settings not found"}
        return settings

    def generate_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a summary of user activity and status.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing summary information about tasks, contacts, and recent interactions
        """
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
