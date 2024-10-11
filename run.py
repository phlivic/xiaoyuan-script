import config

import os
import time
import subprocess
import random

import cv2
import pyautogui
import pytesseract

import pygetwindow as gw
import numpy as np
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class ImageNotFoundError(Exception):
    """自定义异常：图像不存在错误"""
    pass

def is_emulator_running(index=0):
    cmd = f'"{config.path}" list2'
    result = subprocess.check_output(cmd, shell=True, encoding='iso-8859-1', errors='ignore')
    subprolog = result.split(',')
    print(subprolog)
    if subprolog[0] == str(index) and subprolog[4] == '1':
        return True
    return False

def get_emulator_window(title='雷电模拟器'):
    # 获取所有窗口
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        raise Exception(f"未找到标题为 '{title}' 的窗口")
    return windows[0]

#启动模拟器
def launch_emulator(index=0):
    cmd = f'"{config.path}" launch --index {index}'
    os.system(cmd)
    print("启动模拟器中...")
    while not is_emulator_running(index):
        print("等待模拟器启动...")
        time.sleep(5)  # 每5秒检查一次
    print("模拟器已启动")
    time.sleep(5)

def screenshot_emulator(index=0, save_path=config.savepath):
    # 确保保存路径存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 截取屏幕截图并保存到模拟器内部
    cmd = f'"{config.path}" adb --index {index} --command "screencap -p /sdcard/screenshot.png"'
    os.system(cmd)
    
    # 从模拟器内部拉取截图到本地指定路径
    cmd = f'"{config.path}" pull --index {index} /sdcard/screenshot.png {save_path}'
    os.system(cmd)

#打开app
def open_target(thresh=0.8, imgs_path=config.imgspath, target_=None, name=None, check=False, check_target=None):
    print(f"尝试打开图像对应内容...: {name}")
    target_img_path = os.path.join(imgs_path, target_)
    if not os.path.exists(target_img_path):
        raise ImageNotFoundError(f"目标图像 {target_img_path} 不存在")
    
    #TODO:截图大小
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 读取目标图像
    target = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)
    w, h = target.shape[::-1]

    # 将截图转换为灰度图像
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # 使用模板匹配查找目标图像
    result = cv2.matchTemplate(gray_screenshot, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = thresh
    if max_val >= threshold:
        # 获取匹配位置的中心点
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2

        # 点击匹配位置
        pyautogui.click(center_x, center_y)
        print(f"找到目标！已点击位置: ({center_x}, {center_y})")

        #TODO:更合理的等待打开方式
        if check:
            finish_open(target_=check_target, name=name)
        time.sleep(2)
        return True
    else:
        print("未找到匹配的目标图像")
        return False

def finish_open(imgs_path=config.imgspath, target_=None, name=None):
    if not target_:
        return
    print(f"检查是否完成打开...: {name}")
    target_img_path = os.path.join(imgs_path, target_)
    if not os.path.exists(target_img_path):
        raise ImageNotFoundError(f"目标图像 {target_img_path} 不存在")
    
    # 读取目标图像
    target = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)
    w, h = target.shape[::-1]

    max_val, threshold = 0, 0.8

    while max_val >= threshold:
        #TODO:截图大小
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # 将截图转换为灰度图像
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # 使用模板匹配查找目标图像
        result = cv2.matchTemplate(gray_screenshot, target, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f'"未找到对应目标，正在继续寻找...{name}"')
        time.sleep(0.02)
    print("已找到目标，继续执行。")

