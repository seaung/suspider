import argparse
import logging
import signal
import sys
from typing import NoReturn

from superspider.crawler import Crawler


def setup_logging(log_level: str) -> None:
    """配置日志记录

    Args:
        log_level: 日志级别
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def signal_handler(signum: int, _) -> NoReturn:
    """处理信号

    Args:
        signum: 信号编号
    """
    logging.info(f"接收到信号 {signum}，正在优雅退出...")
    sys.exit(0)


def parse_args() -> argparse.Namespace:
    """解析命令行参数

    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(description='网站爬虫工具')
    parser.add_argument('url', help='要爬取的网站URL')
    parser.add_argument('-d', '--depth', type=int, default=3, help='爬取深度 (默认: 3)')
    parser.add_argument('-t', '--delay', type=float, default=1.0, help='请求延迟时间(秒) (默认: 1.0)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='日志级别 (默认: INFO)')
    return parser.parse_args()


def main() -> None:
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_args()

        # 设置日志
        setup_logging(args.log_level)

        # 设置信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 启动爬虫
        logging.info(f"开始爬取 {args.url}，深度：{args.depth}，延迟：{args.delay}秒")
        crawler = Crawler(args.url, max_depth=args.depth, request_delay=args.delay)
        crawler.start()
        logging.info("爬取完成")

    except KeyboardInterrupt:
        logging.info("用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
