#!/bin/bash

VENV_PATH=""
SCRAPY_PROJECT_ROOT_DIR=""

cd $SCRAPY_PROJECT_ROOT_DIR
source $VENV_PATH
scrapy crawl availability
python3 lego/evaluate_availability.py