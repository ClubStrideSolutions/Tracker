"""
Integration tests for end-to-end workflows
"""
import pytest
from datetime import datetime, timedelta

class TestCoreInternWorkflow:
    """Test complete Core Intern workflow"""

    def test_complete_intern_onboarding_workflow(self, temp_db):
        """Test full onboarding process"""
        # Step 1: Intern submits account request
        result = temp_db.create_account_request(
            "New Intern",
            "intern@test.com",
            "Test University",
            "Core Intern"
        )
        assert result is True

        # Step 2: Admin reviews and approves
        pending = temp_db.get_pending_requests()
        assert len(pending) > 0

        intern_request = pending[-1]
        result = temp_db.approve_account(
            intern_request["id"],
            "newintern",
            "password123"
        )
        assert result is True

        # Step 3: Intern can now authenticate
        user = temp_db.authenticate_user("newintern", "password123")
        assert user is not None
        assert user["role"] == "Core Intern"
        assert user["status"] == "Active"

    def test_complete_hours_submission_workflow(self, db_with_users):
        """Test complete hours submission and approval workflow"""
        users = db_with_users.get_all_users()
        intern_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Step 1: Intern logs hours
        result = db_with_users.log_hours(
            intern_id,
            "2025-01-15",
            "09:00",
            "17:00",
            8.0,
            "Worked on social media content"
        )
        assert result is True

        # Step 2: Hours appear in pending list
        all_hours = db_with_users.get_all_hours()
        assert len(all_hours) > 0
        pending_hours = [h for h in all_hours if not h["approved"]]
        assert len(pending_hours) > 0

        # Step 3: Admin approves hours
        hour_entry = pending_hours[0]
        result = db_with_users.approve_hours(hour_entry["id"], True)
        assert result is True

        # Step 4: Hours are now approved
        total_approved = db_with_users.get_total_hours(intern_id, approved_only=True)
        assert total_approved == 8.0

    def test_complete_deliverable_workflow(self, db_with_users):
        """Test complete deliverable submission and review workflow"""
        users = db_with_users.get_all_users()
        intern_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Step 1: Intern submits deliverable
        result = db_with_users.submit_deliverable(
            intern_id,
            "Reel",
            "Mental health awareness Reel",
            "https://instagram.com/test",
            "https://drive.google.com/proof"
        )
        assert result is True

        # Step 2: Deliverable appears in pending list
        pending = db_with_users.get_pending_deliverables()
        assert len(pending) > 0

        # Step 3: Admin reviews and approves
        deliv = pending[0]
        result = db_with_users.update_deliverable_status(
            deliv["id"],
            "Approved",
            "Excellent work on the mental health content!"
        )
        assert result is True

        # Step 4: Intern can see approved status
        deliverables = db_with_users.get_user_deliverables(intern_id)
        assert deliverables[0]["status"] == "Approved"
        assert deliverables[0]["admin_comments"] is not None


