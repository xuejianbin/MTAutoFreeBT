import os
import time
import dotenv
import logging
from init_directories import init_directories

dotenv.load_dotenv(verbose=True, override=True)
from flood_refactored import flood_task, setup_mt_session, read_config, save_config

CYCLE = int(float(os.environ.get("CYCLE", 0.5)) * 60 * 60)

if __name__ == "__main__":
    # 初始化目录
    init_directories()
    
    read_config()
    setup_mt_session()
    while True:
        flood_task()
        save_config()
        logging.info(f"完成本次循环，等待下一次循环。")
        time.sleep(CYCLE)
