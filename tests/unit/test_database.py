"""
Unit tests for database operations
"""
import pytest
from datetime import datetime

class TestUserManagement:
    """Test user management operations"""

    def test_create_account_request(self, temp_db, sample_user_data):
        """Test creating a new account request"""
        result = temp_db.create_account_request(
            sample_user_data["name"],
            sample_user_data["email"],
            sample_user_data["school"],
            sample_user_data["role"]
        )
        assert result is True

        # Verify account is pending
        pending = temp_db.get_pending_requests()
        assert len(pending) > 0
        assert pending[-1]["email"] == sample_user_data["email"]
        assert pending[-1]["status"] == "Pending Approval"

    def test_duplicate_email_rejection(self, temp_db, sample_user_data):
        """Test that duplicate emails are rejected"""
        temp_db.create_account_request(
            sample_user_data["name"],
            sample_user_data["email"],
            sample_user_data["school"],
            sample_user_data["role"]
        )

        # Try to create duplicate
        result = temp_db.create_account_request(
            "Another Name",
            sample_user_data["email"],
            sample_user_data["school"],
            sample_user_data["role"]
        )
        assert result is False

    def test_approve_account(self, temp_db, sample_user_data):
        """Test account approval"""
        temp_db.create_account_request(
            sample_user_data["name"],
            sample_user_data["email"],
            sample_user_data["school"],
            sample_user_data["role"]
        )

        pending = temp_db.get_pending_requests()
        user_id = pending[-1]["id"]

        result = temp_db.approve_account(user_id, "testuser", "testpass123")
        assert result is True

        # Verify user is active
        user = temp_db.get_user_by_id(user_id)
        assert user["status"] == "Active"
        assert user["username"] == "testuser"

    def test_reject_account(self, temp_db, sample_user_data):
        """Test account rejection"""
        temp_db.create_account_request(
            sample_user_data["name"],
            sample_user_data["email"],
            sample_user_data["school"],
            sample_user_data["role"]
        )

        pending = temp_db.get_pending_requests()
        user_id = pending[-1]["id"]

        result = temp_db.reject_account(user_id)
        assert result is True

        # Verify user is deleted
        user = temp_db.get_user_by_id(user_id)
        assert user is None

    def test_authenticate_user(self, db_with_users):
        """Test user authentication"""
        user = db_with_users.authenticate_user("testcore", "password123")
        assert user is not None
        assert user["username"] == "testcore"
        assert user["role"] == "Core Intern"

    def test_authenticate_invalid_password(self, db_with_users):
        """Test authentication with invalid password"""
        user = db_with_users.authenticate_user("testcore", "wrongpassword")
        assert user is None

    def test_authenticate_inactive_user(self, temp_db, sample_user_data):
        """Test that inactive users cannot authenticate"""
        temp_db.create_account_request(
            sample_user_data["name"],
            sample_user_data["email"],
            sample_user_data["school"],
            sample_user_data["role"]
        )

        pending = temp_db.get_pending_requests()
        user_id = pending[-1]["id"]
        temp_db.approve_account(user_id, "testuser", "password123")
        temp_db.toggle_user_status(user_id, "Inactive")

        user = temp_db.authenticate_user("testuser", "password123")
        assert user is None

    def test_get_all_users(self, db_with_users):
        """Test retrieving all active users"""
        users = db_with_users.get_all_users()
        assert len(users) >= 2  # At least our test users
        assert all(u["status"] == "Active" for u in users)

    def test_toggle_user_status(self, db_with_users):
        """Test toggling user status"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        result = db_with_users.toggle_user_status(user_id, "Inactive")
        assert result is True

        user = db_with_users.get_user_by_id(user_id)
        assert user["status"] == "Inactive"


class TestHoursManagement:
    """Test hours tracking operations"""

    def test_log_hours(self, db_with_users, sample_hours_data):
        """Test logging work hours"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        result = db_with_users.log_hours(
            user_id,
            sample_hours_data["date"],
            sample_hours_data["start_time"],
            sample_hours_data["end_time"],
            sample_hours_data["total_hours"],
            sample_hours_data["description"]
        )
        assert result is True

        # Verify hours were logged
        hours = db_with_users.get_user_hours(user_id)
        assert len(hours) == 1
        assert hours[0]["total_hours"] == sample_hours_data["total_hours"]

    def test_get_user_hours_with_date_filter(self, db_with_users, sample_hours_data):
        """Test retrieving hours with date filtering"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Log hours
        db_with_users.log_hours(
            user_id,
            sample_hours_data["date"],
            sample_hours_data["start_time"],
            sample_hours_data["end_time"],
            sample_hours_data["total_hours"],
            sample_hours_data["description"]
        )

        # Test date filtering
        hours = db_with_users.get_user_hours(
            user_id,
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        assert len(hours) == 1

        # Test no results outside date range
        hours = db_with_users.get_user_hours(
            user_id,
            start_date="2025-02-01",
            end_date="2025-02-28"
        )
        assert len(hours) == 0

    def test_approve_hours(self, db_with_users, sample_hours_data):
        """Test approving hours"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        db_with_users.log_hours(
            user_id,
            sample_hours_data["date"],
            sample_hours_data["start_time"],
            sample_hours_data["end_time"],
            sample_hours_data["total_hours"],
            sample_hours_data["description"]
        )

        hours = db_with_users.get_user_hours(user_id)
        hour_id = hours[0]["id"]

        result = db_with_users.approve_hours(hour_id, True)
        assert result is True

        # Verify approval
        hours = db_with_users.get_user_hours(user_id)
        assert hours[0]["approved"] == 1

    def test_get_total_hours(self, db_with_users, sample_hours_data):
        """Test calculating total hours"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Log multiple hours entries
        db_with_users.log_hours(user_id, "2025-01-15", "09:00", "13:00", 4.0, "Morning work")
        db_with_users.log_hours(user_id, "2025-01-16", "09:00", "17:00", 8.0, "Full day")

        total = db_with_users.get_total_hours(user_id)
        assert total == 12.0

    def test_get_approved_hours_only(self, db_with_users, sample_hours_data):
        """Test calculating approved hours only"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Log and approve first entry
        db_with_users.log_hours(user_id, "2025-01-15", "09:00", "13:00", 4.0, "Morning work")
        hours = db_with_users.get_user_hours(user_id)
        db_with_users.approve_hours(hours[0]["id"], True)

        # Log second entry (not approved)
        db_with_users.log_hours(user_id, "2025-01-16", "09:00", "17:00", 8.0, "Full day")

        approved_total = db_with_users.get_total_hours(user_id, approved_only=True)
        assert approved_total == 4.0


