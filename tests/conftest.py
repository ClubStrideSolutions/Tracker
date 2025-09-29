"""
Pytest configuration and fixtures for the Intern Hour Tracker test suite
"""
import pytest
import os
import tempfile
from database import Database
from auth import Auth

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name

    db = Database(db_path)
    yield db

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def db_with_users(temp_db):
    """Database with test users already created"""
    # Create test users
    temp_db.create_account_request(
        "Test Core Intern",
        "core@test.com",
        "Test University",
        "Core Intern"
    )

    temp_db.create_account_request(
        "Test Lead Intern",
        "lead@test.com",
        "Test University",
        "Lead Intern"
    )

    # Approve and set credentials
    temp_db.approve_account(2, "testcore", "password123")
    temp_db.approve_account(3, "testlead", "password123")

    return temp_db

@pytest.fixture
def auth_instance(temp_db):
    """Create an auth instance with temp database"""
    return Auth(temp_db)

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "name": "Sample User",
        "email": "sample@test.com",
        "school": "Test University",
        "role": "Core Intern"
    }

@pytest.fixture
def sample_hours_data():
    """Sample hours data for testing"""
    return {
        "date": "2025-01-15",
        "start_time": "09:00",
        "end_time": "17:00",
        "total_hours": 8.0,
        "description": "Test work session"
    }

@pytest.fixture
def sample_deliverable_data():
    """Sample deliverable data for testing"""
    return {
        "type": "Reel",
        "description": "Test Instagram Reel about mental health",
        "links": "https://instagram.com/test",
        "proof_links": "https://drive.google.com/test"
    }

@pytest.fixture
def sample_review_data():
    """Sample Core Intern review data for testing"""
    return {
        "review_period": "Week 1-2",
        "overall_vibe": "✅ On Track",
        "whats_working": "Great content creation and engagement",
        "growth_areas": "Could improve posting consistency",
        "needs_support": "No - All Good!",
        "hours_compliance": "100% (4-6 hours)",
        "content_created": "2+ Reels",
        "meeting_attendance": "All meetings",
        "dm_response_rate": "Excellent",
        "proof_uploaded": "Yes - All uploaded",
        "notes": "Keep up the great work!"
    }

@pytest.fixture
def sample_support_plan_data():
    """Sample support plan data for testing"""
    return {
        "issue_challenge": "Low engagement on posts",
        "goal": "Increase engagement by 20%",
        "action_steps": "1. Research best posting times\n2. Improve hashtags\n3. Create more interactive content",
        "check_in_date": "2025-02-01"
    }

@pytest.fixture
def sample_win_data():
    """Sample win data for testing"""
    return {
        "win_description": "Posted viral Reel with 1000+ views",
        "why_matters": "Exceeded engagement goals and reached wider audience",
        "celebrated": True,
        "notes": "Amazing work!"
    }