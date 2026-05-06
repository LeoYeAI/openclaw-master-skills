"""xyfcli - 下单订货 CLI 工具主入口"""

import typer
from .shop import shop_app
from .order import order_app
from .config_cmd import config_app

app = typer.Typer(
    name="xyfcli",
    help="下单订货 CLI 工具",
    rich_markup_mode="rich",
)

# 注册子命令
app.add_typer(shop_app, name="shop")
app.add_typer(order_app, name="order")
app.add_typer(config_app, name="config")


if __name__ == "__main__":
    app()
