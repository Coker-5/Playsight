# 部署到阿里云指南

## 一、服务器准备

### 1. 购买 ECS 实例
- **配置建议**: 2核4G 或更高（Kafka + ClickHouse 需要内存）
- **系统**: Ubuntu 22.04 LTS / CentOS 7+
- **带宽**: 5Mbps 或以上
- **磁盘**: 50GB+ SSD（数据量大需要更大）

### 2. 配置安全组（重要！）
开放以下端口：
- `22` - SSH
- `80` - HTTP
- `5000` - Flask 应用（或配置 Nginx 后关闭）
- `8123` - ClickHouse HTTP 端口（建议只开放内网或加认证）
- `9092` - Kafka（建议只开放内网）
- `9000` - ClickHouse 原生端口（建议只开放内网）

## 二、服务器环境安装

### 1. 连接服务器
```bash
ssh root@<你的服务器IP>
```

### 2. 安装 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh

# 或手动安装
apt-get update
apt-get install -y docker.io docker-compose

# 启动 Docker
systemctl start docker
systemctl enable docker
```

### 3. 安装 uv（Python 包管理器）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

## 三、部署应用

### 1. 上传代码到服务器

**方式 A - 使用 git（推荐）**
```bash
# 在服务器上克隆代码
git clone <你的git仓库地址> /opt/game-analytics
cd /opt/game-analytics
```

**方式 B - 使用 scp**
```bash
# 在本地执行
scp -r /Users/zyq/my-projects/game-analytics root@<服务器IP>:/opt/
```

### 2. 修改配置文件

编辑 `game_analytics/config.py` 或创建 `.env` 文件：

```bash
cd /opt/game-analytics

# 创建环境变量文件
cat > .env << 'EOF'
# ClickHouse 配置
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=game

# Kafka 配置
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_EVENTS=tp_game_events

# Flask 配置
FLASK_PORT=5000
FLASK_DEBUG=false

# 模拟器配置
SIMULATE_SPEED_UP=60
EOF
```

### 3. 修改 Docker 配置（适配阿里云）

需要修改 `docker-compose.yml` 中的 Kafka 广告地址：

```bash
# 获取服务器内网 IP
ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

编辑 `docker-compose.yml`：

```yaml
services:
  kafka:
    image: apache/kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_NODE_ID=1
      - KAFKA_PROCESS_ROLES=broker,controller
      - KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka:9093
      - KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      # 修改为服务器内网 IP 或 0.0.0.0
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://<服务器内网IP>:9092
      - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_AUTO_CREATE_TOPICS_ENABLE=true
    volumes:
      - kafka_data:/var/lib/kafka/data
    restart: always

  clickhouse:
    image: clickhouse/clickhouse-server:23
    container_name: clickhouse
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      # 如需自定义配置，可挂载配置文件
      # - ./clickhouse-config.xml:/etc/clickhouse-server/config.d/custom.xml
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
    restart: always

volumes:
  kafka_data:
  clickhouse_data:
```

### 4. 启动基础设施

```bash
cd /opt/game-analytics

# 启动 ClickHouse 和 Kafka
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 初始化 ClickHouse 表

```bash
# 进入 ClickHouse 容器
docker exec -it clickhouse clickhouse-client

# 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS game;

# 创建事件表
USE game;

CREATE TABLE IF NOT EXISTS game_events (
    event_time DateTime,
    event_name String,
    user_id String,
    server String,
    device String,
    level String,
    pay_amount Float32,
    duration UInt32,
    properties Map(String, String)
) ENGINE = MergeTree()
ORDER BY (event_time, user_id)
PARTITION BY toYYYYMMDD(event_time);

# 退出
exit
```

### 6. 安装 Python 依赖并启动应用

```bash
cd /opt/game-analytics

# 安装依赖
uv sync

# 测试启动 Flask
uv run main.py

