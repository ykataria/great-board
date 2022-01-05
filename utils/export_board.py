from typing import Dict, Union
import os
from pathlib import Path
from datetime import datetime

from tabulate import tabulate

from logger import LOGGER

EXPORT_DIR_PATH = Path("out")


def export_project_board(
        board_task_details: Dict[str, Union[str, Dict[str, str]]]
) -> str:
    """ Util function to export the project board to a readable, indented txt file
    :param board_task_details: board model details
    :type board_task_details: Dict[str, Union[str, Dict[str, str]]]
    """
    board_details_str = f"Board: {board_task_details['board_name']}   Team: {board_task_details['team_name']}\n"
    board_details_str += f"About Board: {board_task_details['board_description']}\n"
    board_details_str += f"Board Status: {board_task_details['board_status']}\n\n"

    table_board_data = tabulate(
            board_task_details['task_details'],
            headers={
                'task_title': 'Task',
                'task_description': 'Detail',
                'user_display_name': 'Assigned to',
                'task_status': 'Status'
            },
            tablefmt="github"
        )
    board_details_str += table_board_data

    file_name = board_task_details['board_name'] + f"_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

    file_path = EXPORT_DIR_PATH / file_name
    with open(file_path, 'w') as file:
        file.write(board_details_str)
        LOGGER.info("Exported Board")

    return file_name
