import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import Database
from auth import Auth

def lead_intern_dashboard(db: Database, auth: Auth):
    """Lead Intern dashboard with Core Intern management"""
    user = auth.get_current_user()
    st.title(f"Lead Intern Portal - {user['name']}")

    menu = st.sidebar.radio(
        "Lead Intern Menu",
        ["Dashboard", "Review Core Interns", "Support Plans", "Track Wins", "View Reports"]
    )

    if menu == "Dashboard":
        lead_home(db, user)
    elif menu == "Review Core Interns":
        review_core_interns(db, user)
    elif menu == "Support Plans":
        manage_support_plans(db, user)
    elif menu == "Track Wins":
        track_wins(db, user)
    elif menu == "View Reports":
        view_reports(db, user)

def lead_home(db: Database, user: dict):
    """Lead Intern home dashboard"""
    st.header("🌟 My Core Team Overview")

    # Get Core Interns
    core_interns = db.get_core_interns()

    if not core_interns:
        st.info("No Core Interns in the system yet. Check back soon!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Core Interns", len(core_interns))

    with col2:
        recent_reviews = db.get_core_reviews(lead_intern_id=user['id'])
        st.metric("Reviews Submitted", len(recent_reviews))

    with col3:
        active_plans = db.get_support_plans(lead_intern_id=user['id'], status='Active')
        st.metric("Active Support Plans", len(active_plans))

    with col4:
        wins = db.get_wins(lead_intern_id=user['id'])
        st.metric("Team Wins", len(wins))

    st.divider()

    # Core Team Cards
    st.subheader("💫 Your Core Team")

    for intern in core_interns[:3]:  # Show up to 3 interns
        with st.expander(f"📋 {intern['name']} - {intern['school']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Email:** {intern['email']}")
                st.write(f"**Start Date:** {intern['start_date']}")

                # Get latest review
                reviews = db.get_core_reviews(lead_intern_id=user['id'], core_intern_id=intern['id'])
                if reviews:
                    latest = reviews[0]
                    st.write(f"**Last Review:** {latest['review_date']}")
                    st.write(f"**Overall Vibe:** {latest['overall_vibe']}")
                else:
                    st.warning("No reviews yet - schedule one soon!")

            with col2:
                # Get hours and deliverables
                total_hours = db.get_total_hours(intern['id'])
                deliverables = db.get_user_deliverables(intern['id'])

                st.metric("Total Hours", f"{total_hours:.1f}")
                st.metric("Deliverables", len(deliverables))

                # Support status
                support_plans = db.get_support_plans(lead_intern_id=user['id'],
                                                    core_intern_id=intern['id'],
                                                    status='Active')
                if support_plans:
                    st.warning(f"⚠️ {len(support_plans)} Active Support Plan(s)")

    st.divider()

    # Recent Wins
    st.subheader("🎉 Recent Team Wins")
    recent_wins = db.get_wins(lead_intern_id=user['id'])

    if recent_wins[:5]:
        for win in recent_wins[:5]:
            col1, col2 = st.columns([4, 1])
            with col1:
                celebrated_emoji = "🎊" if win['celebrated'] else "⭐"
                st.write(f"{celebrated_emoji} **{win['core_name']}**: {win['win_description']}")
                if win['why_matters']:
                    st.caption(f"Why it matters: {win['why_matters']}")
            with col2:
                if not win['celebrated']:
                    if st.button("Celebrate!", key=f"celebrate_{win['id']}"):
                        db.mark_win_celebrated(win['id'])
                        st.success("Celebrated! 🎉")
                        st.rerun()
    else:
        st.info("No wins recorded yet. Start celebrating your team's achievements!")

