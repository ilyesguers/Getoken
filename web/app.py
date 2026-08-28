"""
Web Application - Dashboard v2.0
Enhanced dashboard with analytics and management
"""
import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

from database import init_db, SessionLocal, Account, Task, Rating, ActivityLog, Proxy
from database.models import AccountStatus, TaskStatus
from bot.analytics import DataAnalyzer
from bot.backup_manager import BackupManager

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

# Initialize managers
analyzer = DataAnalyzer()
backup_manager = BackupManager()


# ============ Dashboard Routes ============

@app.route('/')
def index():
    """Main dashboard page"""
    db = SessionLocal()
    try:
        stats = analyzer.get_dashboard_stats()
        recent_logs = db.query(ActivityLog).order_by(
            ActivityLog.created_at.desc()
        ).limit(20).all()
        
        return render_template('dashboard.html', stats=stats, recent_logs=recent_logs)
    finally:
        db.close()


# ============ Analytics Routes ============

@app.route('/analytics')
def analytics():
    """Analytics page with advanced statistics"""
    daily_stats = analyzer.get_daily_stats(days=14)
    efficiency = analyzer.get_efficiency_metrics()
    star_distribution = analyzer.get_star_distribution()
    predictions = analyzer.get_predictions()
    error_analysis = analyzer.get_error_analysis(days=7)
    top_accounts = analyzer.get_account_performance(limit=10)
    
    return render_template(
        'analytics.html',
        daily_stats=daily_stats,
        efficiency=efficiency,
        star_distribution=star_distribution,
        predictions=predictions,
        error_analysis=error_analysis,
        top_accounts=top_accounts,
    )


# ============ Account Routes ============

@app.route('/accounts')
def accounts():
    """Accounts management page"""
    db = SessionLocal()
    try:
        status = request.args.get('status', 'all')
        query = db.query(Account)
        
        if status != 'all':
            query = query.filter(Account.status == status)
        
        accounts = query.order_by(Account.created_at.desc()).limit(100).all()
        
        return render_template('accounts.html', accounts=accounts, current_status=status)
    finally:
        db.close()


@app.route('/api/accounts', methods=['GET'])
def api_get_accounts():
    """API: Get accounts"""
    db = SessionLocal()
    try:
        status = request.args.get('status')
        query = db.query(Account)
        if status and status != 'all':
            query = query.filter(Account.status == status)
        accounts = query.order_by(Account.created_at.desc()).limit(100).all()
        return jsonify([acc.to_dict() for acc in accounts])
    finally:
        db.close()


