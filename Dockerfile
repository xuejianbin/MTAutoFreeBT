FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    locales \
    && rm -rf /var/lib/apt/lists/*

# 设置中文和时区
RUN sed -i 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8
ENV LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    TZ=Asia/Shanghai

# 拷贝代码
COPY ./app /app

# 持久化目录
VOLUME ["/app/logs", "/app/data", "/app/mt_auto_freebt.db"]

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 默认暴露Web端口
EXPOSE 5000

# 通过环境变量切换运行模式
# RUN_MODE=web 运行Web管理界面，否则运行主循环
ENV RUN_MODE=web

CMD ["sh", "-c", "if [ \"$RUN_MODE\" = 'web' ]; then python start_web.py; else python main.py; fi"]
