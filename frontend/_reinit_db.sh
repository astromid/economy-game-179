#!/usr/bin/env bash
set -eo pipefail
source ~/miniconda3/etc/profile.d/conda.sh
conda activate egame-179
cd ../backend
alembic downgrade -1
alembic upgrade head