def check_target(thresh=0.8, imgs_path=config.imgspath, target_=None, name=None):
    if not target_:
        return False
    print(f"检查对应目标是否存在...: {name}")
    target_img_path = os.path.join(imgs_path, target_)
    if not os.path.exists(target_img_path):
        raise ImageNotFoundError(f"目标图像 {target_img_path} 不存在")
    
    #TODO:截图大小
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 读取目标图像
    target = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)
    w, h = target.shape[::-1]

    # 将截图转换为灰度图像
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # 使用模板匹配查找目标图像
    result = cv2.matchTemplate(gray_screenshot, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = thresh

    if max_val < threshold:
        print(f'"暂未发现{name}"')
        time.sleep(0.02)
        return False
    else:
        return True

def match(round=10):
    #match_path = os.path.join(config.imgspath, config.match)
    winnum, winrate = 0, 0.0
    for i in range(round):
        #TODO：这里的识别逻辑有点问题
        open_target(target_=config.step1, name='进入对战', check=True, check_target=config.check1)
        start = False
        Finish = False
        turn = 0
        while not Finish:
            turn += 1
            s = answer(start=start)
            if s or turn == 10:
                start = True
                print("识别到开始做题。无法识别时会进行猜测。")
            Finish = check_target(target_=config.match_finish, name="已完成!")
        time.sleep(2)

        open_target(target_=config.match_finish, name="已完成!")
        time.sleep(0.5)

        open_target(target_=config.step2, name="正在返回")
        time.sleep(1)

        res = check_target(thresh=0.99, target_=config.win, name="正在检查结果")

        res_str = "Lose" if not res else "Win"
        if res:
            winnum += 1
        winrate = winnum / (i + 1)

        print(f'"Round {i}: Result: {res_str}" Winrate: {winrate}')
        time.sleep(1)

        open_target(target_=config.step3, name="准备下一场对局", check=True, check_target=config.match_check)
    
    return

def draw_symbol(symbol, start_x, start_y, size=100):
    """模拟手写符号（大于、小于、等于）"""
    # 确保鼠标在绘制区域开始
    pyautogui.moveTo(start_x, start_y)

    if symbol == ">":
        # 一笔画出大于号
        pyautogui.mouseDown()  # 按下鼠标左键
        pyautogui.dragTo(start_x + size, start_y + size // 2, duration=0.2)  # 斜线 /
        pyautogui.moveTo(start_x + size // 2, start_y + size // 4)
        pyautogui.dragTo(start_x, start_y + size // 2, duration=0.2)  # 回到顶端
        pyautogui.mouseUp()  # 松开鼠标左键

    elif symbol == "<":
        # 一笔画出小于号
        pyautogui.mouseDown()  # 按下鼠标左键
        pyautogui.dragTo(start_x - size, start_y + size // 2, duration=0.2)  # 斜线 \
        pyautogui.moveTo(start_x - size // 2, start_y + size // 4)
        pyautogui.dragTo(start_x, start_y + size // 2, duration=0.2)  # 回到底端
        pyautogui.mouseUp()  # 松开鼠标左键

def answer(start=False):

    switchcase = [1, -1]

    screenshot = pyautogui.screenshot()
    
    # 将截图转换为 OpenCV 格式（从 RGB 转为 BGR）
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 使用 pytesseract 提取图片中的数字，限定只识别数字部分
    #config_str = '--psm 6 outputbase digits'  # 配置 tesseract 只识别数字
    #text = pytesseract.image_to_string(screenshot, config=config_str)
    
    y_min, y_max = 300, 500
    cropped_screenshot = screenshot[y_min:y_max, 890:1675]  # 截取纵坐标为 y_min 到 y_max 的区域
    
    # 使用 matplotlib 显示裁剪后的图像
    #plt.imshow(cv2.cvtColor(cropped_screenshot, cv2.COLOR_BGR2RGB))
    #plt.title("Cropped Screenshot for OCR")
    #plt.show()
    
    # 使用 pytesseract 对裁剪后的截图进行文字识别
    config_str = "--psm 6"  # 配置为单块文字识别模式

    area1 = cropped_screenshot[:, :330]
    # area2 = cropped_screenshot[:, 450:]

    # plt.imshow(cv2.cvtColor(area2, cv2.COLOR_BGR2RGB))
    # plt.title("Cropped Screenshot for OCR")
    # plt.show()

    
    text = pytesseract.image_to_string(cropped_screenshot, config=config_str)
    
    print("识别结果如下：")
    print(text)

    # 提取识别到的数字
    numbers = [int(s) for s in text.split() if s.isdigit()]
    
    screen_width, screen_height = pyautogui.size()

    draw_area_y = screen_height // 2
    center_x = screen_width // 2
    center_y = draw_area_y + (screen_height // 18)

    

    # 检查是否识别到了至少两个数字
    if len(numbers) < 2:
        print("识别到的数字不足两个，无法作答")
        if start:
            switch = random.choice(switchcase)
            if switch == 1:
                draw_symbol(">", center_x, center_y, size=100)
                print(f"在模拟器中猜测了符号: >")
                time.sleep(0.2)

            elif switch == -1:
                draw_symbol("<", center_x, center_y, size=100)
                print(f"在模拟器中猜测了符号: <")
                time.sleep(0.2)
        return False
    num1, num2 = numbers[:2]
    
    '''
    t1 = pytesseract.image_to_string(area1, config=config_str)
    text = pytesseract.image_to_string(cropped_screenshot, config=config_str)

    numbers1 = [int(s) for s in t1.split() if s.isdigit()]
    numbers = [int(s) for s in text.split() if s.isdigit()]
    print(numbers)
    print(numbers1)

    if len(numbers1) < 1 or len(numbers) < 2:
        print("识别到的数字不足两个，无法作答")
        return
    
    
    num1, num2 = numbers1[-1], numbers[1]
    '''

    print(num1, num2)

    if num1 > num2:
        symbol = ">"
    elif num1 < num2:
        symbol = "<"
    else:
        symbol = "="
    
    draw_symbol(symbol, center_x, center_y, size=100)
    print(f"在模拟器中手写了符号: {symbol}")
    time.sleep(0.1)

    return True

if __name__ == "__main__":
    launch_emulator(0)
    #screenshot_emulator(0, 'screenshot.png')
    open_target(target_=config.target_app, name='app')

    exist = False
    while not exist:
        exist = check_target(target_=config.check_app, name="app")
    time.sleep(2)

    open_target(target_=config.match, name='口算pk', check=True, check_target=config.match_check)
    time.sleep(2)
    
    match(config.times)