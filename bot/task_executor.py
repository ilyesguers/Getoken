"""
Task Executor - Executes rating tasks
"""
import asyncio
import random
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from bot.config import BotConfig
from bot.facebook_api import FacebookAPI
from bot.utils import Utils
from database import SessionLocal, Account, Task, Rating, ActivityLog
from database.models import AccountStatus, TaskStatus


class TaskExecutor:
    """Executes rating tasks using available accounts"""
    
    def __init__(self):
        self.config = BotConfig
    
    def execute_task(self, task_id: int) -> Dict:
        """Execute a rating task"""
        db = SessionLocal()
        result = {"success": 0, "failed": 0, "total": 0}
        
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.error(f"Task {task_id} not found")
                return result
            
            logger.info(f"Starting task {task_id}: {task.total_ratings_needed} ratings needed")
            
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            db.commit()
            
            # Get available accounts
            accounts = self._get_available_accounts(db, task.total_ratings_needed)
            
            if not accounts:
                logger.warning("No available accounts for task")
                task.status = TaskStatus.FAILED
                task.notes = "No available accounts"
                db.commit()
                return result
            
            # Assign accounts to task
            task.accounts_assigned = [acc.id for acc in accounts]
            db.commit()
            
            # Execute ratings
            for i, account in enumerate(accounts):
                if task.ratings_completed >= task.total_ratings_needed:
                    break
                
                rating_result = self._execute_single_rating(db, account, task)
                
                if rating_result:
                    result["success"] += 1
                else:
                    result["failed"] += 1
                
                result["total"] += 1
                task.ratings_completed += 1
                db.commit()
                
                # Delay between ratings
                if i < len(accounts) - 1:
                    delay_hours = self.config.RATING_INTERVAL_DAYS * 24
                    logger.info(f"Waiting for next rating (simulated {delay_hours}h)")
            
            # Update task status
            if result["success"] >= task.total_ratings_needed:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            db.commit()
            
            # Log activity
            self._log_activity(db, "task_execution", task_id=task_id,
                             message=f"Task completed: {result['success']} success, {result['failed']} failed")
            
            logger.info(f"Task {task_id} completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            self._log_activity(db, "error", task_id=task_id,
                             message=f"Task execution error: {str(e)}", level="error")
            return result
        finally:
            db.close()
    
    def _get_available_accounts(self, db, count: int) -> list:
        """Get accounts ready for tasks"""
        from bot.utils import Utils
        
        accounts = db.query(Account).filter(
            Account.status == AccountStatus.READY
        ).limit(count).all()
        
        # Also check accounts that have matured
        maturing_accounts = db.query(Account).filter(
            Account.status == AccountStatus.MATURING
        ).all()
        
        for acc in maturing_accounts:
            if acc.created_at and Utils.is_account_mature(acc.created_at, self.config.ACCOUNT_MATURITY_DAYS):
                acc.status = AccountStatus.READY
                acc.matured_at = datetime.now()
                db.commit()
                accounts.append(acc)
        
        return accounts[:count]
    
    def _execute_single_rating(self, db, account: Account, task: Task) -> bool:
        """Execute a single rating with an account"""
        try:
            # Determine rating details
            stars = random.randint(self.config.MIN_STARS, self.config.MAX_STARS)
            comment = BotConfig.get_comment_for_stars(stars) if task.rating_type in ["comments", "both"] else None
            
            # Create rating record
            rating = Rating(
                account_id=account.id,
                task_id=task.id,
                stars=stars,
                comment=comment,
                rating_type=task.rating_type,
                target_url=task.target_profile_url,
                status="pending",
            )
            db.add(rating)
            db.commit()
            
            # TODO: Actually execute the rating using browser automation
            # For now, simulate success
            logger.info(f"Rating executed: Account {account.id} -> {stars} stars")
            
            # Update rating status
            rating.status = "success"
            rating.submitted_at = datetime.now()
            
            # Update account stats
            account.total_ratings_given += 1
            account.last_active = datetime.now()
            
            # Check if account has reached max ratings
            if account.total_ratings_given >= self.config.MAX_RATINGS_PER_ACCOUNT:
                account.status = AccountStatus.RETIRED
            
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing rating: {e}")
            
            # Update rating status
            try:
                rating.status = "failed"
                rating.error_message = str(e)
                db.commit()
            except:
                pass
            
            return False
    
    def _log_activity(self, db, log_type: str, account_id=None, task_id=None,
                     message: str = "", level: str = "info"):
        """Log activity"""
        log = ActivityLog(
            log_type=log_type,
            account_id=account_id,
            task_id=task_id,
            message=message,
            level=level,
        )
        db.add(log)
        db.commit()
