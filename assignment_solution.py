import os
import json
import shutil
from glob import glob
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def get_config(config_file_path):
    """
    Read config file and return config dictionary

    :param config_file_path:
    :return:
    """

    with open(config_file_path, "r") as fp:
        config = json.load(fp)

    return config


def get_txt_file_links(base_url, num_files):
    """
    Parse a given url to extract links of text files

    :param base_url: URL of the webpage containing text file links
    :param num_files: Number of text file links to grab
    :return:
    """

    main_page = BeautifulSoup(
        requests.get(base_url).content,
        "html.parser"
    )

    txt_files = []

    for maybe_txt_file in main_page.find_all("a"):
        link_text = maybe_txt_file.text

        if link_text.endswith(".txt"):
            # TODO: Could be made better using href
            txt_files.append(
                requests.compat.urljoin(
                    base_url,
                    link_text
                )
            )
        if len(txt_files) == num_files:
            break

    return txt_files


def download_txt_files(url_list, destination_dir="play_files"):
    """
    Take a list of text file links and download the files
    in the specified directory

    :param url_list: List of links
    :param destination_dir: Path of the directory to download
    :return:
    """

    if not os.path.exists(destination_dir):
        os.mkdir(destination_dir)
    else:
        shutil.rmtree(destination_dir)
        os.mkdir(destination_dir)

    for file_url in url_list:
        file_response = requests.get(file_url)

        if file_response.status_code == 200:
            save_path = os.path.join(
                destination_dir,
                file_url.rpartition("/")[-1]
            )

            with open(save_path, "w") as fp:
                fp.write(file_response.content.decode())


def get_file_data(file_parent_dir="play_files"):
    """
    Read txt files in the specified directory, return
    the list of txt file paths and their content

    :param file_parent_dir: Path of the dir containing txt files
    :return:
    """

    file_list = glob(os.path.join(file_parent_dir, "*.txt"))
    file_data = []

    for file_path in file_list:
        with open(file_path, "r") as fp:
            file_data.append(fp.read())

    return file_list, file_data


def get_line_number_mapping(file_path_list, file_data):
    """
    Take a list of text files, and their contents,
    and count the number of words in each line of each
    file. Store these counts in a dictionary for each
    file.

    :param file_path_list:
    :param file_data:
    :return:
    """

    file_wise_line_number_mapping = {}

    for file_path, each_file_data in zip(file_path_list, file_data):
        file_name = file_path.rpartition("/")[-1]
        file_wise_line_number_mapping[file_name] = {}

        file_lines = each_file_data.splitlines()
        for line_index, line in enumerate(file_lines):
            file_wise_line_number_mapping[file_name][line_index + 1] = len(
                line.strip().split()
            )

    return file_wise_line_number_mapping


def get_num_lines_with_more_than_num_words(file_wise_line_number_mapping, num_words):
    """
    Take a mapping containing the number of words
    per line for a set of files and count the number
    of lines for each file with number of words
    greater than the specified threshold.

    :param file_wise_line_number_mapping:
    :param num_words: Threshold for line word count
    :return:
    """

    lines_with_more_than_num_words = {}
    for file_name in file_wise_line_number_mapping:
        # Use list comprehension to select the line numbers
        # which with count of words higher than the specified
        # threshold, and then store the length of this list
        # to get the count of the number of lines
        lines_with_more_than_num_words[file_name] = len(
            [line_num for line_num in file_wise_line_number_mapping[file_name]
             if file_wise_line_number_mapping[file_name][line_num] > num_words]
        )

    return lines_with_more_than_num_words


def main():
    """
    Main function, solve assignment
    :return:
    """
    config = get_config("./config.json")

    """
    Task 1 - Download txt files from webpage
    """
    txt_file_links = get_txt_file_links(
        config["base_url"],
        config["num_files"]
    )
    download_txt_files(txt_file_links)

    """
    Task 2 - Get line number mapping
    """
    file_list, file_data = get_file_data()
    file_wise_line_number_mapping = get_line_number_mapping(file_list, file_data)

    """
    Task 3 - Get the number of lines with more than 10 words per file
    """
    lines_with_more_than_num_words = get_num_lines_with_more_than_num_words(
        file_wise_line_number_mapping,
        num_words=10
    )
    pprint(lines_with_more_than_num_words)


if __name__ == '__main__':
    main()
