# 🎓 Intern Hour Tracker & Deliverables Management System

A comprehensive Streamlit application for tracking intern hours, managing deliverables, and facilitating admin oversight with SQLite database integration, containerized with Docker for easy deployment.

## 🌟 Features

### For Interns
- **Account Registration**: Submit account requests with automatic approval workflow
- **Hour Tracking**: Log work sessions with date, time, and descriptions
- **Deliverables Submission**: Submit weekly deliverables with proof of work
- **Personal Dashboard**: View hour totals, approval status, and submission history
- **Export Functionality**: Download personal hours and deliverables data

### For Admins
- **Account Management**: Approve/reject account requests and manage user status
- **Hours Review**: Review and approve/reject submitted hours
- **Deliverables Review**: Review deliverables with commenting system
- **Comprehensive Reports**: Generate reports on intern activity and progress
- **Data Export**: Export all data to CSV for further analysis

## 🏗️ Project Structure

```
intern-tracker/
├── app.py                      # Main Streamlit application
├── database.py                 # Database operations and schema
├── auth.py                     # Authentication and session management
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose for local development
├── .dockerignore              # Docker ignore file
├── .gitignore                 # Git ignore file
├── README.md                  # This file
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml.example   # Example secrets file
└── data/
    └── intern_tracker.db      # SQLite database (auto-created)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd tracker
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv intern_tracker_env

# Activate on Windows
intern_tracker_env\Scripts\activate

# Activate on Mac/Linux
source intern_tracker_env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Access the application**
Open your browser and navigate to `http://localhost:8501`

### Default Admin Credentials
- **Email**: admin@clubstride.org
- **Username**: admin123
- **Password**: admin123456

⚠️ **Security Note**: Change the admin password immediately after first login in production!

## 🐳 Docker Deployment

### Build and Run with Docker

1. **Build the Docker image**
```bash
docker build -t intern-tracker .
```

2. **Run the container**
```bash
docker run -p 8501:8501 -v $(pwd)/data:/app/data intern-tracker
```

### Using Docker Compose (Recommended)

1. **Start the application**
```bash
docker-compose up -d
```

2. **View logs**
```bash
docker-compose logs -f
```

3. **Stop the application**
```bash
docker-compose down
```

4. **Access the application**
Open your browser and navigate to `http://localhost:8501`

## ☁️ Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Deployment Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select your repository and branch
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (Optional)
   - In Streamlit Cloud dashboard, go to your app settings
   - Click "Secrets"
   - Add any environment-specific secrets:
   ```toml
   [database]
   path = "data/intern_tracker.db"

   [admin]
   email = "admin@clubstride.org"
   username = "admin123"
   password = "admin123456"

   [session]
   secret_key = "your-production-secret-key"
   ```

4. **Access your deployed app**
   - Your app will be available at `https://[your-app-name].streamlit.app`

## 📊 Database Schema

### Users Table
```sql
- id: Primary key
- name: Full name
- email: Email address (unique)
- username: Login username (unique)
- school: School name
- role: Core Intern | Lead Intern | Admin
- start_date: Start date
- status: Pending Approval | Active | Inactive
- auth_hash: Bcrypt password hash
- created_at: Account creation timestamp
```

### Hours Table
```sql
- id: Primary key
- user_id: Foreign key to users
- date: Work date
- start_time: Start time
- end_time: End time
- total_hours: Calculated hours
- description: Work description
- approved: Boolean approval status
- created_at: Submission timestamp
```

### Deliverables Table
```sql
- id: Primary key
- user_id: Foreign key to users
- type: Deliverable type (Reel, IG Live, Event, etc.)
- description: Deliverable description
- links: Material links
- proof_links: Proof of work links
- status: Pending | Approved | Needs Revision | Rejected
- admin_comments: Admin feedback
- submitted_at: Submission timestamp
- reviewed_at: Review timestamp
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt encryption for all passwords
- **Session Management**: Secure session state handling
- **Rate Limiting**: Login attempt throttling
- **Role-Based Access**: Separate admin and intern permissions
- **Input Validation**: Server-side validation for all inputs

## 📝 Usage Guide

### For Interns

1. **Create Account**
   - Go to "Request Account" tab
   - Fill in your information
   - Wait for admin approval

2. **Log Hours**
   - Navigate to "Log Hours"
   - Enter date, start/end times, and work description
   - Submit for admin approval

3. **Submit Deliverables**
   - Go to "Submit Deliverables"
   - Select deliverable type
   - Add description and links
   - Include proof of work

4. **View History**
   - Check "View History" for all submissions
   - Filter by date range
   - Export your data to CSV

### For Admins

1. **Approve Accounts**
   - Review pending requests in "Account Requests"
   - Generate credentials (auto-suggested)
   - Approve or reject requests

2. **Review Hours**
   - Check "Review Hours" for pending submissions
   - Review work descriptions
   - Approve or reject hours

3. **Review Deliverables**
   - Navigate to "Review Deliverables"
   - Review submission details and proof
   - Add comments and update status

4. **Generate Reports**
   - Access "Reports" section
   - View summary statistics
   - Export data for analysis

## 🛠️ Configuration

### Streamlit Configuration
Edit `.streamlit/config.toml` to customize:
- Server settings (port, CORS, etc.)
- Theme colors
- Browser behavior
- Performance settings

### Environment Variables
For production deployment, set:
- `STREAMLIT_SERVER_PORT`: Server port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)
- Database path in secrets or environment

## 📦 Dependencies

```
streamlit>=1.30.0    # Web framework
pandas>=2.0.0        # Data manipulation
bcrypt>=4.0.0        # Password hashing
python-dotenv>=1.0.0 # Environment variables
```

## 🐛 Troubleshooting

### Database Issues
- **Database locked**: Ensure only one instance is running
- **Permission denied**: Check data directory permissions
- **Database not found**: Application auto-creates on first run

### Docker Issues
- **Port already in use**: Change port in docker-compose.yml
- **Volume mount fails**: Check path permissions
- **Container won't start**: Check logs with `docker-compose logs`

### Streamlit Cloud Issues
- **App won't deploy**: Check requirements.txt for all dependencies
- **Database persistence**: Use Streamlit secrets for configuration
- **Slow performance**: Optimize queries or upgrade plan

## 🔄 Database Backup

### Manual Backup
```bash
# Copy database file
cp data/intern_tracker.db data/backup_$(date +%Y%m%d).db
```

### Automated Backup Script
```bash
#!/bin/bash
# Add to cron for automated backups
DATE=$(date +%Y%m%d_%H%M%S)
cp data/intern_tracker.db backups/intern_tracker_$DATE.db
find backups/ -mtime +30 -delete  # Keep last 30 days
```

## 📈 Future Enhancements

- [ ] Email notifications for approvals
- [ ] Calendar integration for work schedules
- [ ] Mobile responsive design improvements
- [ ] Advanced analytics dashboard
- [ ] Multi-organization support
- [ ] API endpoints for integrations
- [ ] Automated reminders for submissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Contact: admin@clubstride.org

## 🎯 Version

Current Version: 1.0.0

---

Built with ❤️ using Streamlit, Python, and SQLite