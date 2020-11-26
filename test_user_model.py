"""User model tests."""
# python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        testuser1 = User.signup("testuser1", "testuser1@email.com", "password", None)
        testuser2 = User.signup("testuser2", "testuser2@email.com", "password", None)
        testuser1id = 123456
        testuser2id = 1234567
        testuser1.id = testuser1id
        testuser2.id = testuser2id
        db.session.commit()
        testuser1 = User.query.get(testuser1id)
        testuser2 = User.query.get(testuser2id)
        self.testuser1 = testuser1
        self.testuser1id = testuser1id
        self.testuser2 = testuser2
        self.testuser2id = testuser2id
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        testuser3 = User("testuser3", "testuser3@email.com", "randompassword")
        db.session.add(testuser3)
        db.session.commit()
        self.assertEqual(len(testuser3.messages), 0)
        self.assertEqual(len(testuser3.likes), 0)
        self.assertEqual(len(testuser3.following), 0)
        self.assertEqual(len(testuser3.followers), 0)

    def test_following(self):
        self.testuser1.following.append(self.testuser2)
        db.session.commit()
        self.assertTrue(self.testuser1.is_following(self.testuser2))
        self.assertFalse(self.testuser2.is_following(self.testuser1))

    def test_followed(self):
        self.testuser1.following.append(self.testuser2)
        db.session.commit()
        self.assertTrue(self.testuser2.is_followed_by(self.testuser1))
        self.assertFalse(self.testuser1.is_followed_by(self.testuser2))

    def test_valid_signup(self):
        testuser3 = User.signup("testuser3", "testuser3@email.com", "password", None)
        testuser3id = 12345678
        testuser3.id = testuser3id
        db.session.commit()
        testuser3 = User.query.get(testuser3id)
        self.assertEqual(testuser3.username, "testuser3")
        self.assertEqual(testuser3.email, "testuser3@email.com")
        self.assertNotEqual(testuser3.password, "password")

    def test_invalid_signup(self):
        invalid = User.signup(None, "test@email.com", "password", None)
        invalidid = 123456789
        invalid.id = invalidid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authentication(self):
        user = User.authenticate(self.testuser1.username, "password")
        self.assertEqual(user.id, self.testuser1id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notacorrectusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.testuser1.username, "notacorrectpassword"))




        




        

