from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import os
import logging
from strategies.strategy_manager import StrategyManager
from qbittorrent_client import QBittorrentClient
import threading
import time

# 配置Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mt_auto_freebt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 全局变量
strategy_manager = None
qb_client = None
is_running = False
task_thread = None

# 数据库模型
class TorrentRecord(db.Model):
    """种子记录表"""
    id = db.Column(db.Integer, primary_key=True)
    torrent_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    discount = db.Column(db.String(20))
    discount_end_time = db.Column(db.DateTime)
    seeders = db.Column(db.Integer)
    leechers = db.Column(db.Integer)
    download_decision = db.Column(db.Boolean, nullable=False)
    strategy_used = db.Column(db.String(100))
    priority_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'torrent_id': self.torrent_id,
            'name': self.name,
            'size': self.size,
            'size_human': self.format_size(),
            'discount': self.discount,
            'discount_end_time': self.discount_end_time.isoformat() if self.discount_end_time else None,
            'seeders': self.seeders,
            'leechers': self.leechers,
            'download_decision': self.download_decision,
            'strategy_used': self.strategy_used,
            'priority_score': self.priority_score,
            'created_at': self.created_at.isoformat()
        }
    
    def format_size(self):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.size < 1024.0:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.2f} PB"

class SystemLog(db.Model):
    """系统日志表"""
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }

