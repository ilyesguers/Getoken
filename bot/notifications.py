"""
Notification System
Send alerts and notifications about bot activities
"""
import requests
import json
from typing import Optional, Dict
from datetime import datetime
from loguru import logger
from bot.config import BotConfig


class NotificationManager:
    """
    Manages notifications for various events
    Supports multiple channels (future expansion)
    """
    
    def __init__(self):
        self.config = BotConfig
    
    def notify_account_created(self, account_name: str, account_email: str):
        """Notify when new account is created"""
        message = f"✅ تم إنشاء حساب جديد: {account_name}\nالبريد: {account_email}"
        self._send_notification("account_created", message, level="info")
    
    def notify_account_banned(self, account_name: str, reason: str = ""):
        """Notify when account is banned"""
        message = f"🚫 تم حظر حساب: {account_name}\nالسبب: {reason or 'غير معروف'}"
        self._send_notification("account_banned", message, level="warning")
    
    def notify_task_completed(self, task_id: int, success_count: int, total: int):
        """Notify when task is completed"""
        rate = (success_count / total * 100) if total > 0 else 0
        message = f"📋 اكتملت المهمة #{task_id}\nالنجاح: {success_count}/{total} ({rate:.1f}%)"
        self._send_notification("task_completed", message, level="info")
    
    def notify_task_failed(self, task_id: int, error: str):
        """Notify when task fails"""
        message = f"❌ فشلت المهمة #{task_id}\nالخطأ: {error}"
        self._send_notification("task_failed", message, level="error")
    
    def notify_system_error(self, error: str, context: str = ""):
        """Notify about system errors"""
        message = f"⚠️ خطأ في النظام\n{error}"
        if context:
            message += f"\nالسياق: {context}"
        self._send_notification("system_error", message, level="error")
    
    def notify_daily_report(self, stats: Dict):
        """Send daily summary report"""
        message = (
            f"📊 التقرير اليومي\n"
            f"━━━━━━━━━━━━━━━\n"
            f"الحسابات النشطة: {stats.get('active_accounts', 0)}\n"
            f"الحسابات الجاهزة: {stats.get('ready_accounts', 0)}\n"
            f"التقييمات اليوم: {stats.get('ratings_today', 0)}\n"
            f"نسبة النجاح: {stats.get('success_rate', 0):.1f}%\n"
            f"المهام المكتملة: {stats.get('completed_tasks', 0)}"
        )
        self._send_notification("daily_report", message, level="info")
    
    def _send_notification(self, event_type: str, message: str, level: str = "info"):
        """
        Send notification through configured channels
        Currently logs only - can be extended to Telegram, Discord, Email, etc.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_func = {
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
        }.get(level, logger.info)
        
        log_func(f"[NOTIFICATION] [{event_type}] {message}")
        
        # Future: Add Telegram, Discord, Email notifications
        # self._send_telegram(message)
        # self._send_discord(message)
        # self._send_email(message)
    
    def _send_telegram(self, message: str):
        """Send notification via Telegram Bot (future)"""
        # TODO: Implement Telegram notifications
        pass
    
    def _send_discord(self, message: str):
        """Send notification via Discord Webhook (future)"""
        # TODO: Implement Discord notifications
        pass
    
    def _send_email(self, message: str):
        """Send notification via Email (future)"""
        # TODO: Implement Email notifications
        pass
