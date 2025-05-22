#!/bin/bash
pip install -r requirements.txt
python -m flask db init || true
python -m flask db migrate || true
python -m flask db upgrade || true
