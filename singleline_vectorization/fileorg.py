# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_fileorg.ipynb.

# %% auto 0
__all__ = ['SAMPLE_SKETCHBOOKS_DIR', 'SAMPLE_CHECKPOINT', 'PRETRAINED_DIR', 'PRETRAINED_CHECKPOINT', 'flat_sketchbook_paths',
           'flatten_sketchbooks']

# %% ../nbs/00_fileorg.ipynb 6
import math
import os
import shutil
from pprint import pprint

import pandas as pd
from fastai.vision.all import *

# %% ../nbs/00_fileorg.ipynb 7
SAMPLE_SKETCHBOOKS_DIR = "../data/sample"
SAMPLE_CHECKPOINT = "sample_epoch6"

PRETRAINED_DIR = "../data/v1-full"
PRETRAINED_CHECKPOINT = "model_20231121_2epochs"

# %% ../nbs/00_fileorg.ipynb 11
def flat_sketchbook_paths(data_root, exclude_parents=["xtra", "priv"]):
    for p in get_image_files(data_root):
        # ex. '016.jpg'
        name = os.path.basename(p)
        # ex. 'art'
        parent_dir = os.path.dirname(p)
        parent_name = os.path.basename(parent_dir)
        if parent_name in exclude_parents:
            continue
        # ex. 'sb44'
        grandparent_dir = os.path.dirname(parent_dir)
        grandparent_name = os.path.basename(grandparent_dir)

        # should be same as data_root
        greatgrandparent_dir = os.path.dirname(grandparent_dir)
        assert data_root == str(greatgrandparent_dir)

        dest_fname = f"{parent_name}/{grandparent_name}p{name}"

        yield {
            "source_abs": p,
            "dest_fname": dest_fname,
            "parent_name": parent_name,
            "grandparent_name": grandparent_name,
        }

# %% ../nbs/00_fileorg.ipynb 12
def flatten_sketchbooks(source_root, dest_root):
    parent_counts = {}
    grandparent_counts = {}
    for f in flat_sketchbook_paths(source_root):
        source_abs = f["source_abs"]
        dest_abs = Path(dest_root) / f["dest_fname"]
        dest_dir = os.path.dirname(dest_abs)
        if not os.path.isdir(dest_dir):
            print(f"creating {dest_dir}")
            os.makedirs(dest_dir)
        if not os.path.exists(dest_abs):
            print(f"copying {source_abs} to {dest_abs}")
            shutil.copy(source_abs, dest_abs)

        parent_cnt = parent_counts.get(f["parent_name"], 0)
        parent_counts[f["parent_name"]] = parent_cnt + 1
        grandparent_cnt = grandparent_counts.get(f["grandparent_name"], 0)
        grandparent_counts[f["grandparent_name"]] = grandparent_cnt + 1
    return parent_counts, grandparent_counts
