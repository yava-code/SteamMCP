# server.py
from fastmcp import FastMCP

# 1. Инициализируем сервер, даем ему имя и описание.
mcp = FastMCP(
    name="hello_server"
)


# 2. С помощью декоратора @mcp.tool() превращаем функцию в инструмент.
@mcp.tool()
def say_hello(name: str) -> str:
    """
    Greets the person with the given name.

    Args:
        name: The name of the person to greet.
    """
    return f"Hello, {name}!"


# 3. Эта строка нужна, чтобы сервер можно было запустить напрямую.
if __name__ == "__main__":
    mcp.run()