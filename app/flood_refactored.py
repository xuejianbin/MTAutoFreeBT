import time
import xml.etree.ElementTree as ET
from dateutil import parser
import os
import re
import random
import logging
from datetime import datetime, timedelta
import json
import pytz
import requests
from qbittorrent_client import QBittorrentClient
from strategies.strategy_manager import StrategyManager

# 时区映射信息
tzinfos = {"CST": pytz.timezone("Asia/Shanghai")}
# 配置日志记录器
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 环境变量配置
APIKEY = os.environ.get("APIKEY", "70390435-35fb-44e8-a207-fcd6be7099ef")
DOWNLOADPATH = os.environ.get("DOWNLOADPATH", "/download/PT刷流")

SEND_URL = os.environ.get("SEND_URL", None)
RSS = os.environ.get("RSS", "url")
SPACE = int(float(os.environ.get("SPACE", 80)) * 1024 * 1024 * 1024)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
CHAT_ID = int(os.environ.get("CHAT_ID", "646111111"))
GET_METHOD = os.environ.get("GET_METHOD", False)
MAX_SIZE = int(float(os.environ.get("MAX_SIZE", 30)) * 1024 * 1024 * 1024)
MIN_SIZE = int(float(os.environ.get("MIN_SIZE", 1)) * 1024 * 1024 * 1024)
FREE_TIME = int(float(os.environ.get("FREE_TIME", 10)) * 60 * 60)
PUBLISH_BEFORE = int(float(os.environ.get("PUBLISH_BEFORE", 24)) * 60 * 60)
PROXY = os.environ.get("PROXY", None)
TAGS = os.environ.get("TAGS", "MT刷流")
LS_RATIO = float(os.environ.get("LS_RATIO", 1))
IPV6 = os.environ.get("IPV6", False)
DATA_FILE = "flood_data.json"

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", None)
WEBHOOK_KEY = os.environ.get("WEBHOOK_KEY", None)

# 策略配置
STRATEGY_CONFIG_FILE = os.environ.get("STRATEGY_CONFIG_FILE", "strategies/config_example.json")

mt_session = requests.Session()
flood_torrents = []

# 全局策略管理器
strategy_manager = None


# 添加Telegram通知
def send_telegram_message(message):
    if BOT_TOKEN is None:
        return
    logging.info(f"发送消息通知到TG{message}")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        logging.error(f"发送TG通知失败，请求异常：{e}")
        return
    if response.status_code == 200:
        logging.info("消息发送成功！")
    else:
        logging.info("消息发送失败！")


# 添加Server酱3消息推送
def send_server3_message(message):
    if SEND_URL is None:
        return
    logging.info(f"发送消息通知到Server3{message}")
    url = f"{SEND_URL}"
    data = {"title": "M-Team 刷流", "desp": message}
    try:
        response = requests.post(url, json=data)
    except requests.exceptions.RequestException as e:
        logging.error(f"发送Server3通知失败，请求异常：{e}")
        return
    if response.status_code == 200:
        logging.info("消息发送成功！")
    else:
        logging.info("消息发送失败！")


# 新增Webhook消息推送
def send_webhook_message(message):
    if WEBHOOK_URL is None:
        return
    logging.info(f"发送消息通知到Webhook: {message}")
    data = {"message": message}
    if WEBHOOK_KEY:
        data["key"] = WEBHOOK_KEY
    try:
        response = requests.post(WEBHOOK_URL, json=data)
    except requests.exceptions.RequestException as e:
        logging.error(f"发送Webhook通知失败，请求异常：{e}")
        return
    if response.status_code == 200:
        logging.info("Webhook消息发送成功！")
    else:
        logging.info(f"Webhook消息发送失败！HTTP状态码: {response.status_code}")


# 从MT获取种子信息
def get_torrent_detail(torrent_id):
    url = "https://api.m-team.cc/api/torrent/detail"
    try:
        response = mt_session.post(url, data={"id": torrent_id})
    except requests.exceptions.RequestException as e:
        logging.error(f"种子信息获取失败，请求异常：{e}")
        return None
    try:
        data = response.json()["data"]
        name = data["name"]
        size = int(data["size"])
        discount = data["status"].get("discount", None)
        discount_end_time = data["status"].get("discountEndTime", None)
        seeders = int(data["status"]["seeders"])
        leechers = int(data["status"]["leechers"])
        if discount_end_time is not None:
            discount_end_time = datetime.strptime(
                discount_end_time, "%Y-%m-%d %H:%M:%S"
            )
    except (ValueError, KeyError) as e:
        logging.warning(f"response信息为{response.text}")
        logging.error(f"种子信息解析失败：{e}")
        return None
    return {
        "name": name,
        "size": size,
        "discount": discount,
        "discount_end_time": discount_end_time,
        "seeders": seeders,
        "leechers": leechers,
    }


