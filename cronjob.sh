#!/bin/bash
FILE_PATH=$(readlink -f $0)
ROOT=$(dirname "$FILE_PATH")
source $ROOT/ENV/bin/activate
$ROOT/refresh_review_requests.py
