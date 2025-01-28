# Suspider 网站爬虫工具

一个基于PyQt5的网站爬虫工具，支持多层级网页抓取和自定义配置。

## 功能特点

- 支持多层级网页抓取
- 可配置爬取深度
- 自定义请求延迟时间
- 支持日志级别配置
- 优雅的退出机制
- 自动过滤无效链接
- SQLite数据存储

## 环境要求

- Python 3.6+
- PyQt5
- 其他依赖请查看 requirements.txt

## 安装方法

1. 克隆项目代码：

```bash
git clone https://github.com/seaung/suspider.git
cd suspider
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python main.py <url>
```

### 命令行参数

- `url`: 要爬取的网站URL（必需）
- `-d, --depth`: 爬取深度，默认为3
- `-t, --delay`: 请求延迟时间（秒），默认为1.0
- `--log-level`: 日志级别，可选值：DEBUG、INFO、WARNING、ERROR、CRITICAL，默认为INFO

### 示例

```bash
# 使用默认配置爬取网站
python main.py https://example.com

# 设置爬取深度为5，延迟2秒
python main.py https://example.com -d 5 -t 2.0

# 设置日志级别为DEBUG
python main.py https://example.com --log-level DEBUG
```

## 注意事项

1. 请遵守网站的robots.txt规则
2. 建议设置适当的请求延迟，避免对目标网站造成压力
3. 爬取深度越大，耗时越长，请根据实际需求设置