def review_core_interns(db: Database, user: dict):
    """Biweekly Core Intern review interface"""
    st.header("✨ Core Intern Check-Ins")

    st.info("📅 **Remember:** Complete reviews every 2 weeks (biweekly)")

    core_interns = db.get_core_interns()

    if not core_interns:
        st.warning("No Core Interns available to review.")
        return

    # Review Period Selection
    col1, col2 = st.columns(2)

    with col1:
        review_period = st.selectbox(
            "Review Period",
            ["Week 1-2", "Week 3-4", "Week 5-6", "Week 7-8"]
        )

    with col2:
        intern_to_review = st.selectbox(
            "Select Core Intern",
            options=[intern['name'] for intern in core_interns],
            key="review_intern_select"
        )

    # Get selected intern
    selected_intern = next((i for i in core_interns if i['name'] == intern_to_review), None)

    if not selected_intern:
        return

    st.divider()

    # Show previous reviews
    with st.expander("📜 Previous Reviews"):
        prev_reviews = db.get_core_reviews(lead_intern_id=user['id'],
                                          core_intern_id=selected_intern['id'])
        if prev_reviews:
            for review in prev_reviews:
                st.write(f"**{review['review_period']}** ({review['review_date']})")
                st.write(f"Vibe: {review['overall_vibe']}")
                st.write(f"Working Well: {review['whats_working']}")
                st.write(f"Growth Areas: {review['growth_areas']}")
                st.divider()
        else:
            st.info("No previous reviews")

    st.subheader(f"🌟 New Check-In for {selected_intern['name']}")

    with st.form("review_form"):
        st.write("### Overall Assessment")

        overall_vibe = st.select_slider(
            "Overall Vibe",
            options=["💬 Let's Chat", "🌱 Getting There", "✅ On Track", "🎉 Crushing It!"],
            value="✅ On Track"
        )

        col1, col2 = st.columns(2)

        with col1:
            whats_working = st.text_area(
                "What's Working Well 🌟",
                placeholder="2-3 specific positives... (e.g., Posted creative Reels, engaged with peers)"
            )

        with col2:
            growth_areas = st.text_area(
                "Growth Areas 🌱",
                placeholder="Gentle suggestions... (e.g., Could work on posting consistency)"
            )

        needs_support = st.radio(
            "Needs Support?",
            ["No - All Good!", "Maybe - Check In", "Yes - Need Help"],
            horizontal=True
        )

        st.write("### Behind-the-Scenes Metrics")
        st.caption("(For program reporting)")

        col1, col2 = st.columns(2)

        with col1:
            hours_compliance = st.selectbox(
                "Hours Compliance (2 days/week)",
                ["100% (4-6 hours)", "75% (3-4 hours)", "50% (2-3 hours)", "Below 50%"]
            )

            content_created = st.selectbox(
                "Content Created (2 Reels/week goal)",
                ["2+ Reels", "1 Reel", "Other content only", "No content"]
            )

        with col2:
            meeting_attendance = st.selectbox(
                "Meeting Attendance",
                ["All meetings", "Most meetings", "Some meetings", "Missed multiple"]
            )

            dm_response_rate = st.selectbox(
                "DM Response Rate",
                ["Excellent", "Good", "Needs Improvement", "Poor"]
            )

        proof_uploaded = st.selectbox(
            "Proof of Work Uploaded to Drive",
            ["Yes - All uploaded", "Partial", "Not yet"]
        )

        notes = st.text_area(
            "Additional Notes",
            placeholder="Any other observations or action items..."
        )

        submit = st.form_submit_button("Submit Check-In", use_container_width=True)

        if submit:
            if whats_working and growth_areas:
                success = db.submit_core_review(
                    lead_intern_id=user['id'],
                    core_intern_id=selected_intern['id'],
                    review_period=review_period,
                    overall_vibe=overall_vibe,
                    whats_working=whats_working,
                    growth_areas=growth_areas,
                    needs_support=needs_support,
                    hours_compliance=hours_compliance,
                    content_created=content_created,
                    meeting_attendance=meeting_attendance,
                    dm_response_rate=dm_response_rate,
                    proof_uploaded=proof_uploaded,
                    notes=notes
                )

                if success:
                    st.success(f"✅ Check-in for {selected_intern['name']} submitted!")
                    if "Yes" in needs_support:
                        st.warning("⚠️ Don't forget to create a support plan!")
                    st.rerun()
                else:
                    st.error("Failed to submit review. Please try again.")
            else:
                st.warning("Please fill in 'What's Working Well' and 'Growth Areas'")

