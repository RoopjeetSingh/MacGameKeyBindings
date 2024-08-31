import cv2
import numpy as np
import json
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
from functools import partial

import pyautogui
from pynput import keyboard
import pynput
from mss import mss
from scrollable_frame import ScrollFrame
from tkinter import filedialog
import time

with open("key_bindings.json") as json_file:
    key_bindings: dict = json.load(json_file)

letters_used = []
current_game = ""
# sets current_game
for i in key_bindings.keys():
    if key_bindings[i]["current game"]:
        current_game = i
# sets current game if no variable for some reason
if not current_game:
    for i in key_bindings.keys():
        current_game = i
        break
for key in key_bindings[current_game].keys():
    if key == "current game":
        continue
    if len(key) > 1:
        for letter in key:
            letters_used.append(letter)
    else:
        letters_used.append(key)


# image conversion- Width= 980/1962   Height= 489/1382

class LetterController:
    """
    Can resize early
    """

    def __init__(self):
        self.currently_pressed = set()
        self.joystick_moved = False
        self.joystick_keys = ""
        self.sides4 = False
        for binding in key_bindings[current_game].keys():
            if binding == "current game":
                continue
            if key_bindings[current_game][binding][0] in ("Joystick", "Joystick4Sides"):
                if key_bindings[current_game][binding][0] == "Joystick4Sides":
                    self.sides4 = True
                self.joystick_keys = binding

        self.cursor_down = False
        self.working = True

    def keyboard_track(self, key: str | pynput.keyboard._darwin.KeyCode = None):
        if key == "no key":
            Joystick.handle_movements(self.joystick_keys, self.currently_pressed,
                                      key_bindings[current_game][self.joystick_keys][2] +
                                      key_bindings[current_game][self.joystick_keys][3])
            self.joystick_moved = True
        if not hasattr(key, "char") or not (key.char in letters_used or key.char in ("p", "z")):
            return
        key = key.char
        if key == 'p':
            self.working = False
            print("paused")
        if key == 'z':
            self.working = True
            print("resumed")
        if self.working:
            for binding in key_bindings[current_game].keys():
                if binding == "current game":
                    continue
                if key in binding and key_bindings[current_game][binding][4]:
                    if key_bindings[current_game][binding][2] != [-1, -1]:
                        if key_bindings[current_game][binding][0] == "Button":
                            with mss() as sct:
                                left, top, width, height = key_bindings[current_game][binding][2][0], \
                                                           key_bindings[current_game][binding][2][1], \
                                                           key_bindings[current_game][binding][3][0], \
                                                           key_bindings[current_game][binding][3][1]
                                monitor = {"left": left - 5, "top": top - 5, "width": width + 10,
                                           "height": height + 10}
                                large_image = np.array(sct.grab(monitor))
                                large_image = cv2.resize(large_image,
                                                         (width + 10, height + 10))
                                large_image = cv2.cvtColor(large_image, cv2.COLOR_BGRA2BGR)
                            button_image = cv2.resize(cv2.imread(key_bindings[current_game][binding][1]),
                                                      key_bindings[current_game][binding][3])
                            position = Button.get_location(button_image
                                                           , large_image,
                                                           key_bindings[current_game][binding][5])
                            if position:
                                Button.click_button(
                                    key_bindings[current_game][binding][2][0] + key_bindings[current_game][binding][3][
                                        0] / 2,
                                    key_bindings[current_game][binding][2][1] + key_bindings[current_game][binding][3][
                                        1] / 2)
                        if key_bindings[current_game][binding][0] in ("Joystick", "Joystick4Sides") and (
                                key not in self.currently_pressed or
                                not self.joystick_moved):
                            self.currently_pressed.add(key)
                            Joystick.handle_movements(binding, self.currently_pressed,
                                                      key_bindings[current_game][binding][2] +
                                                      key_bindings[current_game][binding][3])
                        if key_bindings[current_game][binding][0] == "LongPressButton":
                            self.currently_pressed.add(key)
                            LongPressButton.click_button(key_bindings[current_game][binding][2][0] +
                                                         key_bindings[current_game][binding][3][0] / 2,
                                                         key_bindings[current_game][binding][2][1] +
                                                         key_bindings[current_game][binding][3][1] / 2)
                        if key_bindings[current_game][binding][0] == "PositionButton":
                            PositionButton.click_button(key_bindings[current_game][binding][2][0],
                                                        key_bindings[current_game][binding][2][1])
                    elif key_bindings[current_game][binding][0] == "PositionButton":
                        # type is PositionButton and we have to find location
                        position = PositionButton.get_location()
                        PositionButton.click_button(position[0],
                                                    position[1])
                        key_bindings[current_game][binding][2][0] = position[0]
                        key_bindings[current_game][binding][2][1] = position[1]
                    else:
                        with mss() as sct:
                            org_monitor_size = sct.monitors[0]["width"], sct.monitors[0]["height"]
                            left, top, width, height = 0, 0, org_monitor_size[0], org_monitor_size[1]
                            monitor = {"left": left, "top": top, "width": width,
                                       "height": height}
                            large_image = np.array(sct.grab(monitor))
                            large_image = cv2.resize(large_image,
                                                     (int(pyautogui.size()[0]), int(pyautogui.size()[1])))
                            large_image = cv2.cvtColor(large_image, cv2.COLOR_BGRA2BGR)

                        if key_bindings[current_game][binding][0] == "Button":
                            if key_bindings[current_game][binding][3] == [-1, -1]:
                                Button.identify_image_size(key_bindings[current_game][binding], large_image)
                            # if type(key_bindings[current_game][binding][1]) != list:
                            button_image = cv2.resize(cv2.imread(key_bindings[current_game][binding][1]),
                                                      key_bindings[current_game][binding][3])
                            position = Button.get_location(button_image
                                                           , large_image,
                                                           key_bindings[current_game][binding][5])
                            if position:
                                Button.click_button(position[0] + key_bindings[current_game][binding][3][0] / 2,
                                                    position[1] + key_bindings[current_game][binding][3][1] / 2)
                                key_bindings[current_game][binding][2][0] = position[0]
                                key_bindings[current_game][binding][2][1] = position[1]

                        if key_bindings[current_game][binding][0] == "LongPressButton":
                            if key_bindings[current_game][binding][3] == [-1, -1]:
                                LongPressButton.identify_image_size(key_bindings[current_game][binding], large_image)
                            # if type(key_bindings[current_game][binding][1]) != list:
                            button_image = cv2.resize(cv2.imread(key_bindings[current_game][binding][1]),
                                                      key_bindings[current_game][binding][3])
                            position = LongPressButton.get_location(button_image
                                                                    , large_image,
                                                                    key_bindings[current_game][binding][5])
                            if position:
                                LongPressButton.click_button(
                                    position[0] + key_bindings[current_game][binding][3][0] / 2,
                                    position[1] + key_bindings[current_game][binding][3][1] / 2)
                                key_bindings[current_game][binding][2][0] = position[0]
                                key_bindings[current_game][binding][2][1] = position[1]
                            # else:
                            #     image, index = "", -1
                            #     for j, i in enumerate(key_bindings[current_game][binding][1]):
                            #         if i[1]:
                            #             image = i[0]
                            #             index = j
                            #     button_image = cv2.resize(cv2.imread(image),
                            #                               key_bindings[current_game][binding][3][index])
                            #     position = Button.get_location(button_image
                            #                                    , large_image,
                            #                                    key_bindings[current_game][binding][5])
                            #     if position:
                            #         Button.click_button(
                            #             position[0] + key_bindings[current_game][binding][3][index][0] / 2,
                            #             position[1] + key_bindings[current_game][binding][3][index][1] / 2)
                            #         key_bindings[current_game][binding][2][0] = position[0]
                            #         key_bindings[current_game][binding][2][1] = position[1]

                        if key_bindings[current_game][binding][0] in ("Joystick", "Joystick4Sides"):
                            if key_bindings[current_game][binding][3] == [-1, -1]:
                                Joystick.identify_image_size(key_bindings[current_game][binding], large_image)
                            self.currently_pressed.add(key)
                            position = Joystick.get_location(
                                cv2.resize(cv2.imread(key_bindings[current_game][binding][1]),
                                           key_bindings[current_game][binding][3]),
                                large_image,
                                key_bindings[current_game][binding][5])
                            if position:
                                Joystick.handle_movements(binding, self.currently_pressed,
                                                          [position[0], position[1]] +
                                                          key_bindings[current_game][binding][3])
                                self.joystick_moved = True
                                key_bindings[current_game][binding][2][0] = position[0]
                                key_bindings[current_game][binding][2][1] = position[1]

    def release(self, key=None):
        if not hasattr(key, "char"):
            return
        try:

            try:
                self.currently_pressed.remove(key.char)
            except KeyError:
                pass
            if key.char in self.joystick_keys and self.working:
                self.joystick_moved = False
                self.keyboard_track(key="no key")
        except TypeError:
            print(key)
        if not any(x in letters_used
                   for x in self.currently_pressed):
            pyautogui.mouseUp()
            letter_controller.cursor_down = False
        # else:
        #     self.keyboard_track()


