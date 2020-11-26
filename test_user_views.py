"""User View tests."""
# FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup
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
        self.testuser1 = User.signup("testuser1", "testuser1@email.com", "password", None)
        self.testuser2 = User.signup("testuser2", "testuser2@email.com", "password", None)
        self.testuser3 = User.signup("testuser3", "testuser3@email.com", "password", None)
        self.testuser1id = 1234567
        self.testuser2id = 12345678
        self.testuser3id = 123456789
        self.testuser1.id = self.testuser1id
        self.testuser2.id = self.testuser2id
        self.testuser3.id = self.testuser3id
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))

    def test_show_following(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get(f"/users/{self.testuser1id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))

    def test_show_followers(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get(f"/users/{self.testuser1id}/followers")
            self.assertIn("@testuser2", str(resp.data))
            self.assertNotIn("@testuser3", str(resp.data))

    def test_unauthorized_following_page(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1id}/following", follow_redirects=True)
            self.assertNotIn("@testuser2", str(resp.data))

    def test_unauthorized_followers_page(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1id}/followers", follow_redirects=True)
            self.assertNotIn("@testuser2", str(resp.data))

    def setup_followers(self):
        follow1 = Follows(user_being_followed_id=self.testuser2id, user_following_id=self.testuser1id)
        follow2 = Follows(user_being_followed_id=self.testuser3id, user_following_id=self.testuser1id)
        follow3 = Follows(user_being_followed_id=self.testuser1id, user_following_id=self.testuser2id)
        db.session.add_all([follow1, follow2, follow3])
        db.session.commit()