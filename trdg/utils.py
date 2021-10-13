import csv
import os
import numpy as np
import pathlib
from PIL import ImageDraw
import shutil


def load_dict(lang):
    """Read the dictionnary file and returns all words in it.
    """

    lang_dict = []
    with open(
        os.path.join(os.path.dirname(__file__), "dicts", lang + ".txt"),
        "r",
        encoding="utf8",
        errors="ignore",
    ) as d:
        lang_dict = [l for l in d.read().splitlines() if len(l) > 0]
    return lang_dict


def load_fonts(lang):
    """Load all fonts in the fonts directories
    """

    if lang == "cn":
        return [
            os.path.join(os.path.dirname(__file__), "fonts/cn", font)
            for font in os.listdir(os.path.join(os.path.dirname(__file__), "fonts/cn"))
        ]
    else:
        return [
            os.path.join(os.path.dirname(__file__), "fonts/latin", font)
            for font in os.listdir(
                os.path.join(os.path.dirname(__file__), "fonts/latin")
            )
        ]


def split_text_to_words(text):
    splitted_text = []
    for w in text.split(' '):
        splitted_text.append(w)
        splitted_text.append(' ')
    splitted_text.pop()
    return splitted_text


def mask_to_bboxes(mask, text, tess=False):
    """Process the mask and turns it into a list of AABB bounding boxes
    """

    mask_arr = np.array(mask)

    bboxes = []

    splitted_text = split_text_to_words(text)
    for i in range(len(splitted_text)):
        color_tuple = ((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255)
        letter = np.where(np.all(mask_arr == color_tuple, axis=-1))
        if len(letter[0]) == 0 or len(letter[1]) == 0:
            continue
        x1 = max(0, np.min(letter[1]) - 1)
        x2 = max(0, np.min(letter[0]) - 1) if not tess else max(0, mask_arr.shape[0] - np.max(letter[0]) - 1)
        y1 = min(mask_arr.shape[1] - 1, np.max(letter[1]) + 1)
        y2 = min(mask_arr.shape[0] - 1, np.max(letter[0]) + 1) if not tess else min(mask_arr.shape[0] - 1,
                                                                                    mask_arr.shape[0] -
                                                                                    np.min(letter[0]) + 1)
        bboxes.append((x1, x2, y1, y2))

    return bboxes


def draw_bounding_boxes(img, bboxes, color="green"):
    d = ImageDraw.Draw(img)

    for bbox in bboxes:
        if len(bbox) > 4:
            bbox = bbox[1:5]
        d.rectangle(bbox, outline=color)


def load_bounding_boxes(background_img_path):
    background_img_no_ext = os.path.splitext(background_img_path)[0]
    boxes_file = f'{background_img_no_ext}_boxes.csv'
    with open(boxes_file, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader)
        data = [tuple(map(int, rec)) for rec in reader]
        return data


class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return self.start <= other <= self.end

    def __contains__(self, item):
        return self.__eq__(item)

    def __iter__(self):
        yield self

    def __str__(self):
        return '[{0},{1}]'.format(self.start, self.end)


def create_dir_if_not_exists(dir_path):
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def move_dir_files(source_dir, target_dir):
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        shutil.move(os.path.join(source_dir, file_name), target_dir)
