from setuptools import setup, find_packages

setup(
    name="sergei-mikhailov-tg-channel-reader",
    version="0.9.2",
    description="OpenClaw skill: read Telegram channels via MTProto",
    author="Sergey Mikhailov",
    url="https://github.com/bzSega/sergei-mikhailov-tg-channel-reader",
    license="MIT",
    py_modules=["reader", "reader_telethon", "tg_reader_unified", "tg_check", "tg_state"],
    install_requires=[
        "pyrogram>=2.0.0",
        "tgcrypto>=1.2.0",
        "telethon>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "tg-reader=tg_reader_unified:main",
            "tg-reader-pyrogram=reader:main",
            "tg-reader-telethon=reader_telethon:main",
            "tg-reader-check=tg_check:main",
        ],
    },
    python_requires=">=3.9",
)