# 按 Ctrl+C 停止，然后使用后台运行
```

### 7. 使用 systemd 管理 Python 服务

创建服务文件：

```bash
cat > /etc/systemd/system/game-analytics.service << 'EOF'
[Unit]
Description=Game Analytics Dashboard
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/game-analytics
Environment="PATH=/root/.local/bin:/usr/local/bin:/usr/bin"
Environment="CLICKHOUSE_HOST=localhost"
Environment="CLICKHOUSE_PORT=8123"
Environment="KAFKA_BOOTSTRAP_SERVERS=localhost:9092"
Environment="FLASK_PORT=5000"
Environment="FLASK_DEBUG=false"
ExecStart=/root/.local/bin/uv run main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
systemctl daemon-reload

# 启动服务
systemctl start game-analytics

# 设置开机自启
systemctl enable game-analytics

# 查看状态
systemctl status game-analytics
```

### 8. 启动 Kafka 消费者（可选，如果需要实时消费）

```bash
cat > /etc/systemd/system/game-consumer.service << 'EOF'
[Unit]
Description=Game Analytics Kafka Consumer
After=network.target docker.service game-analytics.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/game-analytics
Environment="PATH=/root/.local/bin:/usr/local/bin:/usr/bin"
Environment="CLICKHOUSE_HOST=localhost"
Environment="KAFKA_BOOTSTRAP_SERVERS=localhost:9092"
ExecStart=/root/.local/bin/uv run scripts/consume.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start game-consumer
systemctl enable game-consumer
```

### 9. 配置 Nginx 反向代理（推荐）

```bash
# 安装 Nginx
apt-get install -y nginx

# 创建配置文件
cat > /etc/nginx/sites-available/game-analytics << 'EOF'
server {
    listen 80;
    server_name <你的域名或服务器IP>;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /static {
        alias /opt/game-analytics/static;
        expires 30d;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/game-analytics /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # 删除默认配置

# 测试并重载
nginx -t
systemctl restart nginx
```

## 四、验证部署

### 1. 检查服务状态
```bash
# 查看所有服务
docker-compose ps
systemctl status game-analytics
systemctl status game-consumer
systemctl status nginx

# 查看端口监听
netstat -tlnp | grep -E '5000|8123|9092|80'
```

### 2. 生成测试数据
```bash
cd /opt/game-analytics
uv run scripts/simulate.py
```

### 3. 访问应用
- 如果配置了 Nginx: `http://<服务器IP>/`
- 直接访问 Flask: `http://<服务器IP>:5000/`
- API 测试: `http://<服务器IP>/api/overview`

## 五、生产环境建议

### 1. 安全性
```bash
# 配置防火墙（UFW）
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# ClickHouse 添加密码认证
# 编辑 clickhouse/users.xml 或使用环境变量
```

### 2. 数据备份
```bash
# 创建备份脚本
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份 ClickHouse
docker exec clickhouse clickhouse-client --query="BACKUP DATABASE game TO '/tmp/backup_$DATE'"
docker cp clickhouse:/tmp/backup_$DATE $BACKUP_DIR/

# 保留最近7天备份
find $BACKUP_DIR -name "backup_*" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# 添加到定时任务
crontab -e
# 添加: 0 2 * * * /opt/backup.sh
```

### 3. 监控建议
- 使用阿里云云监控
- 或使用 Prometheus + Grafana 自建监控

### 4. SSL/HTTPS（可选）
使用 Let's Encrypt 免费证书：
```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## 六、常见问题

### Q1: Kafka 连接失败？
- 检查安全组是否开放 9092
- 检查 `KAFKA_ADVERTISED_LISTENERS` 是否配置正确（使用内网 IP）

### Q2: ClickHouse 无法连接？
- 检查容器状态: `docker logs clickhouse`
- 检查端口: `telnet localhost 8123`

### Q3: Flask 无法访问？
- 检查是否监听 0.0.0.0（默认 Flask 只监听 127.0.0.1）
- 修改 `main.py` 确保 `app.run(host='0.0.0.0')`

### Q4: 内存不足？
- 升级 ECS 配置
- 或限制 Docker 容器内存使用

## 七、更新代码

```bash
cd /opt/game-analytics

# 拉取最新代码
git pull

# 重启服务
systemctl restart game-analytics
systemctl restart game-consumer
```
