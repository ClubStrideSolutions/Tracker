"""
Load testing script for the Intern Hour Tracker
Run with: locust -f tests/load_test.py
"""
from locust import HttpUser, task, between
import random

class InternTrackerUser(HttpUser):
    """
    Simulates user behavior for load testing
    """
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    def on_start(self):
        """Execute on start - login"""
        # Note: Adapt these endpoints based on your actual API structure
        self.username = f"testuser{random.randint(1, 1000)}"
        self.user_id = random.randint(1, 100)

    @task(3)
    def view_dashboard(self):
        """Most common task - viewing dashboard"""
        self.client.get("/")

    @task(2)
    def view_hours(self):
        """View hours history"""
        self.client.get("/hours")

    @task(2)
    def view_deliverables(self):
        """View deliverables"""
        self.client.get("/deliverables")

    @task(1)
    def log_hours(self):
        """Submit hours (less frequent)"""
        payload = {
            "date": "2025-01-15",
            "start_time": "09:00",
            "end_time": "17:00",
            "description": "Load test work session"
        }
        self.client.post("/api/hours", json=payload)

    @task(1)
    def submit_deliverable(self):
        """Submit deliverable (less frequent)"""
        payload = {
            "type": "Reel",
            "description": "Load test deliverable",
            "links": "https://test.com",
            "proof_links": "https://proof.com"
        }
        self.client.post("/api/deliverables", json=payload)


class LeadInternUser(HttpUser):
    """
    Simulates Lead Intern behavior
    """
    wait_time = between(2, 6)

    @task(3)
    def view_team_dashboard(self):
        """View Core Intern team dashboard"""
        self.client.get("/lead/dashboard")

    @task(2)
    def view_reviews(self):
        """View previous reviews"""
        self.client.get("/lead/reviews")

    @task(1)
    def submit_review(self):
        """Submit Core Intern review"""
        payload = {
            "core_intern_id": random.randint(1, 50),
            "review_period": "Week 1-2",
            "overall_vibe": "On Track",
            "whats_working": "Good progress",
            "growth_areas": "Keep improving",
            "needs_support": "No"
        }
        self.client.post("/api/reviews", json=payload)

    @task(1)
    def view_support_plans(self):
        """View support plans"""
        self.client.get("/lead/support-plans")


class AdminUser(HttpUser):
    """
    Simulates Admin behavior
    """
    wait_time = between(3, 8)

    @task(3)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        self.client.get("/admin/dashboard")

    @task(2)
    def review_pending_accounts(self):
        """Review pending account requests"""
        self.client.get("/admin/accounts/pending")

    @task(2)
    def review_hours(self):
        """Review pending hours"""
        self.client.get("/admin/hours/review")

    @task(2)
    def review_deliverables(self):
        """Review pending deliverables"""
        self.client.get("/admin/deliverables/review")

    @task(1)
    def approve_hours(self):
        """Approve hours entry"""
        hour_id = random.randint(1, 1000)
        self.client.post(f"/api/hours/{hour_id}/approve")

    @task(1)
    def generate_report(self):
        """Generate activity report"""
        self.client.get("/admin/reports/activity")


# Load test scenarios
class StressTestUser(HttpUser):
    """
    Heavy load user for stress testing
    """
    wait_time = between(0.5, 1)

    @task
    def rapid_fire_requests(self):
        """Rapid consecutive requests"""
        endpoints = ["/", "/hours", "/deliverables", "/admin/dashboard"]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)