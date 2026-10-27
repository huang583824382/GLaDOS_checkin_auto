"""青龙面板和云函数入口，共用主脚本的签到逻辑。"""

import sys

from glados import main


def start():
    return main()


def main_handler(event, context):
    return start()


if __name__ == '__main__':
    sys.exit(start())
