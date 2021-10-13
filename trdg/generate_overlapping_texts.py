import argparse
import math
import random
import shlex
import shutil
import subprocess

from utils import create_dir_if_not_exists, Range, move_dir_files

RESULT_DIR = 'res'
OUT_DIR = 'out'
TEMP_OUT_DIR = 'out_1'

MIN_WIDTH = 100
MAX_WIDTH = 800
MIN_HEIGHT = 64
MAX_HEIGHT = 100
MIN_NUM_WORDS_BACKGROUND = 1
MAX_NUM_WORDS_BACKGROUND = 5
MIN_MARGIN = 0
MAX_MARGIN = 20
NUM_MARGINS = 4


def run_shell_command(command):
    subprocess.run(shlex.split(command))


def generate_single_layer_text(num_samples, num_words_background, width, height, margin_list_first_run):
    margin_list = ','.join([str(i) for i in margin_list_first_run])
    command = f"python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c {num_samples} " \
              f"-w {num_words_background} -tc '#000000,#FFFFFF' -obb 3 -ws -b 4 -na 1 -wd {width} -f " \
              f"{height} --output_dir {TEMP_OUT_DIR} -e png " \
              f"-m '{margin_list}'"
    run_shell_command(command)


def generate_second_layer_text(num_samples, width, height, margin_second_run):
    margin_list = ','.join(([str(margin_second_run)] * NUM_MARGINS))
    command = f"python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c {num_samples} " \
              f"-tc '#000000,#FFFFFF' -obb 3 -ws -b 3 -id {TEMP_OUT_DIR} -na 1 -f {height} -e png -wd {width} " \
              f"-m '{margin_list}'"
    run_shell_command(command)


def generate_random_values():
    width = random.randint(MIN_WIDTH, MAX_WIDTH)
    height = random.randint(MIN_HEIGHT, MAX_HEIGHT)
    num_words_background = random.randint(MIN_NUM_WORDS_BACKGROUND, MAX_NUM_WORDS_BACKGROUND)
    margin_list_first_run = random.sample(range(MIN_MARGIN, MAX_MARGIN), NUM_MARGINS)
    margin_second_run = random.randint(MIN_MARGIN, MAX_MARGIN)
    return width, height, num_words_background, margin_list_first_run, margin_second_run


def generate_data(num_iterations, num_samples, create_overlap):
    for i in range(num_iterations):
        create_dir_if_not_exists(OUT_DIR)
        create_dir_if_not_exists(TEMP_OUT_DIR)

        width, height, num_words_background, margin_list_first_run, margin_second_run = \
            generate_random_values()

        generate_single_layer_text(num_samples, num_words_background, width, height, margin_list_first_run)

        if create_overlap:
            generate_second_layer_text(num_samples, width, height, margin_second_run)
            move_dir_files(OUT_DIR, RESULT_DIR)
        else:
            move_dir_files(TEMP_OUT_DIR, RESULT_DIR)

        shutil.rmtree(TEMP_OUT_DIR)
        shutil.rmtree(OUT_DIR)


def generate_data_by_overlap_ratio(num_iterations, num_samples, overlap_ratio):
    num_overlap_iterations = math.floor(num_iterations * overlap_ratio)
    generate_data(num_overlap_iterations, num_samples, True)
    generate_data(num_iterations - num_overlap_iterations, num_samples, False)


def parse_args():
    parser = argparse.ArgumentParser(description='Generate images with texts')
    parser.add_argument('-i', '--iterations', type=int, help='Number of iterations to run', required=True)
    parser.add_argument('-s', '--samples', type=int, help='Number of samples generated in each iteration',
                        required=True)
    parser.add_argument('-o', '--overlap', type=float, help='Non overlapping fraction',
                        choices=Range(0.0, 1.0), required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    create_dir_if_not_exists(RESULT_DIR)
    generate_data_by_overlap_ratio(args.iterations, args.samples, args.overlap)


if __name__ == '__main__':
    main()