def manage_support_plans(db: Database, user: dict):
    """Support plan management for Core Interns"""
    st.header("💪 Support Plans")

    tab1, tab2 = st.tabs(["Active Plans", "Create New Plan"])

    with tab1:
        st.subheader("🎯 Active Support Plans")

        active_plans = db.get_support_plans(lead_intern_id=user['id'])

        if not active_plans:
            st.info("No support plans yet. Create one when a Core Intern needs extra help!")
        else:
            for plan in active_plans:
                status_color = {
                    'Active': '🟢',
                    'In Progress': '🟡',
                    'Completed': '✅',
                    'On Hold': '⏸️'
                }
                emoji = status_color.get(plan['status'], '📋')

                with st.expander(f"{emoji} {plan['core_name']} - {plan['goal']}", expanded=plan['status']=='Active'):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Core Intern:** {plan['core_name']}")
                        st.write(f"**Start Date:** {plan['start_date']}")
                        st.write(f"**Check-In Date:** {plan['check_in_date']}")

                    with col2:
                        st.write(f"**Status:** {plan['status']}")

                    st.write(f"**Challenge:** {plan['issue_challenge']}")
                    st.write(f"**Goal:** {plan['goal']}")
                    st.write(f"**Action Steps:** {plan['action_steps']}")

                    # Update status
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if st.button("Mark In Progress", key=f"progress_{plan['id']}"):
                            db.update_support_plan_status(plan['id'], 'In Progress')
                            st.rerun()

                    with col2:
                        if st.button("Mark Completed", key=f"complete_{plan['id']}"):
                            db.update_support_plan_status(plan['id'], 'Completed')
                            st.rerun()

                    with col3:
                        if st.button("Put On Hold", key=f"hold_{plan['id']}"):
                            db.update_support_plan_status(plan['id'], 'On Hold')
                            st.rerun()

                    with col4:
                        if st.button("Reactivate", key=f"reactivate_{plan['id']}"):
                            db.update_support_plan_status(plan['id'], 'Active')
                            st.rerun()

    with tab2:
        st.subheader("📝 Create New Support Plan")

        core_interns = db.get_core_interns()

        if not core_interns:
            st.warning("No Core Interns available")
            return

        with st.form("support_plan_form"):
            intern_name = st.selectbox(
                "Core Intern Needing Support",
                options=[intern['name'] for intern in core_interns]
            )

            selected_intern = next((i for i in core_interns if i['name'] == intern_name), None)

            col1, col2 = st.columns(2)

            with col1:
                issue_challenge = st.text_area(
                    "Issue/Challenge",
                    placeholder="What's the challenge? (e.g., Low engagement on posts)"
                )

            with col2:
                goal = st.text_area(
                    "Goal",
                    placeholder="What's the goal? (e.g., Increase Reel engagement by 20%)"
                )

            action_steps = st.text_area(
                "Action Steps",
                placeholder="Specific steps to achieve goal:\n• Step 1\n• Step 2\n• Step 3"
            )

            check_in_date = st.date_input(
                "Check-In Date",
                value=date.today()
            )

            submit = st.form_submit_button("Create Support Plan", use_container_width=True)

            if submit:
                if selected_intern and issue_challenge and goal and action_steps:
                    success = db.create_support_plan(
                        lead_intern_id=user['id'],
                        core_intern_id=selected_intern['id'],
                        issue_challenge=issue_challenge,
                        goal=goal,
                        action_steps=action_steps,
                        check_in_date=check_in_date.strftime('%Y-%m-%d')
                    )

                    if success:
                        st.success("Support plan created! 💪")
                        st.rerun()
                    else:
                        st.error("Failed to create support plan")
                else:
                    st.warning("Please fill in all fields")

        # Resources
        st.divider()
        st.subheader("📚 Helpful Resources")

        st.write("""
        **Common Challenges & Solutions:**

        🔹 **Low Engagement**
        - Review best posting times
        - Improve hashtag strategy
        - Create more interactive content

        🔹 **Missing Deadlines**
        - Set phone reminders
        - Create content calendar
        - Break tasks into smaller steps

        🔹 **Technical Issues**
        - Pair with tech-savvy peer
        - Watch video tutorials
        - Provide step-by-step guides

        🔹 **Low Confidence**
        - Start with easier content
        - Celebrate small wins
        - Provide positive feedback
        """)

