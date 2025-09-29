"""
Performance and load testing for database operations
"""
import pytest
import time
from datetime import datetime, timedelta
import statistics

class TestDatabasePerformance:
    """Test database operation performance"""

    def test_bulk_user_creation_performance(self, temp_db):
        """Test performance of creating multiple users"""
        start_time = time.time()

        num_users = 100
        for i in range(num_users):
            temp_db.create_account_request(
                f"User {i}",
                f"user{i}@test.com",
                "Test University",
                "Core Intern"
            )

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nCreated {num_users} account requests in {duration:.2f}s")
        print(f"Average: {(duration/num_users)*1000:.2f}ms per request")

        # Assert reasonable performance (< 5 seconds for 100 users)
        assert duration < 5.0

    def test_bulk_hours_logging_performance(self, db_with_users):
        """Test performance of logging multiple hours entries"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        start_time = time.time()

        num_entries = 100
        for i in range(num_entries):
            day = 1 + (i % 28)
            db_with_users.log_hours(
                user_id,
                f"2025-01-{day:02d}",
                "09:00",
                "17:00",
                8.0,
                f"Work session {i}"
            )

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nLogged {num_entries} hours entries in {duration:.2f}s")
        print(f"Average: {(duration/num_entries)*1000:.2f}ms per entry")

        assert duration < 3.0

    def test_bulk_query_performance(self, db_with_users):
        """Test performance of querying hours with many entries"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Create 200 hours entries
        for i in range(200):
            day = 1 + (i % 28)
            db_with_users.log_hours(
                user_id,
                f"2025-01-{day:02d}",
                "09:00",
                "17:00",
                8.0,
                f"Work session {i}"
            )

        # Test query performance
        start_time = time.time()
        hours = db_with_users.get_user_hours(user_id)
        end_time = time.time()

        duration = end_time - start_time

        print(f"\nQueried {len(hours)} hours entries in {duration*1000:.2f}ms")

        assert duration < 0.5  # Should be fast
        assert len(hours) == 200

    def test_aggregate_query_performance(self, db_with_users):
        """Test performance of aggregate calculations"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Create 500 hours entries
        for i in range(500):
            day = 1 + (i % 28)
            db_with_users.log_hours(
                user_id,
                f"2025-01-{day:02d}",
                "09:00",
                "17:00",
                8.0,
                f"Work session {i}"
            )

        # Test aggregate query performance
        start_time = time.time()
        total = db_with_users.get_total_hours(user_id)
        end_time = time.time()

        duration = end_time - start_time

        print(f"\nCalculated total hours ({total:.1f}) in {duration*1000:.2f}ms")

        assert duration < 0.5
        assert total == 4000.0  # 500 entries * 8 hours

    def test_deliverable_query_performance(self, db_with_users):
        """Test performance with many deliverables"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        deliverable_types = ["Reel", "IG Live", "Event", "Meeting"]

        # Create 200 deliverables
        start_time = time.time()
        for i in range(200):
            db_with_users.submit_deliverable(
                user_id,
                deliverable_types[i % len(deliverable_types)],
                f"Deliverable {i}",
                "",
                ""
            )
        creation_time = time.time() - start_time

        # Query performance
        start_time = time.time()
        deliverables = db_with_users.get_user_deliverables(user_id)
        query_time = time.time() - start_time

        print(f"\nCreated 200 deliverables in {creation_time:.2f}s")
        print(f"Queried 200 deliverables in {query_time*1000:.2f}ms")

        assert creation_time < 3.0
        assert query_time < 0.5
        assert len(deliverables) == 200

    def test_review_query_performance(self, db_with_users):
        """Test performance with many reviews"""
        users = db_with_users.get_all_users()
        lead_id = next(u["id"] for u in users if u["role"] == "Lead Intern")
        core_id = next(u["id"] for u in users if u["role"] == "Core Intern")

        # Create 100 reviews
        start_time = time.time()
        for i in range(100):
            period = f"Week {i*2+1}-{i*2+2}"
            db_with_users.submit_core_review(
                lead_id, core_id,
                period, "✅ On Track",
                f"Review {i} - positive", f"Review {i} - growth", "No",
                "100%", "2+ Reels", "", "", "", ""
            )
        creation_time = time.time() - start_time

        # Query performance
        start_time = time.time()
        reviews = db_with_users.get_core_reviews(lead_intern_id=lead_id)
        query_time = time.time() - start_time

        print(f"\nCreated 100 reviews in {creation_time:.2f}s")
        print(f"Queried 100 reviews in {query_time*1000:.2f}ms")

        assert creation_time < 3.0
        assert query_time < 0.5
        assert len(reviews) == 100