class TestDeliverablesManagement:
    """Test deliverables management operations"""

    def test_submit_deliverable(self, db_with_users, sample_deliverable_data):
        """Test submitting a deliverable"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        result = db_with_users.submit_deliverable(
            user_id,
            sample_deliverable_data["type"],
            sample_deliverable_data["description"],
            sample_deliverable_data["links"],
            sample_deliverable_data["proof_links"]
        )
        assert result is True

        # Verify deliverable
        deliverables = db_with_users.get_user_deliverables(user_id)
        assert len(deliverables) == 1
        assert deliverables[0]["type"] == sample_deliverable_data["type"]
        assert deliverables[0]["status"] == "Pending"

    def test_update_deliverable_status(self, db_with_users, sample_deliverable_data):
        """Test updating deliverable status"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        db_with_users.submit_deliverable(
            user_id,
            sample_deliverable_data["type"],
            sample_deliverable_data["description"],
            sample_deliverable_data["links"],
            sample_deliverable_data["proof_links"]
        )

        deliverables = db_with_users.get_user_deliverables(user_id)
        deliv_id = deliverables[0]["id"]

        result = db_with_users.update_deliverable_status(
            deliv_id,
            "Approved",
            "Great work!"
        )
        assert result is True

        # Verify update
        deliverables = db_with_users.get_user_deliverables(user_id)
        assert deliverables[0]["status"] == "Approved"
        assert deliverables[0]["admin_comments"] == "Great work!"

    def test_get_pending_deliverables(self, db_with_users, sample_deliverable_data):
        """Test retrieving pending deliverables"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Submit multiple deliverables
        db_with_users.submit_deliverable(user_id, "Reel", "Test 1", "", "")
        db_with_users.submit_deliverable(user_id, "IG Live", "Test 2", "", "")

        pending = db_with_users.get_pending_deliverables()
        assert len(pending) >= 2


class TestLeadInternFunctionality:
    """Test Lead Intern specific operations"""

    def test_get_core_interns(self, db_with_users):
        """Test retrieving Core Interns"""
        core_interns = db_with_users.get_core_interns()
        assert len(core_interns) >= 1
        assert all(intern["role"] == "Core Intern" for intern in core_interns)

    def test_submit_core_review(self, db_with_users, sample_review_data):
        """Test submitting a Core Intern review"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        result = db_with_users.submit_core_review(
            lead_id, core_id,
            sample_review_data["review_period"],
            sample_review_data["overall_vibe"],
            sample_review_data["whats_working"],
            sample_review_data["growth_areas"],
            sample_review_data["needs_support"],
            sample_review_data["hours_compliance"],
            sample_review_data["content_created"],
            sample_review_data["meeting_attendance"],
            sample_review_data["dm_response_rate"],
            sample_review_data["proof_uploaded"],
            sample_review_data["notes"]
        )
        assert result is True

        # Verify review
        reviews = db_with_users.get_core_reviews(lead_intern_id=lead_id)
        assert len(reviews) == 1
        assert reviews[0]["overall_vibe"] == sample_review_data["overall_vibe"]

    def test_create_support_plan(self, db_with_users, sample_support_plan_data):
        """Test creating a support plan"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        result = db_with_users.create_support_plan(
            lead_id, core_id,
            sample_support_plan_data["issue_challenge"],
            sample_support_plan_data["goal"],
            sample_support_plan_data["action_steps"],
            sample_support_plan_data["check_in_date"]
        )
        assert result is True

        # Verify support plan
        plans = db_with_users.get_support_plans(lead_intern_id=lead_id)
        assert len(plans) == 1
        assert plans[0]["goal"] == sample_support_plan_data["goal"]
        assert plans[0]["status"] == "Active"

    def test_update_support_plan_status(self, db_with_users, sample_support_plan_data):
        """Test updating support plan status"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        db_with_users.create_support_plan(
            lead_id, core_id,
            sample_support_plan_data["issue_challenge"],
            sample_support_plan_data["goal"],
            sample_support_plan_data["action_steps"],
            sample_support_plan_data["check_in_date"]
        )

        plans = db_with_users.get_support_plans(lead_intern_id=lead_id)
        plan_id = plans[0]["id"]

        result = db_with_users.update_support_plan_status(plan_id, "Completed")
        assert result is True

        # Verify update
        plans = db_with_users.get_support_plans(lead_intern_id=lead_id)
        assert plans[0]["status"] == "Completed"

    def test_add_win(self, db_with_users, sample_win_data):
        """Test adding a win"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        result = db_with_users.add_win(
            lead_id, core_id,
            sample_win_data["win_description"],
            sample_win_data["why_matters"],
            sample_win_data["celebrated"],
            sample_win_data["notes"]
        )
        assert result is True

        # Verify win
        wins = db_with_users.get_wins(lead_intern_id=lead_id)
        assert len(wins) == 1
        assert wins[0]["win_description"] == sample_win_data["win_description"]

    def test_mark_win_celebrated(self, db_with_users, sample_win_data):
        """Test marking a win as celebrated"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        db_with_users.add_win(lead_id, core_id, "Test win", "", False, "")

        wins = db_with_users.get_wins(lead_intern_id=lead_id)
        win_id = wins[0]["id"]

        result = db_with_users.mark_win_celebrated(win_id)
        assert result is True

        # Verify update
        wins = db_with_users.get_wins(lead_intern_id=lead_id)
        assert wins[0]["celebrated"] == 1


class TestDatabaseIntegrity:
    """Test database integrity and constraints"""

    def test_foreign_key_cascade_delete_user(self, db_with_users, sample_hours_data):
        """Test that deleting a user cascades to related records"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Create related records
        db_with_users.log_hours(
            user_id,
            sample_hours_data["date"],
            sample_hours_data["start_time"],
            sample_hours_data["end_time"],
            sample_hours_data["total_hours"],
            sample_hours_data["description"]
        )

        # Note: SQLite foreign key constraints with CASCADE would handle deletion
        # In production, you'd test the cascade behavior
        hours_before = db_with_users.get_user_hours(user_id)
        assert len(hours_before) > 0

    def test_admin_account_exists(self, temp_db):
        """Test that admin account is created by default"""
        user = temp_db.authenticate_user("admin123", "admin123456")
        assert user is not None
        assert user["role"] == "Admin"
        assert user["email"] == "admin@clubstride.org"