class InputControlTypes:
    @staticmethod
    def identify_image_size(game_key: list, screenshot):
        print("Identifying image")
        start = time.time()
        image = cv2.imread(game_key[1])
        height, width = image.shape[:2]
        thresh, size = 0, 0
        for scale in np.linspace(0.2, 1.0, 40)[::-1]:
            image2 = cv2.resize(image, (int(scale * width), int(scale * height)))
            result = cv2.matchTemplate(screenshot, image2, cv2.TM_SQDIFF_NORMED)
            result = 1 - result
            _, max_value, _, loc2 = cv2.minMaxLoc(result)
            # print([round(scale * width), round(scale * height)])
            if max_value > thresh:
                thresh, size = max_value, scale
        game_key[3] = [round(size * width), round(size * height)]
        game_key[5] = thresh - 0.1
        print([round(size * width), round(size * height)], thresh, key_bindings)
        print(time.time() - start, "time to get size")


class Joystick(InputControlTypes):
    @staticmethod
    def handle_movements(characters: str, char_pressed: set, xywh: list):
        # if xywh[0] != -1:
        if letter_controller.sides4:
            Joystick4Sides.handle_movements(characters, char_pressed, xywh)
        else:
            if characters[0] in char_pressed and characters[2] in char_pressed:
                Joystick.click(xywh[0], xywh[1])
            elif characters[0] in char_pressed and characters[1] in char_pressed:
                Joystick.click(xywh[0], xywh[1] + xywh[3])
            elif characters[3] in char_pressed and characters[2] in char_pressed:
                Joystick.click(xywh[0] + xywh[2], xywh[1])
            elif characters[3] in char_pressed and characters[1] in char_pressed:
                Joystick.click(xywh[0] + xywh[2], xywh[1] + xywh[3])
            elif characters[0] in char_pressed:
                Joystick.click(xywh[0], xywh[1] + xywh[3] / 2)
            elif characters[1] in char_pressed:
                Joystick.click(xywh[0] + xywh[2] / 2, xywh[1] + xywh[3])
            elif characters[2] in char_pressed:
                Joystick.click(xywh[0] + xywh[2] / 2, xywh[1])
            elif characters[3] in char_pressed:
                Joystick.click(xywh[0] + xywh[2], xywh[1] + xywh[3] / 2)

    @staticmethod
    def click(x, y):
        pyautogui.mouseDown(x, y)
        letter_controller.cursor_down = True

    @staticmethod
    def get_location(image, screenshot, threshold):
        result = cv2.matchTemplate(screenshot, image, cv2.TM_SQDIFF_NORMED)
        _, max_value, __, loc2 = cv2.minMaxLoc(1 - result)
        print(max_value)
        if max_value >= threshold:
            return loc2
        else:
            return []


