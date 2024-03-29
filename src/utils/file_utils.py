import logging
import re
import shutil
import os


def split_filepath(path):  # returns the file and the directory of a file path as an ordered pair
    directory = path.split("\\")
    filename = directory.pop()
    return "\\".join(directory), filename


def rename_file(initial_loc, new_name):
    path = split_filepath(initial_loc)
    initial_filename = path[1]
    final_loc = path[0] + "\\" + new_name

    os.rename(initial_loc, final_loc)
    logging.debug(f'Renamed {initial_filename} to {new_name}')
    return final_loc


def get_most_recent_file(files: list[tuple[str, float]]):
    if not isinstance(files, list):
        raise ValueError("files must be a list")

    return max(files, key=lambda x: x[1])[0]


def filter_files(file_dir, must_contain, file_type):
    logging.debug(f"searching for \"{file_type}\" files in \"{file_dir}\" that contain \"{must_contain}\"")
    # Get files with their timestamps from path
    files_with_timestamps = [(filename, os.path.getmtime(os.path.join(file_dir, filename))) for filename in
                             os.listdir(file_dir) if isinstance(filename, str)]
    logging.debug(f"found {len(files_with_timestamps)} total files in {file_dir}")

    # Filter files
    valid_files = [(filename, timestamp) for filename, timestamp in files_with_timestamps if
                   (must_contain in filename) & (filename.endswith(file_type) is True)]
    if not valid_files:
        logging.warn(f'WARNING: No valid {file_type} filenames containing {must_contain} found in {file_dir}')
        raise ValueError(f"No valid {file_type} files containing {must_contain} found in {file_dir}")
    logging.debug(f"found {len(valid_files)} valid files")
    return valid_files


def replace(string, replace_arr):
    for replace_obj in replace_arr:
        string = re.sub(replace_obj["replace"], replace_obj["with"], string)
    return string


def move_file(initial_loc, final_dir):
    filename = split_filepath(initial_loc)[1]
    shutil.move(initial_loc, final_dir + "\\" + filename)
    logging.debug(f'Moved {filename} from {initial_loc} to {final_dir}')
    return final_dir + "\\" + filename


def move_csv(initial_dir, final_dir, filename_must_contain, replace_arr):
    if not initial_dir or not final_dir:
        return
    filetype = '.csv'
    file_name = get_most_recent_file(filter_files(initial_dir, filename_must_contain, filetype))
    if not file_name:
        return
    updated_path = move_file(initial_dir + "\\" + file_name, final_dir)
    updated_name = replace(file_name, replace_arr)
    return rename_file(updated_path, updated_name)


def dir_format(file_dir: str):
    # if the file_dir is relative, make it absolute from the project directory
    if file_dir.startswith("..\\"):
        ROOT_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        return os.path.join(ROOT_DIR, file_dir[3:])
    return file_dir