# 添加种子下载地址到QBittorrent（重构版本）
def add_torrent(qb_client, url, name):
    global flood_torrents
    
    if GET_METHOD == "True":
        logging.info(f"使用保存种子方式给QB服务器添加种子")
        try:
            response = mt_session.get(url)
        except requests.exceptions.RequestException as e:
            logging.error(f"种子下载异常：{e}")
            return False
        if response.status_code != 200:
            logging.error(f"种子文件下载失败，HTTP状态码: {response.status_code}")
            return False
        
        # 使用新的客户端方法
        success = qb_client.add_torrent_by_file(
            torrent_content=response.content,
            filename=name,
            save_path=DOWNLOADPATH,
            tags=TAGS
        )
    else:
        logging.info(f"使用推送URL给QB服务器方式添加种子")
        # 使用新的客户端方法
        success = qb_client.add_torrent_by_url(
            url=url,
            save_path=DOWNLOADPATH,
            tags=TAGS
        )

    if success:
        logging.info(f"种子{name}添加成功！")
        send_telegram_message(f"种子{name}添加成功！")
        send_server3_message(f"种子{name}添加成功！")
        send_webhook_message(f"种子{name}添加成功！")
        return True
    else:
        logging.error(f"种子{name}添加失败！")
        return False


# 从MT获取种子下载地址
def get_torrent_url(torrent_id):
    url = "https://api.m-team.cc/api/torrent/genDlToken"
    try:
        response = mt_session.post(url, data={"id": torrent_id})
    except requests.exceptions.RequestException as e:
        logging.error(f"获取种子地址失败，请求异常：{e}")
        return None
    if response.status_code != 200:
        logging.error(f"获取种子地址失败，HTTP状态码: {response.status_code}")
        return None
    try:
        data = response.json()["data"]
        print(IPV6)
        if IPV6 == "True":
            download_url = (
                f'{data.split("?")[0]}?useHttps=true&type=ipv6&{data.split("?")[1]}'
            )
        else:
            download_url = (
                f'{data.split("?")[0]}?useHttps=true&type=ipv4&{data.split("?")[1]}'
            )
    except (KeyError, ValueError) as e:
        logging.warning(f"response信息为{response.text}")
        logging.error(f"种子地址解析失败：{e}")
        return None
    return download_url