class Button(InputControlTypes):
    """
    Works like a charm
    """

    @staticmethod
    def click_button(x, y):
        current_pos = pyautogui.position()
        pyautogui.mouseUp()
        pyautogui.click(x=x, y=y)
        if letter_controller.cursor_down:
            pyautogui.mouseDown(current_pos.x, current_pos.y)
        else:
            pyautogui.moveTo(current_pos.x, current_pos.y)

    @staticmethod
    def get_location(image, screenshot, threshold):
        result = cv2.matchTemplate(screenshot, image, cv2.TM_SQDIFF_NORMED)
        # cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
        result = 1 - result
        min_value, max_value, loc1, loc2 = cv2.minMaxLoc(result)
        print(max_value, loc2)
        if max_value >= threshold:
            return loc2
        else:
            cv2.imwrite("../image.png", screenshot)
            return []


class LongPressButton(InputControlTypes):
    @staticmethod
    def click_button(x, y):
        pyautogui.mouseDown(x, y)
        letter_controller.cursor_down = True

    @staticmethod
    def get_location(image, screenshot, threshold):
        result = cv2.matchTemplate(screenshot, image, cv2.TM_SQDIFF_NORMED)
        result = 1 - result
        min_value, max_value, loc1, loc2 = cv2.minMaxLoc(result)
        print(max_value, loc2)
        if max_value >= threshold:
            return loc2
        else:
            cv2.imwrite("../image.png", screenshot)
            return []


