import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date, time as dt_time
from database import Database
from auth import Auth
from lead_intern_portal import lead_intern_dashboard
import io

# Page configuration
st.set_page_config(
    page_title="Intern Hour Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and auth
@st.cache_resource
def init_db():
    return Database()

db = init_db()
auth = Auth(db)
Auth.init_session_state()

# Schools list - Local Vallejo area schools
SCHOOLS = [
    "Vallejo High School",
    "Jesse Bethel High School",
    "Hogan High School",
    "St. Patrick-St. Vincent High School",
    "Solano Community College",
    "Napa Valley College",
    "California Maritime Academy",
    "Touro University California",
    "University of California, Berkeley",
    "University of California, Davis",
    "California State University, Sacramento",
    "San Francisco State University",
    "Other"
]

DELIVERABLE_TYPES = [
    "Reel",
    "IG Live",
    "Event",
    "Meeting",
    "Blog Post",
    "Social Media Post",
    "Video Content",
    "Other"
]

# Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B6B;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 0.25rem;
        color: #155724;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        border-radius: 0.25rem;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

def login_page():
    """Login and registration page"""
    st.markdown('<p class="main-header">🎓 Intern Hour Tracker</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Request Account"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if username and password:
                    if auth.login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")

    with tab2:
        st.subheader("Request New Account")
        with st.form("registration_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            school = st.selectbox("School", SCHOOLS)
            role = st.selectbox("Role", ["Core Intern", "Lead Intern"])

            st.info("Your account will be pending approval by an administrator. You will receive your login credentials once approved.")

            submit_request = st.form_submit_button("Submit Request", use_container_width=True)

            if submit_request:
                if name and email and school and role:
                    if db.create_account_request(name, email, school, role):
                        st.success("Account request submitted successfully! Please wait for admin approval.")
                    else:
                        st.error("Email already exists or request already submitted.")
                else:
                    st.warning("Please fill in all fields")

def admin_dashboard():
    """Admin dashboard with all management features"""
    st.title("Admin Dashboard")

    menu = st.sidebar.radio(
        "Admin Menu",
        ["Account Requests", "Manage Users", "Review Hours", "Review Deliverables", "Reports"]
    )

    if menu == "Account Requests":
        admin_account_requests()
    elif menu == "Manage Users":
        admin_manage_users()
    elif menu == "Review Hours":
        admin_review_hours()
    elif menu == "Review Deliverables":
        admin_review_deliverables()
    elif menu == "Reports":
        admin_reports()

def admin_account_requests():
    """Admin page to review and approve account requests"""
    st.header("Pending Account Requests")

    pending = db.get_pending_requests()

    if not pending:
        st.info("No pending account requests")
        return

    for request in pending:
        with st.expander(f"📝 {request['name']} - {request['email']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Name:** {request['name']}")
                st.write(f"**Email:** {request['email']}")
                st.write(f"**School:** {request['school']}")

            with col2:
                st.write(f"**Role:** {request['role']}")
                st.write(f"**Start Date:** {request['start_date']}")
                st.write(f"**Requested:** {request['created_at']}")

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                # Auto-generate username
                suggested_username = auth.generate_username(request['name'])
                username = st.text_input("Username", value=suggested_username, key=f"user_{request['id']}")

            with col2:
                # Auto-generate password
                suggested_password = auth.generate_password()
                password = st.text_input("Password", value=suggested_password, key=f"pass_{request['id']}")

            with col3:
                st.write("")
                st.write("")

            col_approve, col_reject = st.columns(2)

            with col_approve:
                if st.button("✅ Approve", key=f"approve_{request['id']}", use_container_width=True):
                    if db.approve_account(request['id'], username, password):
                        st.success(f"Account approved! Username: {username}, Password: {password}")
                        st.info("Please share these credentials with the intern securely.")
                        st.rerun()
                    else:
                        st.error("Username already exists. Please choose a different username.")

            with col_reject:
                if st.button("❌ Reject", key=f"reject_{request['id']}", use_container_width=True):
                    if db.reject_account(request['id']):
                        st.success("Account request rejected")
                        st.rerun()

            st.divider()

def admin_manage_users():
    """Admin page to manage user accounts"""
    st.header("Manage User Accounts")

    users = db.get_all_users()

    if not users:
        st.info("No active users")
        return

    df = pd.DataFrame(users)
    st.dataframe(df, use_container_width=True)

    st.subheader("User Actions")

    for user in users:
        with st.expander(f"{user['name']} - {user['email']}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Role:** {user['role']}")
                st.write(f"**School:** {user['school']}")

            with col2:
                st.write(f"**Status:** {user['status']}")
                st.write(f"**Start Date:** {user['start_date']}")

            with col3:
                total_hours = db.get_total_hours(user['id'])
                approved_hours = db.get_total_hours(user['id'], approved_only=True)
                st.metric("Total Hours", f"{total_hours:.1f}")
                st.metric("Approved Hours", f"{approved_hours:.1f}")

            if user['status'] == 'Active':
                if st.button("🔒 Deactivate", key=f"deactivate_{user['id']}"):
                    db.toggle_user_status(user['id'], 'Inactive')
                    st.success(f"User {user['name']} deactivated")
                    st.rerun()
            else:
                if st.button("🔓 Activate", key=f"activate_{user['id']}"):
                    db.toggle_user_status(user['id'], 'Active')
                    st.success(f"User {user['name']} activated")
                    st.rerun()

def admin_review_hours():
    """Admin page to review and approve hours"""
    st.header("Review Hours")

    tab1, tab2 = st.tabs(["Pending Hours", "All Hours"])

    with tab1:
        all_hours = db.get_all_hours()
        pending_hours = [h for h in all_hours if not h['approved']]

        if not pending_hours:
            st.info("No pending hours to review")
        else:
            for hour in pending_hours:
                with st.expander(f"📅 {hour['user_name']} - {hour['date']} ({hour['total_hours']}h)"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Intern:** {hour['user_name']}")
                        st.write(f"**Date:** {hour['date']}")
                        st.write(f"**Time:** {hour['start_time']} - {hour['end_time']}")

                    with col2:
                        st.write(f"**Total Hours:** {hour['total_hours']}")
                        st.write(f"**Submitted:** {hour['created_at']}")

                    st.write(f"**Description:** {hour['description']}")

                    col_approve, col_reject = st.columns(2)

                    with col_approve:
                        if st.button("✅ Approve", key=f"approve_hour_{hour['id']}", use_container_width=True):
                            db.approve_hours(hour['id'], True)
                            st.success("Hours approved")
                            st.rerun()

                    with col_reject:
                        if st.button("❌ Reject", key=f"reject_hour_{hour['id']}", use_container_width=True):
                            db.approve_hours(hour['id'], False)
                            st.success("Hours rejected")
                            st.rerun()

    with tab2:
        all_hours = db.get_all_hours()
        if all_hours:
            df = pd.DataFrame(all_hours)
            df['approved'] = df['approved'].apply(lambda x: '✅ Approved' if x else '❌ Pending')
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hours logged yet")

def admin_review_deliverables():
    """Admin page to review deliverables"""
    st.header("Review Deliverables")

    tab1, tab2 = st.tabs(["Pending Deliverables", "All Deliverables"])

    with tab1:
        pending = db.get_pending_deliverables()

        if not pending:
            st.info("No pending deliverables to review")
        else:
            for deliv in pending:
                with st.expander(f"📦 {deliv['user_name']} - {deliv['type']}", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Intern:** {deliv['user_name']}")
                        st.write(f"**Type:** {deliv['type']}")
                        st.write(f"**Submitted:** {deliv['submitted_at']}")

                    with col2:
                        st.write(f"**Status:** {deliv['status']}")

                    st.write(f"**Description:** {deliv['description']}")

                    if deliv['links']:
                        st.write(f"**Links:** {deliv['links']}")

                    if deliv['proof_links']:
                        st.write(f"**Proof Links:** {deliv['proof_links']}")

                    admin_comments = st.text_area("Admin Comments", key=f"comments_{deliv['id']}")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if st.button("✅ Approve", key=f"approve_deliv_{deliv['id']}", use_container_width=True):
                            db.update_deliverable_status(deliv['id'], 'Approved', admin_comments)
                            st.success("Deliverable approved")
                            st.rerun()

                    with col2:
                        if st.button("📝 Needs Revision", key=f"revision_{deliv['id']}", use_container_width=True):
                            db.update_deliverable_status(deliv['id'], 'Needs Revision', admin_comments)
                            st.success("Status updated")
                            st.rerun()

                    with col3:
                        if st.button("❌ Reject", key=f"reject_deliv_{deliv['id']}", use_container_width=True):
                            db.update_deliverable_status(deliv['id'], 'Rejected', admin_comments)
                            st.success("Deliverable rejected")
                            st.rerun()

                    st.divider()

    with tab2:
        all_deliverables = db.get_all_deliverables()
        if all_deliverables:
            df = pd.DataFrame(all_deliverables)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No deliverables submitted yet")

def admin_reports():
    """Admin reports page"""
    st.header("Reports")

    all_users = db.get_all_users()

    if not all_users:
        st.info("No users to generate reports")
        return

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Interns", len(all_users))

    with col2:
        total_hours = sum(db.get_total_hours(u['id']) for u in all_users)
        st.metric("Total Hours Logged", f"{total_hours:.1f}")

    with col3:
        all_deliverables = db.get_all_deliverables()
        st.metric("Total Deliverables", len(all_deliverables))

    with col4:
        pending_deliverables = db.get_pending_deliverables()
        st.metric("Pending Reviews", len(pending_deliverables))

    st.divider()

    # Hours by intern
    st.subheader("Hours by Intern")

    hours_data = []
    for user in all_users:
        total = db.get_total_hours(user['id'])
        approved = db.get_total_hours(user['id'], approved_only=True)
        pending = total - approved

        hours_data.append({
            'Name': user['name'],
            'Role': user['role'],
            'School': user['school'],
            'Total Hours': total,
            'Approved Hours': approved,
            'Pending Hours': pending
        })

    hours_df = pd.DataFrame(hours_data)
    st.dataframe(hours_df, use_container_width=True)

    # Export data
    st.subheader("Export Data")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export Hours Data", use_container_width=True):
            all_hours = db.get_all_hours()
            if all_hours:
                df = pd.DataFrame(all_hours)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download Hours CSV",
                    csv,
                    "intern_hours.csv",
                    "text/csv",
                    use_container_width=True
                )

    with col2:
        if st.button("📥 Export Deliverables Data", use_container_width=True):
            all_deliverables = db.get_all_deliverables()
            if all_deliverables:
                df = pd.DataFrame(all_deliverables)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download Deliverables CSV",
                    csv,
                    "intern_deliverables.csv",
                    "text/csv",
                    use_container_width=True
                )

def intern_dashboard():
    """Intern dashboard"""
    user = auth.get_current_user()
    st.title(f"Welcome, {user['name']}!")

    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Log Hours", "Submit Deliverables", "View History"]
    )

    if menu == "Dashboard":
        intern_home()
    elif menu == "Log Hours":
        intern_log_hours()
    elif menu == "Submit Deliverables":
        intern_submit_deliverables()
    elif menu == "View History":
        intern_view_history()

def intern_home():
    """Intern home dashboard"""
    user = auth.get_current_user()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_hours = db.get_total_hours(user['id'])
        st.metric("Total Hours", f"{total_hours:.1f}")

    with col2:
        approved_hours = db.get_total_hours(user['id'], approved_only=True)
        st.metric("Approved Hours", f"{approved_hours:.1f}")

    with col3:
        deliverables = db.get_user_deliverables(user['id'])
        st.metric("Deliverables Submitted", len(deliverables))

    st.divider()

    # Recent hours
    st.subheader("Recent Hours (Last 7 Days)")
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    recent_hours = db.get_user_hours(user['id'], start_date=week_ago)

    if recent_hours:
        df = pd.DataFrame(recent_hours)
        df['approved'] = df['approved'].apply(lambda x: '✅ Approved' if x else '⏳ Pending')
        st.dataframe(df[['date', 'start_time', 'end_time', 'total_hours', 'description', 'approved']], use_container_width=True)
    else:
        st.info("No hours logged in the last 7 days")

    st.divider()

    # Recent deliverables
    st.subheader("Recent Deliverables")
    deliverables = db.get_user_deliverables(user['id'])

    if deliverables[:5]:
        for deliv in deliverables[:5]:
            status_emoji = {
                'Pending': '⏳',
                'Approved': '✅',
                'Needs Revision': '📝',
                'Rejected': '❌'
            }
            emoji = status_emoji.get(deliv['status'], '📦')

            with st.expander(f"{emoji} {deliv['type']} - {deliv['status']}"):
                st.write(f"**Description:** {deliv['description']}")
                st.write(f"**Submitted:** {deliv['submitted_at']}")
                if deliv['admin_comments']:
                    st.write(f"**Admin Comments:** {deliv['admin_comments']}")
    else:
        st.info("No deliverables submitted yet")

def intern_log_hours():
    """Intern page to log hours"""
    st.header("Log Work Hours")

    user = auth.get_current_user()

    with st.form("log_hours_form"):
        col1, col2 = st.columns(2)

        with col1:
            work_date = st.date_input("Date", value=date.today(), max_value=date.today())
            start_time = st.time_input("Start Time", value=dt_time(9, 0))

        with col2:
            st.write("")
            st.write("")
            end_time = st.time_input("End Time", value=dt_time(17, 0))

        description = st.text_area("Work Description", placeholder="Describe what you worked on...")

        submit = st.form_submit_button("Submit Hours", use_container_width=True)

        if submit:
            if description:
                # Calculate total hours
                start_dt = datetime.combine(work_date, start_time)
                end_dt = datetime.combine(work_date, end_time)

                if end_dt <= start_dt:
                    st.error("End time must be after start time")
                else:
                    total_hours = (end_dt - start_dt).total_seconds() / 3600

                    if db.log_hours(
                        user['id'],
                        work_date.strftime('%Y-%m-%d'),
                        start_time.strftime('%H:%M'),
                        end_time.strftime('%H:%M'),
                        total_hours,
                        description
                    ):
                        st.success(f"Hours logged successfully! Total: {total_hours:.2f} hours")
                        st.rerun()
                    else:
                        st.error("Failed to log hours. Please try again.")
            else:
                st.warning("Please provide a work description")

def intern_submit_deliverables():
    """Intern page to submit deliverables"""
    st.header("Submit Deliverables")

    user = auth.get_current_user()

    with st.form("submit_deliverable_form"):
        deliv_type = st.selectbox("Deliverable Type", DELIVERABLE_TYPES)

        description = st.text_area("Description", placeholder="Describe your deliverable...")

        links = st.text_input("Material Links", placeholder="Google Drive, social media links, etc.")

        proof_links = st.text_area(
            "Proof of Work Links",
            placeholder="Screenshots, additional documentation links..."
        )

        submit = st.form_submit_button("Submit Deliverable", use_container_width=True)

        if submit:
            if description:
                if db.submit_deliverable(user['id'], deliv_type, description, links, proof_links):
                    st.success("Deliverable submitted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to submit deliverable. Please try again.")
            else:
                st.warning("Please provide a description")

def intern_view_history():
    """Intern page to view history"""
    st.header("My History")

    user = auth.get_current_user()

    tab1, tab2 = st.tabs(["Hours History", "Deliverables History"])

    with tab1:
        st.subheader("Hours History")

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("From Date", value=date.today() - timedelta(days=30))

        with col2:
            end_date = st.date_input("To Date", value=date.today())

        hours = db.get_user_hours(
            user['id'],
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        if hours:
            df = pd.DataFrame(hours)
            df['approved'] = df['approved'].apply(lambda x: '✅ Approved' if x else '⏳ Pending')
            st.dataframe(df[['date', 'start_time', 'end_time', 'total_hours', 'description', 'approved']], use_container_width=True)

            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Export to CSV",
                csv,
                "my_hours.csv",
                "text/csv",
                use_container_width=False
            )
        else:
            st.info("No hours logged in this date range")

    with tab2:
        st.subheader("Deliverables History")

        deliverables = db.get_user_deliverables(user['id'])

        if deliverables:
            for deliv in deliverables:
                status_color = {
                    'Pending': '🟡',
                    'Approved': '🟢',
                    'Needs Revision': '🟠',
                    'Rejected': '🔴'
                }
                color = status_color.get(deliv['status'], '⚪')

                with st.expander(f"{color} {deliv['type']} - {deliv['submitted_at']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Type:** {deliv['type']}")
                        st.write(f"**Status:** {deliv['status']}")

                    with col2:
                        st.write(f"**Submitted:** {deliv['submitted_at']}")
                        if deliv['reviewed_at']:
                            st.write(f"**Reviewed:** {deliv['reviewed_at']}")

                    st.write(f"**Description:** {deliv['description']}")

                    if deliv['links']:
                        st.write(f"**Links:** {deliv['links']}")

                    if deliv['proof_links']:
                        st.write(f"**Proof:** {deliv['proof_links']}")

                    if deliv['admin_comments']:
                        st.info(f"**Admin Comments:** {deliv['admin_comments']}")
        else:
            st.info("No deliverables submitted yet")

def main():
    """Main application logic"""
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Club+Stride", use_container_width=True)
        st.title("Navigation")

        if auth.is_authenticated():
            user = auth.get_current_user()
            st.success(f"Logged in as: {user['name']}")
            st.write(f"Role: {user['role']}")

            if st.button("🚪 Logout", use_container_width=True):
                auth.logout()
                st.rerun()
        else:
            st.info("Please login to continue")

    # Main content
    if not auth.is_authenticated():
        login_page()
    else:
        user = auth.get_current_user()
        if auth.is_admin():
            admin_dashboard()
        elif user['role'] == 'Lead Intern':
            lead_intern_dashboard(db, auth)
        else:
            intern_dashboard()

if __name__ == "__main__":
    main()