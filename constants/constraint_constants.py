"""Constraints constants
"""
import enum


class UserConstraints(enum.Enum):
    user_name_len = 64
    user_display_name_len = 64


class TeamConstraints(enum.Enum):
    team_name_len = 64
    team_description_len = 128
    max_users_per_team = 50


class BoardAndTaskConstraints(enum.Enum):
    board_name_len = 64
    board_description_len = 128
    task_title_len = 64
    task_description_len = 128