class TestLeadInternWorkflow:
    """Test complete Lead Intern workflow"""

    def test_complete_review_workflow(self, db_with_users):
        """Test complete biweekly review workflow"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Step 1: Lead Intern conducts review
        result = db_with_users.submit_core_review(
            lead_id, core_id,
            "Week 1-2",
            "✅ On Track",
            "Great content creation, excellent engagement with peers",
            "Could improve posting consistency",
            "No - All Good!",
            "100% (4-6 hours)",
            "2+ Reels",
            "All meetings",
            "Excellent",
            "Yes - All uploaded",
            "Keep up the great work!"
        )
        assert result is True

        # Step 2: Review is stored and retrievable
        reviews = db_with_users.get_core_reviews(lead_intern_id=lead_id)
        assert len(reviews) == 1
        assert reviews[0]["core_intern_id"] == core_id

        # Step 3: Core Intern specific reviews can be queried
        core_reviews = db_with_users.get_core_reviews(core_intern_id=core_id)
        assert len(core_reviews) == 1

    def test_complete_support_plan_workflow(self, db_with_users):
        """Test complete support plan workflow"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Step 1: Lead identifies need for support
        result = db_with_users.submit_core_review(
            lead_id, core_id,
            "Week 3-4",
            "🌱 Getting There",
            "Trying hard, showing improvement",
            "Low engagement on posts",
            "Yes - Need Help",
            "75% (3-4 hours)",
            "1 Reel",
            "Most meetings",
            "Good",
            "Partial",
            "Needs support with content strategy"
        )
        assert result is True

        # Step 2: Lead creates support plan
        result = db_with_users.create_support_plan(
            lead_id, core_id,
            "Low engagement on social media posts",
            "Increase average engagement by 25%",
            "1. Research optimal posting times\n2. Improve hashtag strategy\n3. Create more interactive content",
            "2025-02-01"
        )
        assert result is True

        # Step 3: Support plan is active
        plans = db_with_users.get_support_plans(
            lead_intern_id=lead_id,
            status="Active"
        )
        assert len(plans) == 1

        # Step 4: Lead monitors progress and updates status
        result = db_with_users.update_support_plan_status(plans[0]["id"], "In Progress")
        assert result is True

        # Step 5: Eventually marks as completed
        result = db_with_users.update_support_plan_status(plans[0]["id"], "Completed")
        assert result is True

        completed_plans = db_with_users.get_support_plans(
            lead_intern_id=lead_id,
            status="Completed"
        )
        assert len(completed_plans) == 1

    def test_complete_wins_tracking_workflow(self, db_with_users):
        """Test complete wins tracking workflow"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Step 1: Lead documents win
        result = db_with_users.add_win(
            lead_id, core_id,
            "Posted viral Reel with 2000+ views",
            "Exceeded engagement goals by 400%",
            False,
            "First viral post!"
        )
        assert result is True

        # Step 2: Win is stored and retrievable
        wins = db_with_users.get_wins(lead_intern_id=lead_id)
        assert len(wins) == 1
        assert wins[0]["celebrated"] == 0

        # Step 3: Lead celebrates the win
        result = db_with_users.mark_win_celebrated(wins[0]["id"])
        assert result is True

        # Step 4: Win is marked as celebrated
        wins = db_with_users.get_wins(lead_intern_id=lead_id)
        assert wins[0]["celebrated"] == 1


class TestAdminWorkflow:
    """Test complete Admin workflow"""

    def test_complete_admin_oversight_workflow(self, temp_db):
        """Test admin oversight of entire system"""
        # Step 1: Admin reviews and approves multiple account requests
        temp_db.create_account_request("Lead 1", "lead1@test.com", "Univ A", "Lead Intern")
        temp_db.create_account_request("Core 1", "core1@test.com", "Univ A", "Core Intern")
        temp_db.create_account_request("Core 2", "core2@test.com", "Univ B", "Core Intern")

        pending = temp_db.get_pending_requests()
        assert len(pending) >= 3

        # Approve all
        for request in pending:
            username = f"user{request['id']}"
            temp_db.approve_account(request["id"], username, "pass123")

        # Step 2: Admin monitors all users
        active_users = temp_db.get_all_users()
        assert len(active_users) >= 3

        # Step 3: Admin can view all hours
        users = temp_db.get_all_users()
        for user in users[:2]:  # Log hours for first 2 users
            temp_db.log_hours(user["id"], "2025-01-15", "09:00", "17:00", 8.0, "Work")

        all_hours = temp_db.get_all_hours()
        assert len(all_hours) >= 2

        # Step 4: Admin can view all deliverables
        for user in users[:2]:
            temp_db.submit_deliverable(user["id"], "Reel", "Test content", "", "")

        all_deliverables = temp_db.get_all_deliverables()
        assert len(all_deliverables) >= 2

    def test_admin_deactivate_reactivate_user(self, db_with_users):
        """Test admin deactivating and reactivating users"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Step 1: Admin deactivates user
        result = db_with_users.toggle_user_status(user_id, "Inactive")
        assert result is True

        # Step 2: User cannot login
        user_data = db_with_users.get_user_by_id(user_id)
        assert user_data["status"] == "Inactive"

        # Step 3: Admin reactivates user
        result = db_with_users.toggle_user_status(user_id, "Active")
        assert result is True

        # Step 4: User can login again
        user_data = db_with_users.get_user_by_id(user_id)
        assert user_data["status"] == "Active"