class StrategyConfig(db.Model):
    """策略配置表"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    config_data = db.Column(db.Text, nullable=False)  # JSON格式
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'config_data': json.loads(self.config_data),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# 初始化函数
def init_app():
    """初始化应用"""
    global strategy_manager, qb_client
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 初始化策略管理器
    config_file = os.environ.get("STRATEGY_CONFIG_FILE", "strategies/config_example.json")
    strategy_manager = StrategyManager(config_file)
    
    # 初始化QBittorrent客户端
    qb_host = os.environ.get("QB_HOST", "http://localhost:8080")
    qb_username = os.environ.get("QB_USERNAME", "admin")
    qb_password = os.environ.get("QB_PASSWORD", "adminadmin")
    
    qb_client = QBittorrentClient(qb_host, qb_username, qb_password)
    
    logging.info("Web应用初始化完成")

# 路由定义
@app.route('/')
def index():
    """主页 - 显示仪表板"""
    return render_template('dashboard.html')

@app.route('/torrents')
def torrents_page():
    """种子列表页面"""
    return render_template('torrents.html')

@app.route('/strategies')
def strategies_page():
    """策略管理页面"""
    return render_template('strategies.html')

@app.route('/logs')
def logs_page():
    """系统日志页面"""
    return render_template('logs.html')

@app.route('/settings')
def settings_page():
    """系统设置页面"""
    return render_template('settings.html')

@app.route('/api/stats')
def get_stats():
    """获取统计数据"""
    try:
        # 基础统计
        total_torrents = TorrentRecord.query.count()
        downloaded_torrents = TorrentRecord.query.filter_by(download_decision=True).count()
        rejected_torrents = TorrentRecord.query.filter_by(download_decision=False).count()
        
        # 今日统计
        today = datetime.utcnow().date()
        today_torrents = TorrentRecord.query.filter(
            db.func.date(TorrentRecord.created_at) == today
        ).count()
        today_downloaded = TorrentRecord.query.filter(
            db.func.date(TorrentRecord.created_at) == today,
            TorrentRecord.download_decision == True
        ).count()
        
        # 策略使用统计
        strategy_stats = db.session.query(
            TorrentRecord.strategy_used,
            db.func.count(TorrentRecord.id).label('count')
        ).group_by(TorrentRecord.strategy_used).all()
        
        # 最近7天的趋势
        trend_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            day_count = TorrentRecord.query.filter(
                db.func.date(TorrentRecord.created_at) == date
            ).count()
            day_downloaded = TorrentRecord.query.filter(
                db.func.date(TorrentRecord.created_at) == date,
                TorrentRecord.download_decision == True
            ).count()
            trend_data.append({
                'date': date.isoformat(),
                'total': day_count,
                'downloaded': day_downloaded
            })
        trend_data.reverse()
        
        return jsonify({
            'total_torrents': total_torrents,
            'downloaded_torrents': downloaded_torrents,
            'rejected_torrents': rejected_torrents,
            'download_rate': (downloaded_torrents / total_torrents * 100) if total_torrents > 0 else 0,
            'today_torrents': today_torrents,
            'today_downloaded': today_downloaded,
            'strategy_stats': [{'strategy': s.strategy_used, 'count': s.count} for s in strategy_stats],
            'trend_data': trend_data,
            'is_running': is_running
        })
    except Exception as e:
        logging.error(f"获取统计数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/torrents')
def get_torrents():
    """获取种子列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        torrents = TorrentRecord.query.order_by(
            TorrentRecord.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'torrents': [t.to_dict() for t in torrents.items],
            'total': torrents.total,
            'pages': torrents.pages,
            'current_page': page
        })
    except Exception as e:
        logging.error(f"获取种子列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies')
def get_strategies():
    """获取策略列表"""
    try:
        if not strategy_manager:
            return jsonify({'error': '策略管理器未初始化'}), 500
        
        strategies = []
        for name in strategy_manager.get_available_strategies():
            strategy = strategy_manager.get_strategy(name)
            info = strategy_manager.get_strategy_info(name)
            strategies.append({
                'name': name,
                'info': info,
                'is_current': strategy == strategy_manager.get_current_strategy()
            })
        
        return jsonify({'strategies': strategies})
    except Exception as e:
        logging.error(f"获取策略列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/<strategy_name>', methods=['PUT'])
def update_strategy(strategy_name):
    """更新策略配置"""
    try:
        if not strategy_manager:
            return jsonify({'error': '策略管理器未初始化'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 这里可以添加策略配置更新的逻辑
        # 暂时只是设置当前策略
        success = strategy_manager.set_current_strategy(strategy_name)
        
        if success:
            return jsonify({'message': f'策略 {strategy_name} 设置成功'})
        else:
            return jsonify({'error': f'策略 {strategy_name} 设置失败'}), 400
            
    except Exception as e:
        logging.error(f"更新策略失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/start', methods=['POST'])
def start_system():
    """启动系统"""
    global is_running, task_thread
    
    try:
        if is_running:
            return jsonify({'error': '系统已在运行中'}), 400
        
        is_running = True
        task_thread = threading.Thread(target=run_task_loop, daemon=True)
        task_thread.start()
        
        return jsonify({'message': '系统启动成功'})
    except Exception as e:
        logging.error(f"启动系统失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """停止系统"""
    global is_running
    
    try:
        is_running = False
        return jsonify({'message': '系统停止成功'})
    except Exception as e:
        logging.error(f"停止系统失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """获取系统日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level')
        
        query = SystemLog.query
        if level:
            query = query.filter_by(level=level)
        
        logs = query.order_by(
            SystemLog.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
    except Exception as e:
        logging.error(f"获取日志失败: {e}")
        return jsonify({'error': str(e)}), 500

def run_task_loop():
    """运行任务循环"""
    global is_running
    
    while is_running:
        try:
            # 这里调用原有的flood_task逻辑
            # 暂时只是记录日志
            log_message = f"任务循环执行 - {datetime.utcnow()}"
            with app.app_context():
                log = SystemLog(level='INFO', message=log_message)
                db.session.add(log)
                db.session.commit()
            
            time.sleep(60)  # 每分钟执行一次
        except Exception as e:
            logging.error(f"任务循环执行失败: {e}")
            with app.app_context():
                log = SystemLog(level='ERROR', message=f"任务循环执行失败: {e}")
                db.session.add(log)
                db.session.commit()
            time.sleep(60)

if __name__ == '__main__':
    init_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 