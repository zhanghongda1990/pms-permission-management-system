import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main_window import MainWindow
from app.utils.logger import Logger


def main():
    try:
        Logger.info("程序启动")
        app = MainWindow()
        app.run()
    except Exception as e:
        Logger.critical(f"程序异常退出: {e}")
        raise


if __name__ == '__main__':
    main()
