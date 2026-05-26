# -*- coding: utf-8 -*-
import sys
from core.automation import OnmyojiBot


def main():

    try:
        times = int(input('请输入需要挑战的循环次数：'))
        if times <= 0:
            print("次数必须大于0")
            return

        bot = OnmyojiBot()
        if not bot.templates:
            print("由于没有加载到模板图片，程序无法运行。请检查 images 文件夹。")
            input("\n按回车键退出...")
            return

        print("\n初始化成功，正在监视游戏窗口，请勿最小化游戏...")
        bot.run(times)

    except ValueError:
        print('输入异常，请输入正确的整数。')
    except Exception as e:
        print(f'程序运行中发生未知错误: {e}')

    print("\n任务结束。")
    input("按回车键退出...")


if __name__ == '__main__':
    main()