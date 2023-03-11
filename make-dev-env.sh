#!/usr/bin/env bash
set -eo pipefail
source ~/miniconda3/etc/profile.d/conda.sh
mamba env create -f environment-dev.yml
conda activate egame-179
conda config --env --add channels conda-forge
python -m pip install --no-deps pyecharts streamlit-echarts streamlit-option-menu streamlit-server-state
python -m pip install --no-deps -e backend/
python -m pip install --no-deps -e frontend/
