"""
Data Analyzer
Provides statistics and analytics about bot operations
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

from database import SessionLocal, Account, Task, Rating, ActivityLog
from database.models import AccountStatus, TaskStatus


class DataAnalyzer:
    """
    Analyzes bot data and provides insights
    """
    
    def __init__(self):
        pass
    
    def get_dashboard_stats(self) -> Dict:
        """Get complete dashboard statistics"""
        db = SessionLocal()
        try:
            # Account statistics
            total_accounts = db.query(Account).count()
            active_accounts = db.query(Account).filter(Account.status == AccountStatus.ACTIVE).count()
            ready_accounts = db.query(Account).filter(Account.status == AccountStatus.READY).count()
            maturing_accounts = db.query(Account).filter(Account.status == AccountStatus.MATURING).count()
            banned_accounts = db.query(Account).filter(Account.status == AccountStatus.BANNED).count()
            
            # Task statistics
            total_tasks = db.query(Task).count()
            pending_tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).count()
            running_tasks = db.query(Task).filter(Task.status == TaskStatus.RUNNING).count()
            completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
            failed_tasks = db.query(Task).filter(Task.status == TaskStatus.FAILED).count()
            
            # Rating statistics
            total_ratings = db.query(Rating).count()
            successful_ratings = db.query(Rating).filter(Rating.status == "success").count()
            failed_ratings = db.query(Rating).filter(Rating.status == "failed").count()
            
            # Calculate rates
            success_rate = (successful_ratings / total_ratings * 100) if total_ratings > 0 else 0
            ban_rate = (banned_accounts / total_accounts * 100) if total_accounts > 0 else 0
            
            return {
                "accounts": {
                    "total": total_accounts,
                    "active": active_accounts,
                    "ready": ready_accounts,
                    "maturing": maturing_accounts,
                    "banned": banned_accounts,
                    "ban_rate": round(ban_rate, 2),
                },
                "tasks": {
                    "total": total_tasks,
                    "pending": pending_tasks,
                    "running": running_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks,
                    "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
                },
                "ratings": {
                    "total": total_ratings,
                    "successful": successful_ratings,
                    "failed": failed_ratings,
                    "success_rate": round(success_rate, 2),
                },
            }
        finally:
            db.close()
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily statistics for the past N days"""
        db = SessionLocal()
        try:
            daily_stats = []
            today = datetime.now().date()
            
            for i in range(days):
                date = today - timedelta(days=i)
                start = datetime.combine(date, datetime.min.time())
                end = datetime.combine(date, datetime.max.time())
                
                # Accounts created
                accounts_created = db.query(Account).filter(
                    Account.created_at.between(start, end)
                ).count()
                
                # Ratings submitted
                ratings_submitted = db.query(Rating).filter(
                    Rating.submitted_at.between(start, end)
                ).count()
                
                # Successful ratings
                ratings_success = db.query(Rating).filter(
                    Rating.submitted_at.between(start, end),
                    Rating.status == "success"
                ).count()
                
                # Tasks completed
                tasks_completed = db.query(Task).filter(
                    Task.completed_at.between(start, end),
                    Task.status == TaskStatus.COMPLETED
                ).count()
                
                daily_stats.append({
                    "date": date.isoformat(),
                    "accounts_created": accounts_created,
                    "ratings_submitted": ratings_submitted,
                    "ratings_success": ratings_success,
                    "tasks_completed": tasks_completed,
                })
            
            return daily_stats
        finally:
            db.close()
    
    def get_account_performance(self, limit: int = 10) -> List[Dict]:
        """Get top performing accounts"""
        db = SessionLocal()
        try:
            accounts = db.query(Account).filter(
                Account.status.in_([AccountStatus.ACTIVE, AccountStatus.READY])
            ).order_by(
                Account.total_ratings_given.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": acc.id,
                    "name": acc.display_name,
                    "ratings": acc.total_ratings_given,
                    "comments": acc.total_comments_made,
                    "likes": acc.total_likes_given,
                    "status": acc.status.value,
                    "created": acc.created_at.isoformat() if acc.created_at else None,
                }
                for acc in accounts
            ]
        finally:
            db.close()
    
    def get_star_distribution(self) -> Dict[int, int]:
        """Get distribution of star ratings"""
        db = SessionLocal()
        try:
            distribution = defaultdict(int)
            ratings = db.query(Rating).filter(Rating.stars.isnot(None)).all()
            
            for rating in ratings:
                distribution[rating.stars] += 1
            
            return dict(sorted(distribution.items()))
        finally:
            db.close()
    
    def get_target_stats(self) -> List[Dict]:
        """Get statistics per target"""
        db = SessionLocal()
        try:
            targets = db.query(
                Task.target_profile_url,
                db.query(Task).filter(
                    Task.target_profile_url == Task.target_profile_url
                ).count().label("total_tasks"),
                db.query(Rating).filter(
                    Rating.task_id.in_(
                        db.query(Task.id).filter(
                            Task.target_profile_url == Task.target_profile_url
                        )
                    ),
                    Rating.status == "success"
                ).count().label("successful_ratings"),
            ).group_by(Task.target_profile_url).all()
            
            return [
                {
                    "target": url,
                    "total_tasks": total,
                    "successful_ratings": success,
                }
                for url, total, success in targets
            ]
        except Exception as e:
            logger.error(f"Error getting target stats: {e}")
            return []
        finally:
            db.close()
    
    def get_error_analysis(self, days: int = 7) -> Dict:
        """Analyze errors in the system"""
        db = SessionLocal()
        try:
            start = datetime.now() - timedelta(days=days)
            
            errors = db.query(ActivityLog).filter(
                ActivityLog.created_at >= start,
                ActivityLog.level.in_(["error", "warning"])
            ).all()
            
            error_types = defaultdict(int)
            for error in errors:
                error_types[error.log_type] += 1
            
            return {
                "total_errors": len(errors),
                "by_type": dict(error_types),
                "period_days": days,
            }
        finally:
            db.close()
    
    def get_efficiency_metrics(self) -> Dict:
        """Calculate system efficiency metrics"""
        db = SessionLocal()
        try:
            # Success rates
            total_accounts = db.query(Account).count()
            active_accounts = db.query(Account).filter(
                Account.status.in_([AccountStatus.ACTIVE, AccountStatus.READY])
            ).count()
            
            total_ratings = db.query(Rating).count()
            successful_ratings = db.query(Rating).filter(Rating.status == "success").count()
            
            # Calculate metrics
            account_utilization = (active_accounts / total_accounts * 100) if total_accounts > 0 else 0
            rating_success_rate = (successful_ratings / total_ratings * 100) if total_ratings > 0 else 0
            
            # Overall efficiency score (0-100)
            efficiency = (account_utilization * 0.4 + rating_success_rate * 0.6)
            
            return {
                "account_utilization": round(account_utilization, 2),
                "rating_success_rate": round(rating_success_rate, 2),
                "overall_efficiency": round(efficiency, 2),
                "grade": self._calculate_grade(efficiency),
            }
        finally:
            db.close()
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def get_predictions(self) -> Dict:
        """Simple predictions based on current trends"""
        daily_stats = self.get_daily_stats(days=14)
        
        if len(daily_stats) < 7:
            return {"message": "Not enough data for predictions"}
        
        # Calculate averages
        avg_accounts = sum(d["accounts_created"] for d in daily_stats) / len(daily_stats)
        avg_ratings = sum(d["ratings_submitted"] for d in daily_stats) / len(daily_stats)
        
        # Predict next 7 days
        predicted_accounts = avg_accounts * 7
        predicted_ratings = avg_ratings * 7
        
        return {
            "predicted_accounts_7days": round(predicted_accounts),
            "predicted_ratings_7days": round(predicted_ratings),
            "daily_avg_accounts": round(avg_accounts, 1),
            "daily_avg_ratings": round(avg_ratings, 1),
            "trend": "stable",  # Can be improved with proper trend analysis
        }
