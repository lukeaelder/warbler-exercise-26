"""Message model tests."""
# python -m unittest test_message_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        testuser1 = User.signup("testuser1", "testuser1@email.com", "password", None)
        self.testuser1id = 12345678
        testuser1.id = self.testuser1id
        db.session.commit()
        self.testuser1 = User.query.get(self.testuser1id)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        message1 = Message(text="Test message",user_id=self.testuser1id)
        db.session.add(message1)
        db.session.commit()
        self.assertEqual(len(self.testuser1.messages), 1)
        self.assertEqual(self.testuser1.messages[0].text, "Test message")

    def test_like_message(self):
        message1 = Message(text="Test message",user_id=self.testuser1id)
        message2 = Message(text="Tst message 2",user_id=self.testuser1id )
        testuser1 = User.signup("testuser2", "testuser2@email.com", "password", None)
        testuser1id = 123456789
        testuser1.id = testuser1id
        db.session.add_all([message1, message2, testuser1])
        db.session.commit()
        testuser1.likes.append(message1)
        db.session.commit()
        l = Likes.query.filter(Likes.user_id == testuser1id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, message1.id)   