class TestConcurrentOperations:
    """Test concurrent database operations"""

    def test_multiple_simultaneous_writes(self, db_with_users):
        """Test handling multiple simultaneous write operations"""
        users = db_with_users.get_all_users()

        start_time = time.time()

        # Simulate concurrent writes from multiple users
        for i in range(50):
            for user in users[:3]:
                db_with_users.log_hours(
                    user["id"],
                    f"2025-01-{1+(i%28):02d}",
                    "09:00",
                    "17:00",
                    8.0,
                    f"Concurrent work {i}"
                )

        duration = time.time() - start_time

        print(f"\nProcessed 150 concurrent writes in {duration:.2f}s")

        # Verify all writes succeeded
        total_entries = 0
        for user in users[:3]:
            entries = db_with_users.get_user_hours(user["id"])
            total_entries += len(entries)

        assert total_entries == 150

    def test_read_write_concurrency(self, db_with_users):
        """Test concurrent read and write operations"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Add initial data
        for i in range(50):
            db_with_users.log_hours(user_id, f"2025-01-{1+(i%28):02d}", "09:00", "17:00", 8.0, f"Work {i}")

        start_time = time.time()

        # Alternate between reads and writes
        for i in range(100):
            if i % 2 == 0:
                # Write
                db_with_users.log_hours(user_id, "2025-01-15", "09:00", "17:00", 8.0, f"Concurrent work {i}")
            else:
                # Read
                hours = db_with_users.get_user_hours(user_id)
                assert len(hours) > 0

        duration = time.time() - start_time

        print(f"\nProcessed 100 mixed read/write operations in {duration:.2f}s")

        assert duration < 5.0


class TestMemoryUsage:
    """Test memory efficiency"""

    def test_large_dataset_memory_efficiency(self, temp_db):
        """Test memory usage with large datasets"""
        import sys

        # Create 1000 users
        for i in range(1000):
            temp_db.create_account_request(
                f"User {i}",
                f"user{i}@test.com",
                "Test University",
                "Core Intern"
            )

        # Approve all (this will create password hashes)
        pending = temp_db.get_pending_requests()
        for i, request in enumerate(pending):
            if i % 100 == 0:  # Progress indicator
                print(f"\nApproving user {i}...")
            temp_db.approve_account(request["id"], f"user{i}", "pass123")

        # Query all users
        users = temp_db.get_all_users()

        # Calculate approximate memory usage
        memory_estimate = sys.getsizeof(users)
        print(f"\nMemory estimate for 1000 users: {memory_estimate/1024:.2f} KB")

        assert len(users) >= 1000
        # Memory should be reasonable (< 5MB for 1000 users)
        assert memory_estimate < 5 * 1024 * 1024


class TestResponseTimes:
    """Test and benchmark response times"""

    def test_authentication_response_time(self, db_with_users):
        """Benchmark authentication response time"""
        times = []

        for _ in range(100):
            start = time.perf_counter()
            user = db_with_users.authenticate_user("testcore", "password123")
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile

        print(f"\nAuthentication benchmark (100 iterations):")
        print(f"Average: {avg_time:.2f}ms")
        print(f"Median: {median_time:.2f}ms")
        print(f"P95: {p95_time:.2f}ms")

        # Assert reasonable performance
        assert avg_time < 100  # Average < 100ms
        assert p95_time < 200  # 95th percentile < 200ms

    def test_complex_query_response_time(self, db_with_users):
        """Benchmark complex query with joins"""
        users = db_with_users.get_all_users()

        # Create test data
        for user in users[:5]:
            for i in range(20):
                db_with_users.log_hours(user["id"], f"2025-01-{i+1:02d}", "09:00", "17:00", 8.0, "Work")

        times = []

        for _ in range(50):
            start = time.perf_counter()
            all_hours = db_with_users.get_all_hours()  # Joins with users table
            end = time.perf_counter()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)
        print(f"\nComplex query (with join) average time: {avg_time:.2f}ms")

        assert avg_time < 50  # Should be fast even with joins

    def test_export_data_performance(self, db_with_users):
        """Test performance of data export operations"""
        import pandas as pd

        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        # Create substantial dataset
        for i in range(500):
            db_with_users.log_hours(user_id, f"2025-01-{(i%28)+1:02d}", "09:00", "17:00", 8.0, f"Work {i}")

        # Time the export operation
        start_time = time.time()
        hours = db_with_users.get_user_hours(user_id)
        df = pd.DataFrame(hours)
        csv_data = df.to_csv(index=False)
        duration = time.time() - start_time

        print(f"\nExported 500 hours entries to CSV in {duration:.2f}s")
        print(f"CSV size: {len(csv_data)/1024:.2f} KB")

        assert duration < 2.0  # Should export quickly


class TestScalability:
    """Test system scalability"""

    def test_user_scalability(self, temp_db):
        """Test system with increasing number of users"""
        user_counts = [10, 50, 100, 500]
        creation_times = []

        for count in user_counts:
            # Clear and reset
            start_time = time.time()

            for i in range(count):
                temp_db.create_account_request(
                    f"User {i}",
                    f"user{i}_{count}@test.com",
                    "Test University",
                    "Core Intern"
                )

            duration = time.time() - start_time
            creation_times.append(duration)

            print(f"\n{count} users: {duration:.2f}s ({(duration/count)*1000:.2f}ms per user)")

        # Verify roughly linear scaling (not exponential)
        # Time per user should not increase dramatically
        time_per_user_10 = creation_times[0] / user_counts[0]
        time_per_user_500 = creation_times[3] / user_counts[3]

        print(f"\nTime per user at 10 users: {time_per_user_10*1000:.2f}ms")
        print(f"Time per user at 500 users: {time_per_user_500*1000:.2f}ms")

        # Should not degrade by more than 3x
        assert time_per_user_500 < time_per_user_10 * 3

    def test_data_volume_scalability(self, db_with_users):
        """Test query performance with increasing data volume"""
        users = db_with_users.get_all_users()
        user_id = users[0]["id"]

        data_sizes = [100, 500, 1000]
        query_times = []

        for size in data_sizes:
            # Add data
            for i in range(size):
                db_with_users.log_hours(user_id, f"2025-01-{(i%28)+1:02d}", "09:00", "17:00", 8.0, f"Work {i}")

            # Measure query time
            start = time.time()
            hours = db_with_users.get_user_hours(user_id)
            duration = time.time() - start
            query_times.append(duration)

            print(f"\nQuery {len(hours)} entries: {duration*1000:.2f}ms")

        # Query time should scale reasonably
        assert all(t < 1.0 for t in query_times)  # All queries < 1 second