def track_wins(db: Database, user: dict):
    """Track and celebrate Core Intern wins"""
    st.header("🎉 Track Wins & Celebrate")

    tab1, tab2 = st.tabs(["Recent Wins", "Add New Win"])

    with tab1:
        st.subheader("⭐ Team Wins")

        wins = db.get_wins(lead_intern_id=user['id'])

        if not wins:
            st.info("No wins recorded yet. Start celebrating your team's achievements!")
        else:
            for win in wins:
                celebrated_emoji = "🎊" if win['celebrated'] else "⭐"

                with st.expander(f"{celebrated_emoji} {win['core_name']} - {win['win_date']}"):
                    st.write(f"**The Win:** {win['win_description']}")

                    if win['why_matters']:
                        st.write(f"**Why It Matters:** {win['why_matters']}")

                    if win['notes']:
                        st.write(f"**Notes:** {win['notes']}")

                    st.write(f"**Celebrated:** {'Yes! 🎉' if win['celebrated'] else 'Not yet'}")

                    if not win['celebrated']:
                        if st.button("Mark as Celebrated!", key=f"celebrate_win_{win['id']}"):
                            db.mark_win_celebrated(win['id'])
                            st.success("Celebrated! 🎉")
                            st.rerun()

    with tab2:
        st.subheader("✨ Add a New Win")

        core_interns = db.get_core_interns()

        if not core_interns:
            st.warning("No Core Interns available")
            return

        with st.form("win_form"):
            intern_name = st.selectbox(
                "Core Intern",
                options=[intern['name'] for intern in core_interns]
            )

            selected_intern = next((i for i in core_interns if i['name'] == intern_name), None)

            win_description = st.text_area(
                "The Win! 🌟",
                placeholder="Describe the achievement (e.g., Posted 2 amazing Reels with 500+ views each!)"
            )

            why_matters = st.text_area(
                "Why It Matters",
                placeholder="Why is this significant? (e.g., Met weekly goal and increased engagement)"
            )

            celebrated = st.checkbox("Already Celebrated?")

            notes = st.text_input(
                "Additional Notes",
                placeholder="Any other details..."
            )

            submit = st.form_submit_button("Add Win", use_container_width=True)

            if submit:
                if selected_intern and win_description:
                    success = db.add_win(
                        lead_intern_id=user['id'],
                        core_intern_id=selected_intern['id'],
                        win_description=win_description,
                        why_matters=why_matters,
                        celebrated=celebrated,
                        notes=notes
                    )

                    if success:
                        st.success("Win added! 🎉")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to add win")
                else:
                    st.warning("Please describe the win")

def view_reports(db: Database, user: dict):
    """View Core Intern reports and analytics"""
    st.header("📊 Team Reports")

    core_interns = db.get_core_interns()

    if not core_interns:
        st.info("No Core Interns to report on yet")
        return

    # Summary Stats
    st.subheader("📈 Team Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Core Interns", len(core_interns))

    with col2:
        total_reviews = len(db.get_core_reviews(lead_intern_id=user['id']))
        st.metric("Total Reviews", total_reviews)

    with col3:
        total_wins = len(db.get_wins(lead_intern_id=user['id']))
        st.metric("Total Wins", total_wins)

    with col4:
        active_support = len(db.get_support_plans(lead_intern_id=user['id'], status='Active'))
        st.metric("Active Support Plans", active_support)

    st.divider()

    # Individual Core Intern Reports
    st.subheader("👥 Individual Reports")

    for intern in core_interns:
        with st.expander(f"📋 {intern['name']} Report"):
            col1, col2 = st.columns(2)

            with col1:
                # Hours
                total_hours = db.get_total_hours(intern['id'])
                approved_hours = db.get_total_hours(intern['id'], approved_only=True)
                st.write(f"**Total Hours:** {total_hours:.1f}")
                st.write(f"**Approved Hours:** {approved_hours:.1f}")

                # Deliverables
                deliverables = db.get_user_deliverables(intern['id'])
                approved_deliverables = [d for d in deliverables if d['status'] == 'Approved']
                st.write(f"**Deliverables:** {len(deliverables)}")
                st.write(f"**Approved:** {len(approved_deliverables)}")

            with col2:
                # Reviews
                reviews = db.get_core_reviews(lead_intern_id=user['id'], core_intern_id=intern['id'])
                st.write(f"**Reviews Completed:** {len(reviews)}")

                if reviews:
                    latest = reviews[0]
                    st.write(f"**Latest Review:** {latest['review_date']}")
                    st.write(f"**Overall Vibe:** {latest['overall_vibe']}")

            # Wins
            intern_wins = db.get_wins(lead_intern_id=user['id'], core_intern_id=intern['id'])
            if intern_wins:
                st.write(f"**Recent Wins ({len(intern_wins)}):**")
                for win in intern_wins[:3]:
                    st.write(f"• {win['win_description']}")

    st.divider()

    # Export Options
    st.subheader("📥 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Review Summary", use_container_width=True):
            reviews = db.get_core_reviews(lead_intern_id=user['id'])
            if reviews:
                df = pd.DataFrame(reviews)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download Reviews CSV",
                    csv,
                    "core_reviews.csv",
                    "text/csv",
                    use_container_width=True
                )

    with col2:
        if st.button("Export Wins Report", use_container_width=True):
            wins = db.get_wins(lead_intern_id=user['id'])
            if wins:
                df = pd.DataFrame(wins)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download Wins CSV",
                    csv,
                    "team_wins.csv",
                    "text/csv",
                    use_container_width=True
                )