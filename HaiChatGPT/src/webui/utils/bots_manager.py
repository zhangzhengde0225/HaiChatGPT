"""
用于管理bots
每个用户分配一个bot，
"""

import os, sys


class BotsManager(object):

    def __init__(self) -> None:
        # 定义三类bots
        self.bots = {}