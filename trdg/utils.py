"""
Utility functions
"""

import csv
import os
import numpy as np
from PIL import Image, ImageDraw

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

def mask_to_bboxes(mask, tess=False):
    """Process the mask and turns it into a list of AABB bounding boxes
    """

    mask_arr = np.array(mask)

    bboxes = []

    i = 0
    space_thresh = 1
    while True:
        try:
            color_tuple = ((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255)
            letter = np.where(np.all(mask_arr == color_tuple, axis=-1))
            if space_thresh == 0 and letter:
                x1 = min(bboxes[-1][2] + 1, np.min(letter[1]) - 1)
                y1 = min(bboxes[-1][3] + 1, np.min(letter[0]) - 1) if not tess else min(mask_arr.shape[0] - np.min(letter[0]) + 2, bboxes[-1][1] - 1)
                x2 = max(bboxes[-1][2] + 1, np.min(letter[1]) - 2)
                y2 = max(bboxes[-1][3] + 1, np.min(letter[0]) - 2) if not tess else max(mask_arr.shape[0] - np.min(letter[0]) + 2, bboxes[-1][1] - 1)
                bboxes.append((x1, y1, x2, y2))
                space_thresh += 1
            bboxes.append((
                max(0, np.min(letter[1]) - 1),
                max(0, np.min(letter[0]) - 1) if not tess else max(0, mask_arr.shape[0] - np.max(letter[0]) - 1),
                min(mask_arr.shape[1] - 1, np.max(letter[1]) + 1),
                min(mask_arr.shape[0] - 1, np.max(letter[0]) + 1) if not tess else min(mask_arr.shape[0] - 1, mask_arr.shape[0] - np.min(letter[0]) + 1)
            ))
            i += 1
        except Exception as ex:
            if space_thresh == 0:
                break
            space_thresh -= 1
            i += 1

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