# 每隔一段时间访问MT获取RSS并添加种子到QBittorrent（重构版本）
def flood_task():
    global flood_torrents, strategy_manager
    
    # 初始化策略管理器
    if strategy_manager is None:
        try:
            strategy_manager = StrategyManager(STRATEGY_CONFIG_FILE)
            logging.info(f"策略管理器初始化成功，使用配置文件: {STRATEGY_CONFIG_FILE}")
            logging.info(f"当前策略: {strategy_manager.get_current_strategy().get_strategy_name() if strategy_manager.get_current_strategy() else 'None'}")
        except Exception as e:
            logging.error(f"策略管理器初始化失败: {e}")
            logging.info("使用默认策略")
            strategy_manager = StrategyManager()
    
    # 使用新的 qBittorrent 客户端
    with QBittorrentClient() as qb_client:
        if not qb_client.login():
            logging.error("qBittorrent 登录失败")
            return
        
        logging.info("开始刷流")
        
        # 获取磁盘空间
        disk_space = qb_client.get_disk_space()
        if disk_space is None:
            return
        elif disk_space <= SPACE:
            logging.info("磁盘空间不足，停止刷流")
            send_telegram_message(
                f"磁盘空间不足，停止刷流，当前剩余空间为{disk_space / 1024 / 1024 / 1024:.2f}G"
            )
            send_server3_message(
                f"磁盘空间不足，停止刷流，当前剩余空间为{disk_space / 1024 / 1024 / 1024:.2f}G"
            )
            send_webhook_message(
                f"磁盘空间不足，停止刷流，当前剩余空间为{disk_space / 1024 / 1024 / 1024:.2f}G"
            )
            return
        
        # 获取RSS数据
        try:
            response = mt_session.get(RSS)
        except requests.exceptions.RequestException as e:
            logging.error(f"RSS请求失败：{e}")
            return
        if response.status_code != 200:
            logging.error(f"获取RSS失败，HTTP状态码: {response.status_code}")
            return
        logging.info("RSS数据获取成功")
        
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logging.error(f"XML解析失败：{e}")
            return

        NAMESPACE = {"dc": "http://purl.org/dc/elements/1.1/"}
        for item in root.findall("channel/item", NAMESPACE):
            link = item.find("link").text
            torrent_id = re.search(r"\d+$", link).group()
            publish_time = item.find("pubDate").text
            publish_time = parser.parse(publish_time, tzinfos=tzinfos)
            title = item.find("title").text
            matches = re.findall(
                r"\[(\d+(\.\d+)?)\s(B|KB|MB|GB|TB|PB)\]", title.replace(",", "")
            )
            if not matches:
                logging.info(
                    f"种子{torrent_id}大小解析失败，可能是生成的RSS链接未勾选[大小]，标题为：{title}"
                )
                continue
            # 取最后一个匹配的组
            size, unit = matches[-1][0], matches[-1][2]
            UNIT_LIST = ["B", "KB", "MB", "GB", "TB", "PB"]
            size = int(float(size) * 1024 ** UNIT_LIST.index(unit))

            # 如果已经添加过该种子则跳过
            if any(torrent_id == torrent["id"] for torrent in flood_torrents):
                logging.info(f"种子{torrent_id}已经添加过，跳过")
                continue
            
            # 获取种子详细信息
            logging.info(f"开始获取种子{torrent_id}信息")
            time.sleep(random.randint(5, 10))
            detail = get_torrent_detail(torrent_id)
            if detail is None:
                continue

            name = detail["name"]
            discount = detail["discount"]
            discount_end_time = detail["discount_end_time"]
            seeders = detail["seeders"]
            leechers = detail["leechers"]

            # 基本免费检查（保留原有逻辑作为兜底）
            if discount is None:
                logging.info(
                    f"种子{torrent_id}非免费或请求异常，忽略种子, 信息为：{detail}"
                )
                continue
            if discount not in ["FREE", "_2X_FREE"]:
                logging.info(f"种子{torrent_id}非免费资源，忽略种子，状态为：{discount}")
                continue

            # 构建种子信息字典供策略使用
            torrent_info = {
                "id": torrent_id,
                "name": name,
                "size": size,
                "discount": discount,
                "discount_end_time": discount_end_time,
                "seeders": seeders,
                "leechers": leechers,
                "publish_time": publish_time,
                "disk_space": disk_space
            }

            # 使用策略系统判断是否下载
            try:
                should_download = strategy_manager.should_download(torrent_info)
                if not should_download:
                    logging.info(f"策略系统拒绝下载种子 {torrent_id}: {name}")
                    continue
                
                # 获取优先级（可选，用于日志记录）
                priority = strategy_manager.get_priority(torrent_info)
                logging.info(f"种子 {torrent_id} 通过策略检查，优先级: {priority:.2f}")
                
            except Exception as e:
                logging.error(f"策略系统执行失败: {e}")
                # 策略系统失败时，使用原有的兜底逻辑
                if size > MAX_SIZE:
                    logging.info(
                        f"种子{torrent_id}大小超过{MAX_SIZE / 1024 / 1024 / 1024:.2f}G，忽略种子"
                    )
                    continue
                if size < MIN_SIZE:
                    logging.info(
                        f"种子{torrent_id}大小小于{MIN_SIZE / 1024 / 1024 / 1024:.2f}G，忽略种子"
                    )
                    continue
                if disk_space - size < SPACE:
                    logging.info(
                        f"种子{torrent_id}大小为{size}，下载后磁盘空间将小于{SPACE / 1024 / 1024 / 1024:.2f}G，忽略种子"
                    )
                    continue
                if seeders <= 0:
                    logging.info(f"种子{torrent_id}无人做种，忽略种子")
                    continue
                if leechers / seeders <= LS_RATIO:
                    logging.info(f"种子{torrent_id}下载/做种比例小于{LS_RATIO}，忽略种子")
                    continue

            logging.info(
                f"{name}种子{torrent_id}，大小为{size / 1024 / 1024 / 1024:.2f}G,状态为：{discount}"
            )
            time.sleep(random.randint(5, 10))
            download_url = get_torrent_url(torrent_id)
            if download_url is None:
                continue
            if not add_torrent(qb_client, download_url, name):
                continue
            disk_space -= size
            flood_torrents.append(
                {
                    "name": name,
                    "id": torrent_id,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "size": size,
                    "url": download_url,
                    "discount": discount,
                    "discount_end_time": (
                        discount_end_time.strftime("%Y-%m-%d %H:%M:%S")
                        if discount_end_time is not None
                        else None
                    ),
                }
            )
            if disk_space <= SPACE:
                logging.info("磁盘空间不足，停止刷流")
                send_telegram_message(
                    f"磁盘空间不足，停止刷流，当前剩余空间为{disk_space / 1024 / 1024 / 1024:.2f}G"
                )
                send_server3_message(
                    f"磁盘空间不足，停止刷流，当前剩余空间为{disk_space / 1024 / 1024 / 1024:.2f}G"
                )
                send_webhook_message(
                    f"磁盘空间不足，停止刷流，当前剩余空间为{disk_space / 1024 / 1024 / 1024:.2f}G"
                )
                break


def setup_mt_session():
    """设置 M-Team 会话"""
    mt_session.headers.update({"x-api-key": APIKEY})
    if PROXY:
        mt_session.proxies = {"http": PROXY, "https": PROXY}


def read_config():
    global flood_torrents
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        flood_torrents = json.load(f)
    if not isinstance(flood_torrents, list):
        flood_torrents = []


def save_config():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(flood_torrents, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    read_config()
    setup_mt_session()
    flood_task()
    save_config() 