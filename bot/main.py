"""
Main Bot Module v2.0 - Enhanced with analytics and backup
"""
import asyncio
import time
import signal
import sys
from datetime import datetime, timedelta
from loguru import logger

from bot.config import BotConfig
from bot.account_generator import AccountGenerator
from bot.facebook_api import FacebookAPI
from bot.task_executor import TaskExecutor
from bot.proxy_manager import ProxyManager
from bot.anti_detection import AntiDetectionV2
from bot.notifications import NotificationManager
from bot.backup_manager import BackupManager
from bot.analytics import DataAnalyzer
from bot.utils import Utils
from database import SessionLocal, init_db, Account, Task, ActivityLog
from database.models import AccountStatus, TaskStatus


# Configure loguru
logger.add(
    "logs/bot_{time}.log",
    rotation="1 day",
    retention="7 days",
    compression="gz",
    level="INFO"
)


class Bot:
    """Enhanced main bot class"""
    
    def __init__(self):
        self.config = BotConfig
        self.account_generator = AccountGenerator()
        self.task_executor = TaskExecutor()
        self.proxy_manager = ProxyManager()
        self.notification_manager = NotificationManager()
        self.backup_manager = BackupManager()
        self.data_analyzer = DataAnalyzer()
        self.is_running = False
        self.last_account_creation = None
        self.daily_report_sent = False
        self.start_time = None
    
    def start(self):
        """Start the bot"""
        logger.info("=" * 60)
        logger.info("🤖 Getoken Bot v2.0 Starting...")
        logger.info("=" * 60)
        logger.info(f"Mode: {self.config.BOT_MODE}")
        logger.info(f"Country: {self.config.DEFAULT_COUNTRY}")
        logger.info(f"Anti-Detection: {'Enabled' if self.config.ENABLE_FINGERPRINTING else 'Disabled'}")
        logger.info("=" * 60)
        
        self.start_time = datetime.now()
        
        # Initialize database
        init_db()
        logger.info("✅ Database initialized")
        
        # Initial backup check
        self.backup_manager.auto_backup_if_needed()
        
        # Set running flag
        self.is_running = True
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        
        # Main loop
        self._main_loop()
    
    def _main_loop(self):
        """Main bot loop with enhanced features"""
        while self.is_running:
            try:
                # 1. Check for daily report
                self._check_daily_report()
                
                # 2. Check if it's time to create a new account
                if self._should_create_account():
                    self._create_new_account()
                
                # 3. Check for maturing accounts
                self._check_maturing_accounts()
                
                # 4. Check for pending tasks
                self._execute_pending_tasks()
                
                # 5. Clean up banned accounts
                self._cleanup_banned_accounts()
                
                # 6. Auto backup
                self._check_backup()
                
                # 7. Check system health
                self._check_system_health()
                
                # 8. Log status
                self._log_status()
                
                # Sleep before next iteration
                sleep_hours = self.config.BOT_INTERVAL_HOURS
                logger.info(f"💤 Sleeping for {sleep_hours} hours...")
                
                for _ in range(sleep_hours * 60):
                    if not self.is_running:
                        break
                    time.sleep(60)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                self._log_activity("system_error", message=f"Main loop error: {str(e)}", level="error")
                time.sleep(60)
        
        logger.info("🛑 Bot stopped")
    
    def _check_daily_report(self):
        """Send daily report if needed"""
        now = datetime.now()
        today = now.date()
        
        # Send report at midnight
        if now.hour == 0 and not self.daily_report_sent:
            stats = self.data_analyzer.get_dashboard_stats()
            self.notification_manager.notify_daily_report({
                "active_accounts": stats["accounts"]["active"],
                "ready_accounts": stats["accounts"]["ready"],
                "ratings_today": stats["ratings"]["successful"],
                "success_rate": stats["ratings"]["success_rate"],
                "completed_tasks": stats["tasks"]["completed"],
            })
            self.daily_report_sent = True
        
        # Reset flag for next day
        if now.hour == 1:
            self.daily_report_sent = False
    
    def _should_create_account(self) -> bool:
        """Check if it's time to create a new account"""
        today = datetime.now().date()
        db = SessionLocal()
        try:
            accounts_today = db.query(Account).filter(
                Account.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            safety_config = self.config.get_safety_config()
            
            if accounts_today >= safety_config["max_daily_accounts"]:
                logger.debug(f"Daily account limit reached ({accounts_today})")
                return False
            
            if self.last_account_creation:
                elapsed = datetime.now() - self.last_account_creation
                if elapsed < timedelta(hours=self.config.BOT_INTERVAL_HOURS):
                    return False
            
            return True
        finally:
            db.close()
    
    def _create_new_account(self):
        """Create a new Facebook account with enhanced anti-detection"""
        logger.info("🔄 Creating new account...")
        
        try:
            # Generate account data
            account_data = self.account_generator.generate_account()
            
            # Get proxy
            proxy = self.proxy_manager.get_next_proxy()
            
            # Create account using browser automation
            api = FacebookAPI(proxy=proxy)
            
            # Run async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                success = loop.run_until_complete(self._async_create_account(api, account_data))
            finally:
                loop.close()
            
            if success:
                # Save to database
                self._save_account_to_db(account_data)
                self.last_account_creation = datetime.now()
                
                # Send notification
                self.notification_manager.notify_account_created(
                    account_data['display_name'],
                    account_data['email']
                )
                
                logger.info(f"✅ Account created: {account_data['display_name']}")
            else:
                logger.warning("⚠️ Account creation failed")
            
        except Exception as e:
            logger.error(f"❌ Error creating account: {e}")
            self.notification_manager.notify_system_error(str(e), "Account Creation")
    
    async def _async_create_account(self, api: FacebookAPI, account_data: dict) -> bool:
        """Async account creation"""
        try:
            await api.initialize_browser()
            success = await api.create_account(account_data)
            await api.close_browser()
            return success
        except Exception as e:
            logger.error(f"❌ Async account creation error: {e}")
            await api.close_browser()
            return False
    
    def _save_account_to_db(self, account_data: dict):
        """Save account to database"""
        db = SessionLocal()
        try:
            account = Account(
                fb_email=account_data['email'],
                fb_password=account_data['password'],
                first_name=account_data['first_name'],
                last_name=account_data['last_name'],
                display_name=account_data['display_name'],
                gender=account_data['gender'],
                birth_date=account_data['birth_date'],
                city=account_data['city'],
                bio=account_data.get('bio', ''),
                status=AccountStatus.MATURING,
                user_agent=account_data.get('user_agent', ''),
                fingerprint_hash=account_data.get('fingerprint_hash', ''),
            )
            db.add(account)
            db.commit()
            
            self._log_activity("account_creation", account_id=account.id,
                             message=f"Account created: {account.display_name}")
            
        except Exception as e:
            logger.error(f"❌ Error saving account: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _check_maturing_accounts(self):
        """Check and update maturing accounts"""
        db = SessionLocal()
        try:
            maturing_accounts = db.query(Account).filter(
                Account.status == AccountStatus.MATURING
            ).all()
            
            for account in maturing_accounts:
                if account.created_at and Utils.is_account_mature(
                    account.created_at, self.config.ACCOUNT_MATURITY_DAYS
                ):
                    account.status = AccountStatus.READY
                    account.matured_at = datetime.now()
                    logger.info(f"✅ Account matured: {account.display_name}")
            
            db.commit()
        except Exception as e:
            logger.error(f"❌ Error checking maturing accounts: {e}")
        finally:
            db.close()
    
    def _execute_pending_tasks(self):
        """Execute pending tasks"""
        db = SessionLocal()
        try:
            pending_tasks = db.query(Task).filter(
                Task.status == TaskStatus.PENDING
            ).all()
            
            for task in pending_tasks:
                logger.info(f"📋 Executing task {task.id}...")
                result = self.task_executor.execute_task(task.id)
                
                # Send notification
                if result["success"] > 0:
                    self.notification_manager.notify_task_completed(
                        task.id, result["success"], result["total"]
                    )
                else:
                    self.notification_manager.notify_task_failed(
                        task.id, "No successful ratings"
                    )
            
        except Exception as e:
            logger.error(f"❌ Error executing tasks: {e}")
        finally:
            db.close()
    
    def _cleanup_banned_accounts(self):
        """Clean up banned accounts"""
        db = SessionLocal()
        try:
            banned = db.query(Account).filter(
                Account.status == AccountStatus.BANNED
            ).all()
            
            for account in banned:
                logger.info(f"🚫 Banned account detected: {account.display_name}")
                self.notification_manager.notify_account_banned(
                    account.display_name, "Detected by system"
                )
            
            db.commit()
        except Exception as e:
            logger.error(f"❌ Error cleaning up banned accounts: {e}")
        finally:
            db.close()
    
    def _check_backup(self):
        """Check if backup is needed"""
        if self.config.AUTO_BACKUP_ENABLED:
            self.backup_manager.auto_backup_if_needed()
    
    def _check_system_health(self):
        """Check system health and alert if needed"""
        try:
            efficiency = self.data_analyzer.get_efficiency_metrics()
            
            if efficiency["overall_efficiency"] < 50:
                logger.warning(f"⚠️ Low system efficiency: {efficiency['overall_efficiency']}%")
                self._log_activity("health_check", 
                                 message=f"Low efficiency detected: {efficiency['overall_efficiency']}%",
                                 level="warning")
            
            # Check error rate
            errors = self.data_analyzer.get_error_analysis(days=1)
            if errors["total_errors"] > 10:
                logger.warning(f"⚠️ High error rate: {errors['total_errors']} errors in 24h")
                self.notification_manager.notify_system_error(
                    f"High error rate: {errors['total_errors']} errors in 24h",
                    "Health Check"
                )
                
        except Exception as e:
            logger.error(f"❌ Error checking health: {e}")
    
    def _log_activity(self, log_type: str, account_id=None, task_id=None,
                     message: str = "", level: str = "info"):
        """Log activity to database"""
        db = SessionLocal()
        try:
            log = ActivityLog(
                log_type=log_type,
                account_id=account_id,
                task_id=task_id,
                message=message,
                level=level,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"❌ Error logging activity: {e}")
        finally:
            db.close()
    
    def _log_status(self):
        """Log comprehensive status"""
        try:
            stats = self.data_analyzer.get_dashboard_stats()
            
            uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
            uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h"
            
            logger.info("=" * 60)
            logger.info("📊 BOT STATUS:")
            logger.info(f"  Uptime: {uptime_str}")
            logger.info(f"  Accounts: {stats['accounts']['total']} total, "
                       f"{stats['accounts']['active']} active, "
                       f"{stats['accounts']['ready']} ready, "
                       f"{stats['accounts']['banned']} banned")
            logger.info(f"  Tasks: {stats['tasks']['total']} total, "
                       f"{stats['tasks']['pending']} pending, "
                       f"{stats['tasks']['completed']} completed")
            logger.info(f"  Ratings: {stats['ratings']['total']} total, "
                       f"{stats['ratings']['successful']} successful "
                       f"({stats['ratings']['success_rate']}%)")
            logger.info(f"  Ban Rate: {stats['accounts']['ban_rate']}%")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error logging status: {e}")
    
    def _shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info("🛑 Shutdown signal received...")
        
        # Create final backup
        try:
            logger.info("Creating final backup...")
            self.backup_manager.create_backup()
        except Exception as e:
            logger.error(f"Backup failed: {e}")
        
        self.is_running = False


def main():
    """Entry point for the bot"""
    bot = Bot()
    bot.start()


if __name__ == "__main__":
    main()
