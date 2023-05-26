import numpy as np
import cv2
from mss import mss
from PIL import Image

'''
# на нормальном hsv up and down: 80-160. Они поделены на 2.
#example = [0, 255, 179]  HSV UP = 80
example= [166, 255, 0] # HSV DOWN = 40
pixel_rgb = np.array(example, dtype=np.uint8)

# Преобразуйте RGB в HSV
pixel_hsv = cv2.cvtColor(np.array([[pixel_rgb]]), cv2.COLOR_RGB2HSV)[0][0]

print(pixel_hsv)
'''


def generate_digit_one(width, height):
    thickness = width // 4
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            if j > width - 1 - thickness or (thickness > i and j >= width // 2):
                digit_array[i][j] = 1

    return np.array(digit_array)


def generate_digit_zero(width, height):
    digit_array = [[0 for _ in range(width)] for _ in range(height)]
    thickness = width // 4
    for i in range(height):
        for j in range(width):
            # if j == width - 1 or i == 0 or j == 0 or i == height - 1:
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


'''
new_arr = generate_digit_two1(4, 8) & generate_digit_zero(4, 8)
print(generate_digit_two1(4, 8))
print(generate_digit_zero(4, 8))
matches_count = np.sum(new_arr)
print(new_arr)
'''

# 800
a = generate_digit_zero(20, 40)
b = generate_digit_one(20, 40)
c = generate_digit_two1(20, 40)
d = generate_digit_two2(20, 40)
w = len(a[0])
'''
count = 0
for i in range(len(a)):
    for j in range(w):
        if a[i][j] == b[i][j]:
            count += 1
print(count)
'''
print(c)
