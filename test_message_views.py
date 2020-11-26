"""Message View tests."""
# FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase
from models import db, connect_db, Message, User
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app, CURR_USER_KEY
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        self.testuser1 = User.signup(username="testuser1", email="test@test.com", password="testuser1", image_url=None)
        self.testuser1id = 12345678
        self.testuser1.id = self.testuser1id
        db.session.commit()

    def test_add_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            resp = c.post("/messages/new", data={"text": "Test message"})
            self.assertEqual(resp.status_code, 302)
            msg = Message.query.one()
            self.assertEqual(msg.text, "Test messgae")

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224
            resp = c.post("/messages/new", data={"text": "Test message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_message_delete(self):
        m = Message(id=999999, text="a test message", user_id=self.testuser1id)
        db.session.add(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            resp = c.post("/messages/999999/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            m = Message.query.get(999999)
            self.assertIsNone(m)

    def test_unauthorized_message_delete(self):
        testuser2 = User.signup("testuser2", "testuser2@email.com", "password", None)
        testuser2.id = 123456789
        m = Message(id=999999, text="Test message", user_id=self.testuser1id)
        db.session.add_all([testuser2, m])
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 123456789
            resp = c.post("/messages/999999/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            m = Message.query.get(999999)
            self.assertIsNotNone(m)