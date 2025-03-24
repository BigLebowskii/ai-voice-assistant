import psycopg2
import psycopg2.extras
import json
from datetime import datetime

class AssistantDatabaseDriver:
    def __init__(self, dbname="assistant_db", user="postgres", password="password", host="localhost", port="5432"):
        """Initialize the PostgreSQL database driver with connection parameters."""
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.conn = None
        self.initialize_db()

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            return True
        except psycopg2.Error as e:
            print(f"Connection error: {e}")
            return False

    def initialize_db(self):
        """Initialize database and create tables if they don't exist."""
        if not self.connect():
            return False

        cursor = self.conn.cursor()

        # User profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            preferences JSONB,
            last_interaction TIMESTAMP
        )
        ''')

        # Conversations history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) REFERENCES user_profiles(user_id),
            timestamp TIMESTAMP,
            query TEXT,
            response TEXT,
            context JSONB
        )
        ''')

        # Tasks/reminders
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) REFERENCES user_profiles(user_id),
            title VARCHAR(255),
            description TEXT,
            due_date TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            priority VARCHAR(50),
            category VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # User settings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id VARCHAR(255) PRIMARY KEY REFERENCES user_profiles(user_id),
            voice_settings JSONB,
            notification_preferences JSONB,
            privacy_settings JSONB
        )
        ''')

        # Contacts
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) REFERENCES user_profiles(user_id),
            name VARCHAR(255),
            phone VARCHAR(100),
            email VARCHAR(255),
            relationship VARCHAR(100),
            notes TEXT
        )
        ''')

        self.conn.commit()
        return True

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def get_user(self, user_id):
        """Get user profile by ID."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            return dict(user)
        return None

    def create_or_update_user(self, user_id, name=None, preferences=None):
        """Create or update a user profile."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor()
        current_time = datetime.now()

        # Check if user exists
        existing_user = self.get_user(user_id)

        if existing_user:
            # Update existing user
            update_data = [current_time]
            update_query = "UPDATE user_profiles SET last_interaction = %s"

            if name:
                update_query += ", name = %s"
                update_data.append(name)

            if preferences:
                update_query += ", preferences = %s"
                update_data.append(json.dumps(preferences))

            update_query += " WHERE user_id = %s"
            update_data.append(user_id)

            cursor.execute(update_query, update_data)
        else:
            # Create new user
            cursor.execute(
                "INSERT INTO user_profiles (user_id, name, preferences, last_interaction) VALUES (%s, %s, %s, %s)",
                (user_id, name or "", json.dumps(preferences or {}), current_time)
            )

            # Initialize user settings
            cursor.execute(
                "INSERT INTO user_settings (user_id, voice_settings, notification_preferences, privacy_settings) VALUES (%s, %s, %s, %s)",
                (user_id, '{}', '{}', '{}')
            )

        self.conn.commit()
        return self.get_user(user_id)

    def save_conversation(self, user_id, query, response, context=None):
        """Save a conversation interaction."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor()
        current_time = datetime.now()

        cursor.execute(
            "INSERT INTO conversations (user_id, timestamp, query, response, context) VALUES (%s, %s, %s, %s, %s)",
            (user_id, current_time, query, response, json.dumps(context or {}))
        )

        # Update last interaction time
        cursor.execute(
            "UPDATE user_profiles SET last_interaction = %s WHERE user_id = %s",
            (current_time, user_id)
        )

        self.conn.commit()

    def get_recent_conversations(self, user_id, limit=5):
        """Get recent conversations for a user."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            "SELECT timestamp, query, response, context FROM conversations WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
            (user_id, limit)
        )

        conversations = []
        for row in cursor.fetchall():
            conversations.append(dict(row))

        return conversations

    def add_task(self, user_id, title, description="", due_date=None, priority="medium", category=None):
        """Add a new task/reminder for a user."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, due_date, priority, category) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (user_id, title, description, due_date, priority, category)
        )

        task_id = cursor.fetchone()[0]
        self.conn.commit()
        return task_id

    def get_pending_tasks(self, user_id, category=None):
        """Get all pending tasks for a user, optionally filtered by category."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if category:
            cursor.execute(
                "SELECT id, title, description, due_date, priority, category FROM tasks WHERE user_id = %s AND completed = FALSE AND category = %s ORDER BY due_date, priority",
                (user_id, category)
            )
        else:
            cursor.execute(
                "SELECT id, title, description, due_date, priority, category FROM tasks WHERE user_id = %s AND completed = FALSE ORDER BY due_date, priority",
                (user_id,)
            )

        tasks = []
        for row in cursor.fetchall():
            tasks.append(dict(row))

        return tasks

    def complete_task(self, task_id):
        """Mark a task as completed."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tasks SET completed = TRUE WHERE id = %s",
            (task_id,)
        )

        self.conn.commit()
        return cursor.rowcount > 0

    def add_contact(self, user_id, name, phone=None, email=None, relationship=None, notes=None):
        """Add a new contact for a user."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO contacts (user_id, name, phone, email, relationship, notes) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (user_id, name, phone, email, relationship, notes)
        )

        contact_id = cursor.fetchone()[0]
        self.conn.commit()
        return contact_id

    def get_contacts(self, user_id, name_filter=None):
        """Get all contacts for a user, optionally filtered by name."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if name_filter:
            # Using ILIKE for case-insensitive partial matching
            cursor.execute(
                "SELECT id, name, phone, email, relationship, notes FROM contacts WHERE user_id = %s AND name ILIKE %s",
                (user_id, f"%{name_filter}%")
            )
        else:
            cursor.execute(
                "SELECT id, name, phone, email, relationship, notes FROM contacts WHERE user_id = %s",
                (user_id,)
            )

        contacts = []
        for row in cursor.fetchall():
            contacts.append(dict(row))

        return contacts

    def update_user_settings(self, user_id, setting_type, settings):
        """Update user settings (voice, notification, or privacy)."""
        if not self.conn or self.conn.closed:
            self.connect()

        if setting_type not in ['voice_settings', 'notification_preferences', 'privacy_settings']:
            raise ValueError("Invalid setting type")

        cursor = self.conn.cursor()

        # Check if settings exist
        cursor.execute("SELECT 1 FROM user_settings WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            # Create default settings
            cursor.execute(
                "INSERT INTO user_settings (user_id, voice_settings, notification_preferences, privacy_settings) VALUES (%s, %s, %s, %s)",
                (user_id, '{}', '{}', '{}')
            )

        # Update specific settings
        cursor.execute(
            f"UPDATE user_settings SET {setting_type} = %s WHERE user_id = %s",
            (json.dumps(settings), user_id)
        )

        self.conn.commit()

    def get_user_settings(self, user_id):
        """Get all settings for a user."""
        if not self.conn or self.conn.closed:
            self.connect()

        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM user_settings WHERE user_id = %s", (user_id,))

        settings = cursor.fetchone()
        return dict(settings) if settings else None