class Joystick4Sides(InputControlTypes):
    @staticmethod
    def handle_movements(characters: str, char_pressed: set, xywh: list):
        if characters[0] in char_pressed:
            Joystick.click(xywh[0], xywh[1] + xywh[3] / 2)
        elif characters[1] in char_pressed:
            Joystick.click(xywh[0] + xywh[2] / 2, xywh[1] + xywh[3])
        elif characters[2] in char_pressed:
            Joystick.click(xywh[0] + xywh[2] / 2, xywh[1])
        elif characters[3] in char_pressed:
            Joystick.click(xywh[0] + xywh[2], xywh[1] + xywh[3] / 2)

    @staticmethod
    def click(x, y):
        pyautogui.mouseDown(x, y)
        letter_controller.cursor_down = True

    @staticmethod
    def get_location(image, screenshot, threshold):
        result = cv2.matchTemplate(screenshot, image, cv2.TM_SQDIFF_NORMED)
        _, max_value, __, loc2 = cv2.minMaxLoc(1 - result)
        if max_value >= threshold:
            return loc2
        else:
            return []


class PositionButton(InputControlTypes):
    @staticmethod
    def click_button(x, y):
        current_pos = pyautogui.position()
        pyautogui.mouseUp()
        pyautogui.click(x=x, y=y)
        if letter_controller.cursor_down:
            pyautogui.mouseDown(current_pos.x, current_pos.y)
        else:
            pyautogui.moveTo(current_pos.x, current_pos.y)

    @staticmethod
    def get_location():
        time.sleep(2)
        return [pyautogui.position().x, pyautogui.position().y]


letter_controller = LetterController()


