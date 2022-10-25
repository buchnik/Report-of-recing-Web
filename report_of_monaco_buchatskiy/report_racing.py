import sys
from datetime import datetime
from collections import namedtuple
import click
from click import command
from colorama import Fore, Back, Style
import os.path
import argparse

"""
    Pars log and txt files 
    Create list namedtuple with Drivers statistics
    Print tabular view    
    """

# відносний шлях до файлів
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'file_data')
# константи
ABBREVIATIONS_FILENAME = '/abbreviations.txt'
START_LOG = '/start.log'
END_LOG = '/end.log'
Driver = namedtuple('Driver', 'num, driver_id, name, team, lap_time')


def parse_log_file(file_name: str, files) -> dict:
    driver_time = {}
    if not files:
        file_name = DATA_DIR + file_name
    else:
        file_name = files + file_name
    try:
        with open(file_name, 'r', encoding='utf8') as file:
            for line in file:
                if len(line) > 1:
                    line = line.strip()
                    driver_id = line[0:3]
                    time = line[3:]
                    driver_time.update({driver_id: time})
    except IOError:
        print('path log_file is not found')
        sys.exit(1)
    return driver_time


def parse_txt_file(file_name: str, files) -> list:
    driver_data = []
    if not files:
        file_name = DATA_DIR + file_name
    else:
        file_name = files + file_name
    try:
        with open(file_name, 'r', encoding='utf8') as file:
            for line in file:
                if len(line) > 1:
                    driver_id, name, team = line.strip('\n').split('_')
                    driver_data.append(Driver(num=None, driver_id=driver_id, name=name, team=team, lap_time=None))
    except IOError:
        print('path txt_file is not found')
        sys.exit(1)
    return driver_data


def get_lap_time(start_time, end_time):
    start = datetime.strptime(start_time, "%Y-%m-%d_%H:%M:%S.%f")
    finish = datetime.strptime(end_time, "%Y-%m-%d_%H:%M:%S.%f")
    if end_time > start_time:
        lap_time = str(finish - start)
    else:
        lap_time = str(start - finish)
    return lap_time


def built_report(start_times: dict, end_times: dict, drivers_list: list, desc: bool) -> list:
    drivers = []
    sort_drivers = []
    for id_start, time_start in start_times.items():
        for id_end, time_end in end_times.items():
            lap_time = get_lap_time(start_time=time_start, end_time=time_end)
            for line in drivers_list:
                if id_start == id_end == line.driver_id:
                    drivers_lap_time = line._replace(lap_time=lap_time)
                    sort_drivers.append(drivers_lap_time)
    sort_drivers = sorted(sort_drivers, key=lambda x: x.lap_time, reverse=False)

    # дабавляєм нумерацію у неймтюплів
    num = 1
    for line in sort_drivers:
        driver_num = line._replace(num=str(num))
        num += 1
        drivers.append(driver_num)
    drivers = sorted(drivers, key=lambda x: x.lap_time, reverse=desc)
    return drivers


def print_report(drivers: list, desc: bool, driver_id: str):
    columns = ['№', 'ID', 'Racer', 'Team', 'Time']
    max_columns = []
    # розпаковуємо неймтюпли та визначаємо ширину колонок
    for col in zip(*drivers):
        len_el = []
        [len_el.append(len(el)) for el in col]
        max_columns.append(max(len_el))

    # печать роздільника
    sep = f'{"-" * sum(max_columns) + "-" * 18}'
    print(sep)

    # печать шапки таблиці
    for n, column in enumerate(columns):
        print(f'|{column:^{max_columns[n] + 2}}', end='')
    print()
    print(sep)

    # печать тіла таблиці
    if driver_id:
        driver = get_driver_by_id(drivers, driver_id)
        for col in zip(driver):
            len_el = []
            [len_el.append(len(el)) for el in col]
            max_columns.append(max(len_el))
        chart = ""
        for n, el in enumerate(driver):
            chart += f'| {el:{max_columns[n] + 1}}'
        print(f'{chart}')
    else:
        for i, el in enumerate(drivers):
            chart = ""
            for n, col in enumerate(el):
                if (col == '15' and desc) or (col == "16" and not desc):
                    print(sep)
                chart += f'| {col:{max_columns[n] + 1}}'
            print(f'{chart}')

    # if not driver:
    #     for i, el in enumerate(drivers):
    #         chart = ""
    #         for n, col in enumerate(el):
    #             if (col == '15' and desc) or (col == "16" and not desc):
    #                 print(sep)
    #             chart += f'| {col:{max_columns[n] + 1}}'
    #         print(f'{chart}')
    # else:
    #     driver = get_driver_by_id(drivers, driver)
    #     print(f'| {driver.num:2} | {driver.driver_id:3} | {driver.name:17} | {driver.team:25} | {driver.lap_time}')


def get_driver_by_id(drivers: list, driver_id: str):
    for line in drivers:
        if line.driver_id == driver_id:
            return line


# @command()
# @click.argument('files', type=click.Path(exists=True))
# @click.option("--desc", is_flag=True, show_default=True, default=False)
# @click.option('--driver', help='enter name driver "name"')
# def main(files, desc, driver):
#     drivers = built_report(files, desc, driver)
#     print_report(drivers, desc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report of Monaco')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('--files', required=False, type=str, help='Folder path')
    optional.add_argument('--desc', action='store_true', help='sort negative', required=False)
    optional.add_argument('--driver_id', type=str, help="enter driver names for statistics")
    args = parser.parse_args()

    start_times = parse_log_file(file_name=START_LOG, files=args.files)
    end_times = parse_log_file(file_name=END_LOG, files=args.files)
    drivers_list = parse_txt_file(file_name=ABBREVIATIONS_FILENAME, files=args.files)

    drivers = built_report(start_times, end_times, drivers_list, args.desc)
    print_report(drivers, args.desc, args.driver_id)
