import logging
import sys
from pathlib import Path

from loguru import logger

# 日志存储目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 清除默认 handler，避免重复输出
logger.remove()

# ----- 控制台输出 -----
logger.add(
    sys.stdout,
    level="DEBUG",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# ----- 文件输出（按日轮转，保留3天）-----
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    rotation="00:00",  # 每天午夜轮转
    retention="3 days",  # 保留7天
    compression="zip",  # 压缩历史日志
    enqueue=True,  # 异步写入，提升并发性能
)

# 可选：单独记录错误日志（可独立配置）
logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    rotation="00:00",
    retention="10 days",
    enqueue=True,
)


# ----- 关键：拦截标准 logging 日志（Uvicorn 使用 logging）-----
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取 Loguru 的日志级别
        level = logger.level(record.levelname).name
        # 将 logging 记录转发给 Loguru
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """将 Uvicorn 的日志全部重定向到 Loguru"""
    # 修改 Uvicorn 使用的 logger 的 handler
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        log_obj = logging.getLogger(logger_name)
        log_obj.handlers = []
        log_obj.handlers = [InterceptHandler()]
        # 设置日志级别，确保所有日志都被拦截
        log_obj.setLevel(logging.DEBUG)
        log_obj.propagate = False


# 全局导出 logger 实例
__all__ = ["logger", "setup_logging"]