class Screen(tk.Frame):
    """
    Resize new image
    """

    def __init__(self, screen):
        tk.Frame.__init__(self, screen)
        self.screen = screen
        self.var_active_list = {}
        self.scrollFrame = None
        self.image_added = False
        self.new_key_type = "Joystick"
        self.new_file_path = ""
        self.add_game_on = False
        self.create_page()

    def change_letters(self):
        letters_used.clear()
        for key in key_bindings[current_game].keys():
            if key == "current game":
                continue
            if len(key) > 1:
                for letter in key:
                    letters_used.append(letter)
            else:
                letters_used.append(key)
        global letter_controller
        letter_controller = LetterController()

    @staticmethod
    def save_json(window):
        with open("key_bindings.json", "w") as file:
            key_bindings2 = key_bindings.copy()
            for game in key_bindings2:
                for keys in key_bindings2[game]:
                    if keys == "current game":
                        continue
                    key_bindings2[game][keys][2] = [-1, -1]
            json.dump(key_bindings2, file, indent=4)
        window.destroy()
        exit()

    def create_page(self):
        row_no = 0
        weight = 6
        row_no = self.create_page_basics(row_no, weight)
        row_no += 1
        for game in key_bindings.keys():
            frame, row_frame, row_no = self.every_game(game, row_no, weight)
        self.pack_scroll_frame()
        # print(self.scrollFrame.viewPort.winfo_screenmmwidth())

    def reset_all_keys(self):
        for game in key_bindings:
            for keys in key_bindings[game]:
                if keys == "current game":
                    continue
                key_bindings[game][keys][2] = [-1, -1]

    def delete_button(self, game, binding):
        key_bindings[game].pop(binding, None)
        self.change_letters()
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page()

    def active_button(self, game, binding):
        self.var_active_list[game][binding].set("Not Active") if self.var_active_list[game][binding].get() == "Active" \
            else self.var_active_list[game][binding].set("Active")
        key_bindings[game][binding][4] = True if self.var_active_list[game][binding].get() == "Active" else False

    def change_current_game(self, game):
        global current_game
        current_game = game
        for i in key_bindings.keys():
            key_bindings[i]["current game"] = False

        key_bindings[game]["current game"] = True
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page()

    def add_key(self, game):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page_with_add_image(game)

    def create_page_with_add_image(self, game_key):
        def change_type(new_type):
            new_type = new_type.replace("-", "")
            self.new_key_type = new_type
            self.add_key(game_key)

        def upload_file():
            self.new_file_path = filedialog.askopenfilename()
            if self.new_file_path:
                image = Image.open(self.new_file_path)
                image = image.resize((75, 75))
                image = ImageOps.expand(image, border=5, fill="red")
                image = ImageTk.PhotoImage(image)
                image_upload.config(image=image)
                image_upload.image = image
                self.new_file_path = ""

        row_no = 0
        weight = 7
        self.create_page_basics(row_no, weight)
        row_no += 1
        for game in key_bindings.keys():
            frame, row_frame, row_no = self.every_game(game, row_no, weight)
            if game == game_key:
                image_upload = tk.Button(frame, text="Add Image", command=upload_file)
                if self.new_file_path:
                    image = Image.open(self.new_file_path)
                    image = image.resize((75, 75))
                    image = ImageOps.expand(image, border=5, fill="red")
                    image = ImageTk.PhotoImage(image)
                    image_upload.config(image=image)
                    image_upload.image = image
                image_upload.grid(row=row_frame, column=1)
                type_options = ["Button", "Joystick", "Joystick-4-Sides", "Long-Press-Button", "Position-Button"]
                key_type = tk.StringVar()
                key_type.set(self.new_key_type)  # default value
                tk.OptionMenu(frame, key_type, *type_options,
                              command=lambda changed_type: change_type(changed_type)).grid(row=row_frame, column=2)
                if self.new_key_type.replace("-", "") in ("Button", "LongPressButton", "PositionButton"):
                    key_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'q', 'r',
                                   's', 't', 'u', 'v', 'w', 'x', 'y']
                    letter_in_new_key_game = []
                    for key in key_bindings[game_key].keys():
                        if key == "current game":
                            continue
                        if len(key) > 1:
                            for letter in key:
                                letter_in_new_key_game.append(letter)
                        else:
                            letter_in_new_key_game.append(key)

                    for i in letter_in_new_key_game:
                        if i in key_options:
                            key_options.remove(i)
                    key_var = tk.StringVar()
                    key_var.set(key_options[0])
                    tk.OptionMenu(frame, key_var, *key_options).grid(row=row_frame, column=3)
                    tk.Button(frame, text="Add Key",
                              command=lambda: self.add_key_to_dic(key_var.get(), game_key)).grid(row=row_frame,
                                                                                                 column=4)
                if self.new_key_type.replace("-", "") in ("Joystick", "Joystick4Sides"):
                    key_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'q', 'r',
                                   's', 't', 'u', 'v', 'w', 'x', 'y']
                    letter_in_new_key_game = []
                    for key in key_bindings[game_key].keys():
                        if key == "current game":
                            continue
                        if len(key) > 1:
                            for letter in key:
                                letter_in_new_key_game.append(letter)
                        else:
                            letter_in_new_key_game.append(key)

                    for i in letter_in_new_key_game:
                        if i in key_options:
                            key_options.remove(i)

                    key_var1 = tk.StringVar()
                    key_var1.set(key_options[0])
                    tk.OptionMenu(frame, key_var1, *key_options) \
                        .grid(row=row_frame, column=3)
                    key_var2 = tk.StringVar()
                    key_var2.set(key_options[1])
                    tk.OptionMenu(frame, key_var2, *key_options).grid(row=row_frame, column=4)
                    key_var3 = tk.StringVar()
                    key_var3.set(key_options[2])
                    tk.OptionMenu(frame, key_var3, *key_options).grid(row=row_frame, column=5)
                    key_var4 = tk.StringVar()
                    key_var4.set(key_options[3])
                    tk.OptionMenu(frame, key_var4, *key_options).grid(row=row_frame, column=6)
                    tk.Button(
                        frame, text="Add Key",
                        command=lambda: self.add_key_to_dic(
                            key_var1.get() + key_var2.get() + key_var3.get() + key_var4.get(), game_key)).grid(
                        row=row_frame, column=7)

                row_no += 1
        self.pack_scroll_frame()

    def add_key_to_dic(self, image_key: str, game_key):
        key_bindings[game_key][image_key] = [self.new_key_type, self.new_file_path, [-1, -1], [-1, -1], True, 0.8]
        self.change_letters()
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page()

    def add_game(self, name):
        key_bindings[name] = {"current game": False}
        self.add_game_on = False
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page()

    def pack_scroll_frame(self):
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def delete_game(self, game):
        key_bindings.pop(game, None)
        global current_game
        for i in key_bindings.keys():
            if key_bindings[i]["current game"]:
                current_game = i
        # sets current game if no variable for some reason
        if not current_game:
            for i in key_bindings.keys():
                current_game = i
                break
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page()

    def every_game(self, game, row_no, weight):
        self.var_active_list[game] = {}
        self.columnconfigure(row_no, weight=weight, uniform="fred")
        frame = tk.Frame(self.scrollFrame.viewPort)
        frame.columnconfigure(0, weight=weight, uniform="fred")
        frame.grid(row=row_no, column=0, columnspan=weight, padx=10, pady=5)
        row_frame = 0
        tk.Label(frame, text=game.title(), font=("Arial", 25)).grid(row=row_frame, column=0, columnspan=2,
                                                                    sticky=tk.W, pady=5)
        tk.Button(frame, text="Add Key", font=("Ariel", 15), command=partial(self.add_key, game)).grid(
            row=row_frame, column=2,
            columnspan=2, pady=5)
        highlight_thick = 3 if game == current_game else 0
        button_border = tk.Frame(frame, highlightbackground="#ADD8E6",
                                 highlightthickness=highlight_thick, bd=0)
        button_border.grid(row=row_frame, column=4, columnspan=2, pady=5)
        tk.Button(button_border, text="Current Game", font=("Ariel", 15),
                  command=partial(self.change_current_game, game)).pack()
        tk.Button(frame, text="Delete Game", font=("Ariel", 15), command=partial(self.delete_game, game)).grid(
            row=row_frame, column=6,
            columnspan=2, pady=5)
        row_frame += 1
        for binding in key_bindings[game].keys():
            if binding == "current game":
                continue
            tk.Label(frame, width=5).grid(row=row_frame, column=0, pady=5)
            image = Image.open(key_bindings[game][binding][1])
            image = image.resize((75, 75))
            image = ImageTk.PhotoImage(image)
            label = tk.Label(frame, image=image)
            label.photo = image
            label.grid(row=row_frame, column=1, pady=5)
            tk.Label(frame, text=key_bindings[game][binding][0]).grid(row=row_frame, column=2, pady=5)
            tk.Label(frame, text=binding).grid(row=row_frame, column=3, pady=5)
            self.var_active_list[game][binding] = tk.StringVar()
            active_not = "Active" if key_bindings[game][binding][4] else "Not Active"
            self.var_active_list[game][binding].set(active_not)
            active = tk.Button(frame, textvariable=self.var_active_list[game][binding],
                               command=partial(self.active_button, game, binding), width=10)
            active.grid(row=row_frame, column=4, pady=5, columnspan=2)
            delete = tk.Button(frame, text="Delete", command=partial(self.delete_button, game, binding))
            delete.grid(row=row_frame, column=6, pady=5)
            row_frame += 1
        row_no += 1
        return frame, row_frame, row_no

    def turn_on_add_game(self):
        self.add_game_on = True
        for widget in self.winfo_children():
            widget.destroy()
        self.create_page()

    def create_page_basics(self, row_no, weight):
        self.scrollFrame = ScrollFrame(self)
        self.columnconfigure("all", weight=1, uniform="fred")
        self.columnconfigure(row_no, weight=weight, uniform="fred")
        frame = tk.Frame(self.scrollFrame.viewPort)
        frame.columnconfigure(0, weight=weight, uniform="fred")
        frame.grid(row=row_no, column=0, columnspan=weight)
        # tk.Label(frame, text="Image").grid(row=row_no, column=0)
        # tk.Label(frame, text="Type").grid(row=row_no, column=1)
        # tk.Label(frame, text="Keys").grid(row=row_no, column=2)
        # tk.Label(frame, text="Active").grid(row=row_no, column=3)
        # tk.Label(frame, text="Delete").grid(row=row_no, column=4)
        # row_no += 1
        tk.Button(self.scrollFrame.viewPort, text="Reset Keys", font=("Ariel", 15), command=self.reset_all_keys).grid(
            row=row_no, column=0, columnspan=2)
        tk.Button(self.scrollFrame.viewPort, text="Add Game", font=("Ariel", 15), command=self.turn_on_add_game).grid(
            row=row_no, column=2, columnspan=2)
        if self.add_game_on:
            game_name = tk.Entry(self.scrollFrame.viewPort)
            game_name.grid(row=row_no, column=2, columnspan=2)
            game_name.focus()
            tk.Button(self.scrollFrame.viewPort, text="Add Game", font=("Ariel", 15), background="white",
                      command=lambda: self.add_game(game_name.get())).grid(
                row=row_no, column=4, columnspan=2)
        return row_no


with keyboard.Listener(on_press=letter_controller.keyboard_track,
                       on_release=letter_controller.release) as listener:
    root = tk.Tk()
    root.geometry("650x800")
    root.wm_title("Game with Keys")
    Screen(root).pack(side="top", fill="both", expand=True)
    root.protocol("WM_DELETE_WINDOW", lambda: Screen.save_json(root))
    root.mainloop()
    listener.join()