@app.route('/api/accounts/create', methods=['POST'])
def api_create_account():
    """API: Trigger account creation"""
    try:
        return jsonify({"success": True, "message": "Account creation triggered"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
def api_delete_account(account_id):
    """API: Delete account"""
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            db.delete(account)
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Account not found"}), 404
    finally:
        db.close()


@app.route('/api/accounts/<int:account_id>/ban', methods=['POST'])
def api_ban_account(account_id):
    """API: Mark account as banned"""
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            account.status = AccountStatus.BANNED
            account.banned_at = datetime.now()
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Account not found"}), 404
    finally:
        db.close()


# ============ Task Routes ============

@app.route('/tasks')
def tasks():
    """Tasks management page"""
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.created_at.desc()).all()
        return render_template('tasks.html', tasks=tasks)
    finally:
        db.close()


@app.route('/tasks/new', methods=['GET', 'POST'])
def new_task():
    """Create new task"""
    if request.method == 'POST':
        db = SessionLocal()
        try:
            task = Task(
                target_profile_url=request.form['target_url'],
                target_type=request.form['target_type'],
                total_ratings_needed=int(request.form['total_ratings']),
                rating_type=request.form['rating_type'],
                status=TaskStatus.PENDING,
                config={
                    "min_stars": int(request.form.get('min_stars', 3)),
                    "max_stars": int(request.form.get('max_stars', 5)),
                    "comments_enabled": request.form.get('comments_enabled') == 'on',
                    "auto_approve": request.form.get('auto_approve') == 'on',
                    "priority": request.form.get('priority', 'normal'),
                    "schedule_type": request.form.get('schedule_type', 'immediate'),
                }
            )
            db.add(task)
            db.commit()
            
            return redirect(url_for('tasks'))
        finally:
            db.close()
    
    return render_template('new_task.html')


@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """API: Get tasks"""
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    finally:
        db.close()


@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """API: Create task"""
    db = SessionLocal()
    try:
        data = request.json
        task = Task(
            target_profile_url=data['target_url'],
            target_type=data.get('target_type', 'profile'),
            total_ratings_needed=data.get('total_ratings', 1),
            rating_type=data.get('rating_type', 'stars'),
            status=TaskStatus.PENDING,
            config=data.get('config', {}),
        )
        db.add(task)
        db.commit()
        return jsonify({"success": True, "task": task.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>/start', methods=['POST'])
def api_start_task(task_id):
    """API: Start task"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.PENDING
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Task not found"}), 404
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>/pause', methods=['POST'])
def api_pause_task(task_id):
    """API: Pause task"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.PAUSED
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Task not found"}), 404
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>/cancel', methods=['POST'])
def api_cancel_task(task_id):
    """API: Cancel task"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.CANCELLED
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Task not found"}), 404
    finally:
        db.close()


# ============ API: Analytics ============

@app.route('/api/analytics/dashboard', methods=['GET'])
def api_analytics_dashboard():
    """API: Dashboard statistics"""
    return jsonify(analyzer.get_dashboard_stats())


@app.route('/api/analytics/daily', methods=['GET'])
def api_analytics_daily():
    """API: Daily statistics"""
    days = request.args.get('days', 7, type=int)
    return jsonify(analyzer.get_daily_stats(days=days))


@app.route('/api/analytics/efficiency', methods=['GET'])
def api_analytics_efficiency():
    """API: Efficiency metrics"""
    return jsonify(analyzer.get_efficiency_metrics())


@app.route('/api/analytics/predictions', methods=['GET'])
def api_analytics_predictions():
    """API: Predictions"""
    return jsonify(analyzer.get_predictions())


@app.route('/api/analytics/stars', methods=['GET'])
def api_analytics_stars():
    """API: Star distribution"""
    return jsonify(analyzer.get_star_distribution())


# ============ Backup Routes ============

@app.route('/api/backup/create', methods=['POST'])
def api_create_backup():
    """API: Create backup"""
    try:
        path = backup_manager.create_backup()
        if path:
            return jsonify({"success": True, "path": path})
        return jsonify({"success": False, "message": "Backup failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/backup/list', methods=['GET'])
def api_list_backups():
    """API: List backups"""
    return jsonify(backup_manager.list_backups())


@app.route('/api/backup/restore', methods=['POST'])
def api_restore_backup():
    """API: Restore from backup"""
    data = request.json
    backup_name = data.get('backup_name')
    if not backup_name:
        return jsonify({"success": False, "message": "No backup specified"}), 400
    
    success = backup_manager.restore_backup(backup_name)
    return jsonify({"success": success})


# ============ Ratings & Activity ============

@app.route('/api/ratings', methods=['GET'])
def api_get_ratings():
    """API: Get ratings"""
    db = SessionLocal()
    try:
        task_id = request.args.get('task_id')
        query = db.query(Rating)
        if task_id:
            query = query.filter(Rating.task_id == task_id)
        ratings = query.order_by(Rating.created_at.desc()).limit(100).all()
        return jsonify([r.to_dict() for r in ratings])
    finally:
        db.close()


@app.route('/api/activity', methods=['GET'])
def api_get_activity():
    """API: Get activity logs"""
    db = SessionLocal()
    try:
        level = request.args.get('level')
        query = db.query(ActivityLog)
        if level:
            query = query.filter(ActivityLog.level == level)
        logs = query.order_by(ActivityLog.created_at.desc()).limit(50).all()
        return jsonify([log.to_dict() for log in logs])
    finally:
        db.close()


# ============ Settings Routes ============

@app.route('/settings')
def settings():
    """Settings page"""
    from bot.config import BotConfig
    return render_template('settings.html', config=BotConfig)


# ============ System Status ============

@app.route('/api/status')
def api_status():
    """API: Bot status"""
    db = SessionLocal()
    try:
        total_accounts = db.query(Account).count()
        active_accounts = db.query(Account).filter(Account.status == AccountStatus.ACTIVE).count()
        ready_accounts = db.query(Account).filter(Account.status == AccountStatus.READY).count()
        total_tasks = db.query(Task).count()
        pending_tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).count()
        
        return jsonify({
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "accounts": {
                "total": total_accounts,
                "active": active_accounts,
                "ready": ready_accounts,
            },
            "tasks": {
                "total": total_tasks,
                "pending": pending_tasks,
            },
        })
    finally:
        db.close()


@app.route('/api/health')
def api_health():
    """API: Health check"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


# ============ Error Handlers ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ============ Initialize ============

@app.before_first_request
def before_first_request():
    """Initialize database before first request"""
    init_db()
    # Auto backup check
    backup_manager.auto_backup_if_needed()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
