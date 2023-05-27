import numpy as np
import cv2
from mss import mss
from PIL import Image

np.set_printoptions(suppress=True, linewidth=np.nan)
np.set_printoptions(threshold=np.inf)


def generate_digit_one1(width, height):
    thickness = width // 4
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            if j > width - 1 - thickness or (thickness > i and j >= width // 2):
                digit_array[i][j] = 1

    return np.array(digit_array)


def generate_digit_one2(width, height):
    thickness = width // 4
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            if (thickness - 1 < j < 2 * thickness) or (thickness > i and j < width // 2):
                digit_array[i][j] = 1

    return np.array(digit_array)


def generate_digit_zero(width, height):
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    thickness = width // 4
    for i in range(height):
        for j in range(width):
            if j > width - 1 - thickness or j < thickness or i < thickness or i > height - 1 - thickness:
                digit_array[i][j] = 1

    return np.array(digit_array)


def generate_digit_two1(width, height):
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    thickness = width // 4
    for i in range(height):
        for j in range(width):
            if i < thickness or i > height - thickness - 1:
                digit_array[i][j] = 1
            if height // 2 - thickness // 2 <= i <= height // 2 + thickness // 2:
                digit_array[i][j] = 1
            if (i <= height // 2 and j > width - thickness - 1) or (i > height // 2 and j < thickness):
                digit_array[i][j] = 1
    return np.array(digit_array)


def generate_digit_two2(width, height):
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    thickness = width // 4
    for i in range(height):
        for j in range(width):
            if i < thickness or i > height - thickness - 1:
                digit_array[i][j] = 1
            if height // 2 - thickness // 2 - 1 <= i <= height // 2 + thickness // 2 - 1:
                digit_array[i][j] = 1
            if (i <= height // 2 and j > width - thickness - 1) or (i > height // 2 and j < thickness):
                digit_array[i][j] = 1
    return np.array(digit_array)


def correlation(a, b):
    w = len(a[0])
    count = 0
    for i in range(len(a)):
        for j in range(w):
            if a[i][j] == 1 and b[i][j] == 255 or a[i][j] == 0 and b[i][j] == 0:
                count += 1
    return count


def color_masks(mask_frame):
    s_h = 255
    v_h = 255
    s_l = 50
    v_l = 50

    green_upper = np.array([80, s_h, v_h])
    green_lower = np.array([41, s_l, v_l])
    yellow_upper = np.array([39, s_h, v_h])
    yellow_lower = np.array([15, s_l, v_l])
    blue_upper = np.array([140, s_h, v_h])
    blue_lower = np.array([82, s_l, v_l])

    mask_green = cv2.inRange(mask_frame, green_lower, green_upper)
    mask_yellow = cv2.inRange(mask_frame, yellow_lower, yellow_upper)
    mask_blue = cv2.inRange(mask_frame, blue_lower, blue_upper)

    return {"green": mask_green, "blue": mask_blue, "yellow": mask_yellow}


def define_color(mask_frame):
    map_of_colors = color_masks(mask_frame)
    count_green = 0
    count_blue = 0
    count_yellow = 0
    for i in range(map_of_colors["green"].shape[0]):
        for j in range(map_of_colors["green"].shape[1]):
            if map_of_colors["green"][i][j] == 255:
                count_green += 1
            if map_of_colors["yellow"][i][j] == 255:
                count_yellow += 1
            if map_of_colors["blue"][i][j] == 255:
                count_blue += 1

    if count_green > count_blue and count_green > count_yellow:
        return "green", map_of_colors["green"]
    elif count_blue > count_green and count_blue > count_yellow:
        return "blue", map_of_colors["blue"]
    else:
        return "yellow", map_of_colors["yellow"]


def process(frame, start_point, rect_height, rect_width, key, skip):
    end_point = (start_point[0] + rect_width, start_point[1] + rect_height)
    color = (255, 0, 0)
    thickness = 2
    rect = cv2.rectangle(frame, start_point, end_point, color, thickness)
    # hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV) # for screen
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # for camera
    mask_frame = hsv_frame[start_point[1]:end_point[1], start_point[0]:end_point[0]]

    color_name, mask = define_color(mask_frame)

    intersections = [correlation(generate_digit_one1(rect_width, rect_height), mask),
                     correlation(generate_digit_one2(rect_width, rect_height), mask),
                     correlation(generate_digit_two1(rect_width, rect_height), mask),
                     correlation(generate_digit_two2(rect_width, rect_height), mask),
                     correlation(generate_digit_zero(rect_width, rect_height), mask)]

    # Посмотреть как работает моя маска. Сделай 3 цифры размером 20*40. Так же есть огромное подохрение что маскирование по цветам не работает корректно.
    # Он определяет что количество в маске по пикселям одинаково для green и yellow - будто это одинаковые цвета.
    # Если с цветами будет напряг, то пофиг, главное отгадать цифру, а цвет будешь определять так, как у него в проекте, а не своим способом.
    # Ну то есть цвет отдельно определяешь.

    # Последние записи. Читать отсюда
    # у меня 26597 против 28800. Это 92%. Это с двойкой и 0, Моя проблема цифра 1. Сейчас стоит порог в 98%.
    # Почему проблема с 1? Потому что расстояние от 0 до 1 очень маленькое. Я должен брать цифру 1 впритык, однако границы нуля то же захватываются.
    # То есть я должен еще буду как то отрисовывать много единиц, где к примеру нога единицы будет в центре, справа, слева и промежуточные положения.
    # На больших масштабах (~16000) программа уже не вытягивает по производительности. Оно и не мудрено, у тебя очень много сравнений. Надо это оптимизировать.
    # Ты считаешь для всех цветов, а надо для самого одного самого успешного.

    # Как увеличить Производительность: У тебя каждую милисекунду цикла идет запрос в функцию process, где производятся долгие вычисления. Можно завести
    # переменную в цикле, которую на каждую итерацию обновляем. А к примеру каждый 10ый раз вызываем функцию process. Только нужно позаботится о том,
    # чтоб рамка выводилась. То есть само вычисление чтоб было каждые 10ый раз. Так же переменную надо будет сбрасывать, по достижению большого числа.

    # Как увеличить точность вердикта?
    # Можно установить мои веса, чтоб больший приоритет отдавался 1, чтоб 1 и 0 были не равны.

    # Для цифры один, можно в рамке сделать две зазубрены на два больших пикселя (если считать, что width цифры 1 == 4)
    # И они будут ровно по центру, таким образом для 1, место в рамке - строго по центру.

    org = end_point
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7

    if key:
        print(color_name)
        print(intersections)
        print(mask)

    digit = ""
    max_value = max(intersections)
    if max_value / (rect_width * rect_height) >= 0.80:
        for i in range(len(intersections)):  # 4
            if max_value == intersections[i]:
                if i == 0 or i == 1:
                    digit = "One"
                elif i == 4:
                    digit = "Zero"
                else:
                    digit = "Two"
                cv2.putText(rect, color_name + digit, org, font, font_scale, color, thickness, cv2.LINE_AA)
                cv2.putText(rect,
                            str(rect_height) + " * " + str(rect_width),
                            (50, 100), font, font_scale, color, thickness, cv2.LINE_AA)
                return frame

    cv2.putText(rect, str(rect_height) + " * " + str(rect_width) + " = " + str(rect_width * rect_height), (50, 100),
                font, font_scale, color, thickness, cv2.LINE_AA)
    return frame


def gstreamer_pipeline(
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=30,
        flip_method=0,
):
    return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=true"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
    )


def main():
    print('Press 4 to Quit the Application\n')
    '''
    #for screen
    sct = mss()
    w, h = 800, 1200
    monitor = {'top': 0, 'left': 0, 'width': w, 'height': h}
    '''
    # for camera
    # for standard camera just 0
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)
    # h, w, _ = cap.read()
    h, w = 720, 1280

    rect_height = 40
    rect_width = 20
    start_point = [int(w / 2 - rect_width / 2), int(h / 2 - rect_height / 2)]  # width, height
    skip = 0
    while True:
        query = False
        key = cv2.waitKeyEx(10)  # тайм-аут 10 миллисекунд

        if key == ord('q') or key == 27 or w <= start_point[0] + rect_width or rect_width in [0, 1,
                                                                                              2]:  # клавиша 'q' или Esc:
            cv2.destroyAllWindows()
            break
        if start_point[1] + rect_height >= h or start_point[0] <= 0 or start_point[1] <= 0:
            cv2.destroyAllWindows()
            break
        if key == ord('='):  # увеличить "+"
            rect_width += 4
            rect_height = rect_width * 2
        elif key == ord('-'):  # уменьшить "-"
            rect_width -= 4
            rect_height = rect_width * 2
        elif key == 2490368:  # стрелка вверх "↑"
            start_point[1] -= 5
        elif key == 2621440:  # стрелка вниз "↓"
            start_point[1] += 5
        elif key == 2424832:  # стрелка влево "<-"
            start_point[0] -= 5
        elif key == 2555904:  # стрелка вправо '->'
            start_point[0] += 5
        elif key == ord('5'):
            query = True

        skip += 1
        if skip > 2000000000:
            skip = 0

        # frame = np.array(Image.frombytes('RGB', (w, h), sct.grab(monitor).rgb)) # for screen
        _, frame = cap.read()  # for camera

        invert = process(frame, start_point, rect_height, rect_width, query, skip)

        # cv2.imshow('Inverted', cv2.cvtColor(invert, cv2.COLOR_RGB2BGR)) # for screen
        cv2.imshow('Inverted', invert)  # for camera


if __name__ == "__main__":
    main()