class TestMultiUserScenarios:
    """Test scenarios with multiple users"""

    def test_multiple_lead_interns_managing_different_cores(self, temp_db):
        """Test multiple Lead Interns managing separate Core Intern teams"""
        # Create Lead 1 and their Core Interns
        temp_db.create_account_request("Lead A", "leada@test.com", "Univ A", "Lead Intern")
        temp_db.create_account_request("Core A1", "corea1@test.com", "Univ A", "Core Intern")
        temp_db.create_account_request("Core A2", "corea2@test.com", "Univ A", "Core Intern")

        # Create Lead 2 and their Core Interns
        temp_db.create_account_request("Lead B", "leadb@test.com", "Univ B", "Lead Intern")
        temp_db.create_account_request("Core B1", "coreb1@test.com", "Univ B", "Core Intern")

        # Approve all
        pending = temp_db.get_pending_requests()
        for i, request in enumerate(pending):
            temp_db.approve_account(request["id"], f"user{i}", "pass123")

        users = temp_db.get_all_users()
        lead_a = next(u for u in users if u["email"] == "leada@test.com")
        lead_b = next(u for u in users if u["email"] == "leadb@test.com")
        core_a1 = next(u for u in users if u["email"] == "corea1@test.com")
        core_b1 = next(u for u in users if u["email"] == "coreb1@test.com")

        # Lead A reviews Core A1
        temp_db.submit_core_review(
            lead_a["id"], core_a1["id"],
            "Week 1-2", "✅ On Track", "Good work", "Keep improving", "No",
            "100%", "2+ Reels", "", "", "", ""
        )

        # Lead B reviews Core B1
        temp_db.submit_core_review(
            lead_b["id"], core_b1["id"],
            "Week 1-2", "🎉 Crushing It!", "Excellent", "None", "No",
            "100%", "2+ Reels", "", "", "", ""
        )

        # Verify isolation
        lead_a_reviews = temp_db.get_core_reviews(lead_intern_id=lead_a["id"])
        lead_b_reviews = temp_db.get_core_reviews(lead_intern_id=lead_b["id"])

        assert len(lead_a_reviews) == 1
        assert len(lead_b_reviews) == 1
        assert lead_a_reviews[0]["core_intern_id"] == core_a1["id"]
        assert lead_b_reviews[0]["core_intern_id"] == core_b1["id"]

    def test_concurrent_hours_logging(self, db_with_users):
        """Test multiple interns logging hours simultaneously"""
        users = db_with_users.get_all_users()

        # Multiple interns log hours
        for i, user in enumerate(users[:3]):
            result = db_with_users.log_hours(
                user["id"],
                f"2025-01-{15+i}",
                "09:00",
                "17:00",
                8.0,
                f"Work session {i}"
            )
            assert result is True

        # Verify all hours recorded
        all_hours = db_with_users.get_all_hours()
        assert len(all_hours) >= 3

    def test_weekly_progress_tracking(self, db_with_users):
        """Test tracking weekly progress for Core Intern"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Week 1-2: Getting started
        db_with_users.submit_core_review(
            lead_id, core_id,
            "Week 1-2", "🌱 Getting There",
            "Learning the ropes", "Needs more content", "Maybe",
            "75%", "1 Reel", "", "", "", ""
        )

        # Week 3-4: Improving
        db_with_users.submit_core_review(
            lead_id, core_id,
            "Week 3-4", "✅ On Track",
            "Much better content", "Keep consistency", "No",
            "100%", "2+ Reels", "", "", "", ""
        )

        # Week 5-6: Excelling
        db_with_users.submit_core_review(
            lead_id, core_id,
            "Week 5-6", "🎉 Crushing It!",
            "Amazing engagement, viral content", "Nothing major", "No",
            "100%", "2+ Reels", "", "", "", ""
        )

        # Verify progression
        reviews = db_with_users.get_core_reviews(core_intern_id=core_id)
        assert len(reviews) == 3
        assert reviews[0]["review_period"] == "Week 5-6"  # Most recent first
        assert reviews[2]["review_period"] == "Week 1-2"  # Oldest last