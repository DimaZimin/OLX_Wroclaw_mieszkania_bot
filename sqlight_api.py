import sqlite3


class SQLighter:

    def __init__(self, database):
        """Connect to database and save connection cursor"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, rooms, status=True):
        """Get active subscribers"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `rooms` = ? AND `status` = ?",
                                       (rooms, status)).fetchall()

    def subscriber_exists(self, user_id):
        """Check if user does exist in db"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Add new subscriber"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`, `status`) VALUES(?,?)",
                                       (user_id, status))

    def update_subscription(self, user_id, status):
        """Update subscription status of a subscriber"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def update_rooms(self, user_id, rooms):
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `rooms` = ? WHERE `user_id` = ?", (rooms, user_id))

    def get_user_settings(self, user_id):
        with self.connection:
            settings = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return settings

    def close(self):
        """close connection with db"""
        self.connection.close()
