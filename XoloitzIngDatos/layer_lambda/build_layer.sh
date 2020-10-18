#!/bin/bash
set -eo pipefail
rm -rf python
pip install --target ./python -r requirements.txt
#zip -r example.zip original_folder