import csv
import math
import os
import random as rnd

from PIL import Image, ImageFilter, ImageDraw

from trdg import computer_text_generator, background_generator, distorsion_generator
from trdg.utils import mask_to_bboxes, draw_bounding_boxes, load_bounding_boxes, get_random_color

try:
    from trdg import handwritten_text_generator
except ImportError as e:
    print("Missing modules for handwritten text generation.")


class FakeTextDataGenerator(object):

    MIN_RECTANGLE_DIM = 20

    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """

        cls.generate(*t)

    @classmethod
    def generate(
        cls,
        index,
        text,
        font,
        out_dir,
        size,
        extension,
        skewing_angle,
        random_skew,
        blur,
        random_blur,
        background_type,
        distorsion_type,
        distorsion_orientation,
        is_handwritten,
        name_format,
        width,
        alignment,
        text_color,
        orientation,
        space_width,
        character_spacing,
        margins,
        fit,
        output_mask,
        word_split,
        image_dir,
        output_bboxes,
        rect
    ):

        margin_top, margin_left, margin_bottom, margin_right = margins
        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        ##########################
        # Create picture of text #
        ##########################
        if is_handwritten:
            if orientation == 1:
                raise ValueError("Vertical handwritten text is unavailable")
            image, mask = handwritten_text_generator.generate(text, text_color)
        else:
            image, mask = computer_text_generator.generate(
                text,
                font,
                text_color,
                size,
                orientation,
                space_width,
                character_spacing,
                fit,
                word_split,
            )
        random_angle = rnd.randint(0 - skewing_angle, skewing_angle)

        rotated_img = image.rotate(
            skewing_angle if not random_skew else random_angle, expand=1
        )

        rotated_mask = mask.rotate(
            skewing_angle if not random_skew else random_angle, expand=1
        )

        #############################
        # Apply distorsion to image #
        #############################
        if distorsion_type == 0:
            distorted_img = rotated_img  # Mind = blown
            distorted_mask = rotated_mask
        elif distorsion_type == 1:
            distorted_img, distorted_mask = distorsion_generator.sin(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )
        elif distorsion_type == 2:
            distorted_img, distorted_mask = distorsion_generator.cos(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )
        else:
            distorted_img, distorted_mask = distorsion_generator.random(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )

        ##################################
        # Resize image to desired format #
        ##################################

        # Horizontal text
        if orientation == 0:
            new_width = int(
                distorted_img.size[0]
                * (float(size - vertical_margin) / float(distorted_img.size[1]))
            )
            resized_img = distorted_img.resize(
                (new_width, size - vertical_margin), Image.ANTIALIAS
            )
            resized_mask = distorted_mask.resize((new_width, size - vertical_margin), Image.NEAREST)
            background_width = width if width > 0 else new_width + horizontal_margin
            background_height = size
        # Vertical text
        elif orientation == 1:
            new_height = int(
                float(distorted_img.size[1])
                * (float(size - horizontal_margin) / float(distorted_img.size[0]))
            )
            resized_img = distorted_img.resize(
                (size - horizontal_margin, new_height), Image.ANTIALIAS
            )
            resized_mask = distorted_mask.resize(
                (size - horizontal_margin, new_height), Image.NEAREST
            )
            background_width = size
            background_height = new_height + vertical_margin
        else:
            raise ValueError("Invalid orientation")

        #############################
        # Generate background image #
        #############################
        background_img_path = None
        if background_type == 0:
            background_img = background_generator.gaussian_noise(
                background_height, background_width
            )
        elif background_type == 1:
            background_img = background_generator.plain_white(
                background_height, background_width
            )
        elif background_type == 2:
            background_img = background_generator.quasicrystal(
                background_height, background_width
            )
        elif background_type == 3:
            background_img, background_img_path = background_generator.image(
                background_height, background_width, image_dir,
            )
        else:
            background_img = background_generator.any_color_with_bias_to_white(
                background_height, background_width
            )
        background_mask = Image.new(
            "RGB", (background_width, background_height), (0, 0, 0)
        )

        ##################################
        # Draw rectangle #
        ##################################
        if rect:
            rect_coords = FakeTextDataGenerator.draw_rectangle(background_img)
        else:
            rect_coords = None
            #############################
            # Place text with alignment #
            #############################

            new_text_width, _ = resized_img.size

            if alignment == 0:  # or width == -1:
                background_img.paste(resized_img, (margin_left, margin_top), resized_img)
                background_mask.paste(resized_mask, (margin_left, margin_top))
            elif alignment == 1:
                background_img.paste(
                    resized_img,
                    (int(background_width / 2 - new_text_width / 2), margin_top),
                    resized_img,
                )
                background_mask.paste(
                    resized_mask,
                    (int(background_width / 2 - new_text_width / 2), margin_top),
                )
            else:
                background_img.paste(
                    resized_img,
                    (background_width - new_text_width - margin_right, margin_top),
                    resized_img,
                )
                background_mask.paste(
                    resized_mask,
                    (background_width - new_text_width - margin_right, margin_top),
                )

        ##################################
        # Apply gaussian blur #
        ##################################

        gaussian_filter = ImageFilter.GaussianBlur(
            radius=blur if not random_blur else rnd.randint(0, blur)
        )
        final_image = background_img.filter(gaussian_filter)
        final_mask = background_mask.filter(gaussian_filter)

        #####################################
        # Generate name for resulting image #
        #####################################
        if name_format == 0:
            name = "{}_{}".format(text, str(index))
        elif name_format == 1:
            name = "{}_{}".format(str(index), text)
        elif name_format == 2:
            name = str(index)
        else:
            print("{} is not a valid name format. Using default.".format(name_format))
            name = "{}_{}".format(text, str(index))

        loaded_bboxes = []
        invoke_ind = 0
        if background_img_path is not None:
            name = FakeTextDataGenerator._generate_name_from_background_img(background_img_path, name)
            loaded_bboxes = load_bounding_boxes(background_img_path)
            if len(loaded_bboxes) > 0:
                invoke_ind = loaded_bboxes[0][0] + 1

        image_name = "{}.{}".format(name, extension)
        mask_name = "{}_mask.png".format(name)
        box_name = "{}_boxes.csv".format(name)
        image_box_name = "{}_box.png".format(name)
        tess_box_name = "{}.box".format(name)

        # Save the image
        if out_dir is not None:
            image_out_path = os.path.join(out_dir, image_name)
            mask_out_path = os.path.join(out_dir, mask_name)
            box_out_path = os.path.join(out_dir, image_box_name)
            final_image.convert("RGB").save(image_out_path)
            if output_mask == 1:
                final_mask.convert("RGB").save(mask_out_path)
            if output_bboxes == 1 or output_bboxes == 3:
                if rect_coords is not None:
                    bboxes = [rect_coords]
                else:
                    bboxes = mask_to_bboxes(final_mask, text)
                bboxes.extend(loaded_bboxes)
                if output_bboxes == 3:
                    draw_bounding_boxes(final_image, bboxes)
                    final_image.convert("RGB").save(box_out_path)
                FakeTextDataGenerator.write_boxes(out_dir, box_name, bboxes, invoke_ind)
            if output_bboxes == 2:
                bboxes = mask_to_bboxes(final_mask, tess=True)
                with open(os.path.join(out_dir, tess_box_name), "w") as f:
                    for bbox, char in zip(bboxes, text):
                        f.write(" ".join([char] + [str(v) for v in bbox] + ['0']) + "\n")
        else:
            if output_mask == 1:
                return final_image.convert("RGB"), final_mask.convert("RGB")
            return final_image.convert("RGB")

    @staticmethod
    def _generate_name_from_background_img(background_img_path, curr_name):
        basename = os.path.split(background_img_path)[-1]
        basename_no_ext = os.path.splitext(basename)[0]
        return f"{curr_name}_{basename_no_ext}"

    @staticmethod
    def write_boxes(out_dir, box_name, bboxes, invoke_ind):
        with open(os.path.join(out_dir, box_name), "w") as csv_file:
            writer = csv.writer(csv_file)
            header = ['ind', 'x1', 'y1', 'x2', 'y2']
            writer.writerow(header)
            for bbox in bboxes:
                if len(bbox) == 4:
                    row_to_write = [invoke_ind, *bbox]
                else:
                    row_to_write = bbox
                writer.writerow(row_to_write)

    @staticmethod
    def draw_rectangle(background_img):
        draw = ImageDraw.Draw(background_img)
        width, height = background_img.size
        rect_width = rnd.randint(FakeTextDataGenerator.MIN_RECTANGLE_DIM, math.floor(width / 2))
        rect_height = rnd.randint(FakeTextDataGenerator.MIN_RECTANGLE_DIM, math.floor(height / 2))
        p1_x = rnd.randint(0, width - rect_width - 1)
        p1_y = rnd.randint(0, height - rect_height - 1)
        p2_x = p1_x + rect_width
        p2_y = p2_x + rect_height
        draw.rectangle([(p1_x, p1_y), (p2_x, p2_y)], fill=get_random_color())
        return p1_x, p1_y, p2_x, p2_y
