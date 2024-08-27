# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Bùi Tiến Thành (@bu1th4nh)
# Title: LoggingHelper.py
# Date: 2024/02/28 15:02:48
# Description: File chứa các hàm hỗ trợ logging
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------


import sys
import logging
from datetime import datetime
from colorlog import ColoredFormatter


# -----------------------------------------------------------------------------------------------
# Filter/API
# -----------------------------------------------------------------------------------------------
class EndpointFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().find("/metrics") == -1
    



# -----------------------------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------------------------
def initialize_logging():
    # logging.root = logging.getLogger('uvicorn.default')
    logging.root.handlers = [];

    # Console handler
    handler_sh = logging.StreamHandler(sys.stdout)
    handler_sh.setFormatter(
        ColoredFormatter(
            "%(cyan)s%(asctime)s.%(msecs)03d %(log_color)s[%(levelname)s]%(reset)s %(light_white)s%(message)s%(reset)s %(blue)s(%(filename)s:%(lineno)d)",
            datefmt  = '%Y/%m/%d %H:%M:%S',
            log_colors={
                'DEBUG': 'gray',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    )

    handler_api_sh = logging.StreamHandler(sys.stdout)
    handler_api_sh.setFormatter(
        ColoredFormatter(
            "%(light_purple)s%(asctime)s.%(msecs)03d %(log_color)s[%(levelname)s]%(reset)s %(white)s[RESPONSE]%(reset)s %(light_purple)s%(message)s",
            datefmt  = '%Y/%m/%d %H:%M:%S',
            log_colors={
                'DEBUG': 'gray',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    )

    

    # File handler
    handler_file = logging.FileHandler(
        filename = "cls-nlp-log_latest.log",
        encoding = "utf-8-sig",    
        mode     = "w"
    )
    handler_file.setFormatter(
        logging.Formatter(
            fmt      = '%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)', 
            datefmt  = '%Y/%m/%d %H:%M:%S'
        )
    )

    # Set logging level and handlers
    logging.basicConfig(
        level    = logging.INFO,
        handlers = [handler_sh, handler_file]
    )

    # Remove existing handlers to avoid duplicate logs
    logger = logging.getLogger("uvicorn.access")
    logger.addFilter(EndpointFilter())
    logger.handlers = [handler_api_sh, handler_file]





