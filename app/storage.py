"""
File-based storage system for OptiHire
Replaces database with JSON file storage
Includes: file locking, analytics aggregation, notification management
"""
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

# Thread-level lock for in-process concurrency protection
_file_lock = threading.Lock()


class FileStorage:
    """File-based storage using JSON files with thread-safe read/write"""

    def __init__(self, data_dir: str = None):
        """Initialize storage with data directory"""
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        self.data_dir = os.path.abspath(data_dir)
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.jobs_file = os.path.join(self.data_dir, 'jobs.json')
        self.resumes_file = os.path.join(self.data_dir, 'resumes.json')
        self.applications_file = os.path.join(self.data_dir, 'applications.json')
        self.notifications_file = os.path.join(self.data_dir, 'notifications.json')

        os.makedirs(self.data_dir, exist_ok=True)
        self._initialize_files()

    def _initialize_files(self):
        """Create empty JSON files if they don't exist"""
        for file_path in [
            self.users_file, self.jobs_file, self.resumes_file,
            self.applications_file, self.notifications_file
        ]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)

    def _read_file(self, file_path: str) -> List[Dict]:
        """Read JSON file and return list of records"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_file(self, file_path: str, data: List[Dict]):
        """Write data to JSON file atomically"""
        tmp_path = file_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp_path, file_path)  # atomic replace

    def _generate_id(self) -> str:
        """Generate unique short ID"""
        return str(uuid.uuid4())[:8]

    # ─────────────────────────────────────────
    # User operations
    # ─────────────────────────────────────────

    def create_user(self, user_data: Dict) -> Dict:
        """Create new user"""
        with _file_lock:
            users = self._read_file(self.users_file)
            user_data['id'] = self._generate_id()
            user_data['created_at'] = datetime.now().isoformat()
            user_data['is_active'] = True
            users.append(user_data)
            self._write_file(self.users_file, users)
        return user_data

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self._read_file(self.users_file)
        for user in users:
            if user.get('email', '').lower() == email.lower():
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        users = self._read_file(self.users_file)
        for user in users:
            if user.get('id') == user_id:
                return user
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        users = self._read_file(self.users_file)
        for user in users:
            if user.get('username', '').lower() == username.lower():
                return user
        return None

    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user record by ID"""
        with _file_lock:
            users = self._read_file(self.users_file)
            for i, user in enumerate(users):
                if user.get('id') == user_id:
                    users[i].update(updates)
                    users[i]['updated_at'] = datetime.now().isoformat()
                    self._write_file(self.users_file, users)
                    return True
        return False

    # ─────────────────────────────────────────
    # Job operations
    # ─────────────────────────────────────────

    def create_job(self, job_data: Dict) -> Dict:
        """Create new job posting"""
        with _file_lock:
            jobs = self._read_file(self.jobs_file)
            job_data['id'] = self._generate_id()
            job_data['created_at'] = datetime.now().isoformat()
            job_data['updated_at'] = datetime.now().isoformat()
            job_data['is_active'] = True
            jobs.append(job_data)
            self._write_file(self.jobs_file, jobs)
        return job_data

    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        jobs = self._read_file(self.jobs_file)
        for job in jobs:
            if job.get('id') == job_id:
                return job
        return None

    def get_all_jobs(self, active_only: bool = True) -> List[Dict]:
        """Get all jobs"""
        jobs = self._read_file(self.jobs_file)
        if active_only:
            return [job for job in jobs if job.get('is_active', True)]
        return jobs

    def get_jobs_by_recruiter(self, recruiter_id: str) -> List[Dict]:
        """Get jobs by recruiter ID"""
        jobs = self._read_file(self.jobs_file)
        return [job for job in jobs if job.get('recruiter_id') == recruiter_id]

    def update_job(self, job_id: str, updates: Dict) -> bool:
        """Update job"""
        with _file_lock:
            jobs = self._read_file(self.jobs_file)
            for i, job in enumerate(jobs):
                if job.get('id') == job_id:
                    jobs[i].update(updates)
                    jobs[i]['updated_at'] = datetime.now().isoformat()
                    self._write_file(self.jobs_file, jobs)
                    return True
        return False

    def delete_job(self, job_id: str) -> bool:
        """Soft delete job (mark as inactive)"""
        return self.update_job(job_id, {'is_active': False})

    # ─────────────────────────────────────────
    # Resume operations
    # ─────────────────────────────────────────

    def create_resume(self, resume_data: Dict) -> Dict:
        """Create new resume"""
        with _file_lock:
            resumes = self._read_file(self.resumes_file)
            resume_data['id'] = self._generate_id()
            resume_data['created_at'] = datetime.now().isoformat()
            resume_data['updated_at'] = datetime.now().isoformat()
            resumes.append(resume_data)
            self._write_file(self.resumes_file, resumes)
        return resume_data

    def get_resume_by_id(self, resume_id: str) -> Optional[Dict]:
        """Get resume by ID"""
        resumes = self._read_file(self.resumes_file)
        for resume in resumes:
            if resume.get('id') == resume_id:
                return resume
        return None

    def get_resumes_by_user(self, user_id: str) -> List[Dict]:
        """Get resumes by user ID"""
        resumes = self._read_file(self.resumes_file)
        return [r for r in resumes if r.get('user_id') == user_id]

    # ─────────────────────────────────────────
    # Application operations
    # ─────────────────────────────────────────

    def create_application(self, app_data: Dict) -> Dict:
        """Create new application"""
        with _file_lock:
            applications = self._read_file(self.applications_file)
            app_data['id'] = self._generate_id()
            app_data['applied_at'] = datetime.now().isoformat()
            app_data['updated_at'] = datetime.now().isoformat()
            app_data['status'] = app_data.get('status', 'pending')
            applications.append(app_data)
            self._write_file(self.applications_file, applications)
        return app_data

    def get_application_by_id(self, app_id: str) -> Optional[Dict]:
        """Get application by ID"""
        applications = self._read_file(self.applications_file)
        for app in applications:
            if app.get('id') == app_id:
                return app
        return None

    def get_applications_by_candidate(self, candidate_id: str) -> List[Dict]:
        """Get applications by candidate ID"""
        applications = self._read_file(self.applications_file)
        return [app for app in applications if app.get('candidate_id') == candidate_id]

    def get_applications_by_job(self, job_id: str) -> List[Dict]:
        """Get applications by job ID"""
        applications = self._read_file(self.applications_file)
        return [app for app in applications if app.get('job_id') == job_id]

    def get_existing_application(self, job_id: str, candidate_id: str) -> Optional[Dict]:
        """Check if application already exists"""
        applications = self._read_file(self.applications_file)
        for app in applications:
            if app.get('job_id') == job_id and app.get('candidate_id') == candidate_id:
                return app
        return None

    def update_application(self, app_id: str, updates: Dict) -> bool:
        """Update application"""
        with _file_lock:
            applications = self._read_file(self.applications_file)
            for i, app in enumerate(applications):
                if app.get('id') == app_id:
                    applications[i].update(updates)
                    applications[i]['updated_at'] = datetime.now().isoformat()
                    self._write_file(self.applications_file, applications)
                    return True
        return False

    # ─────────────────────────────────────────
    # Notification operations
    # ─────────────────────────────────────────

    def create_notification(self, notif_data: Dict) -> Dict:
        """Create new notification"""
        with _file_lock:
            notifications = self._read_file(self.notifications_file)
            notif_data['id'] = self._generate_id()
            notif_data['created_at'] = datetime.now().isoformat()
            notif_data['is_read'] = False
            notifications.append(notif_data)
            self._write_file(self.notifications_file, notifications)
        return notif_data

    def get_notifications_by_user(self, user_id: str, unread_only: bool = False) -> List[Dict]:
        """Get notifications by user ID"""
        notifications = self._read_file(self.notifications_file)
        user_notifs = [n for n in notifications if n.get('user_id') == user_id]
        if unread_only:
            return [n for n in user_notifs if not n.get('is_read', False)]
        return user_notifs

    def mark_notification_read(self, notif_id: str) -> bool:
        """Mark a single notification as read"""
        with _file_lock:
            notifications = self._read_file(self.notifications_file)
            for i, n in enumerate(notifications):
                if n.get('id') == notif_id:
                    notifications[i]['is_read'] = True
                    self._write_file(self.notifications_file, notifications)
                    return True
        return False

    def mark_all_notifications_read(self, user_id: str) -> int:
        """Mark all user's notifications as read, returns count updated"""
        with _file_lock:
            notifications = self._read_file(self.notifications_file)
            count = 0
            for i, n in enumerate(notifications):
                if n.get('user_id') == user_id and not n.get('is_read', False):
                    notifications[i]['is_read'] = True
                    count += 1
            if count:
                self._write_file(self.notifications_file, notifications)
        return count

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        notifications = self._read_file(self.notifications_file)
        return sum(
            1 for n in notifications
            if n.get('user_id') == user_id and not n.get('is_read', False)
        )

    # ─────────────────────────────────────────
    # Search operations
    # ─────────────────────────────────────────

    def search_jobs(self, query: str) -> List[Dict]:
        """Search jobs by title, company, description or skills"""
        jobs = self.get_all_jobs(active_only=True)
        query_lower = query.lower()
        results = []
        for job in jobs:
            if (query_lower in job.get('title', '').lower() or
                    query_lower in job.get('company', '').lower() or
                    query_lower in job.get('description', '').lower() or
                    query_lower in job.get('skills_required', '').lower()):
                results.append(job)
        return results

    # ─────────────────────────────────────────
    # Analytics aggregation
    # ─────────────────────────────────────────

    def analytics_summary(self, recruiter_id: str = None) -> Dict:
        """
        Compute aggregate analytics for the analytics dashboard.
        If recruiter_id given, scopes to that recruiter's jobs.
        """
        all_jobs = self._read_file(self.jobs_file)
        all_applications = self._read_file(self.applications_file)

        if recruiter_id:
            job_ids = {j['id'] for j in all_jobs if j.get('recruiter_id') == recruiter_id}
            applications = [a for a in all_applications if a.get('job_id') in job_ids]
            jobs = [j for j in all_jobs if j.get('recruiter_id') == recruiter_id]
        else:
            applications = all_applications
            jobs = all_jobs

        # Score distribution
        scores = [a.get('similarity_score', 0) * 100 for a in applications if a.get('similarity_score') is not None]
        score_mean = round(sum(scores) / len(scores), 1) if scores else 0
        score_median = round(sorted(scores)[len(scores) // 2], 1) if scores else 0
        score_std = 0
        if len(scores) > 1:
            mean = sum(scores) / len(scores)
            score_std = round((sum((s - mean) ** 2 for s in scores) / len(scores)) ** 0.5, 1)

        # Score buckets for histogram (0-10, 10-20, ..., 90-100)
        buckets = [0] * 10
        for s in scores:
            idx = min(int(s // 10), 9)
            buckets[idx] += 1

        # Status breakdown
        status_counts = {}
        for app in applications:
            status = app.get('status', 'pending')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Active vs inactive jobs count
        active_jobs = sum(1 for j in jobs if j.get('is_active', True))

        return {
            'total_jobs': len(jobs),
            'active_jobs': active_jobs,
            'total_applications': len(applications),
            'score_mean': score_mean,
            'score_median': score_median,
            'score_std': score_std,
            'score_buckets': buckets,
            'score_labels': ['0-10', '10-20', '20-30', '30-40', '40-50',
                             '50-60', '60-70', '70-80', '80-90', '90-100'],
            'status_counts': status_counts,
        }


# ─────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────
_storage_instance = None


def get_storage() -> FileStorage:
    """Get or create storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = FileStorage()
    return _storage_instance
