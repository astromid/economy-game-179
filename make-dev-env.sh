#!/usr/bin/env bash
set -eo pipefail
source ~/miniconda3/etc/profile.d/conda.sh
mamba env create -f environment-dev.yml
conda activate egame-179
conda config --env --add channels conda-forge
python -m pip install --no-deps pyecharts streamlit-echarts compress-pickle
python -m pip install --no-deps extra-streamlit-components streamlit-option-menu
python -m pip install --no-deps -e backend/ frontend/
