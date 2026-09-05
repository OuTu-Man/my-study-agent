import uuid

import uvicorn
from fastapi import FastAPI, Request

from common.logger import logger, setup_logging

# 初始化：让 Uvicorn 日志被 Loguru 接管
setup_logging()

app = FastAPI(title="Loguru 演示", version="1.0")


# ----- 中间件：为每个请求注入 request_id 并记录访问日志 -----
@app.middleware("http")
async def log_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    # 使用 contextualize 为整个请求生命周期绑定上下文
    with logger.contextualize(request_id=request_id, method=request.method, path=request.url.path):
        logger.info("Request started")
        try:
            response = await call_next(request)
            logger.info(f"Request finished - status: {response.status_code}")
            return response
        except Exception:
            logger.exception("Unhandled exception occurred")
            raise


# ----- 示例路由 -----
@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello, Loguru!"}


@app.get("/divide/{num}")
async def divide(num: int):
    logger.debug(f"Dividing 100 by {num}")
    try:
        result = 100 / num
        logger.info(f"Result: {result}")
        return {"result": result}
    except ZeroDivisionError:
        logger.error(f"Division by zero attempted for {num}")
        # 也可用 exception 方法自动捕获异常堆栈
        # logger.exception("Division by zero")
        return {"error": "Cannot divide by zero"}, 400


# ----- 启动入口（可选）-----
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # 禁用 Uvicorn 默认日志配置，完全由我们控制
    )
