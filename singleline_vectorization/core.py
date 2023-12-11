# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_fileorg.ipynb.

# %% auto 0
__all__ = ['SAMPLE_SKETCHBOOKS_DIR', 'SAMPLE_CHECKPOINT', 'sketchbook_resnet34', 'batch_fnames_and_images', 'predict_embeddings',
           'Hook', 'embed_dir']

# %% ../nbs/00_fileorg.ipynb 3
import math

import pandas as pd
from fastai.vision.all import *

# %% ../nbs/00_fileorg.ipynb 4
SAMPLE_SKETCHBOOKS_DIR = "../data/sample"
SAMPLE_CHECKPOINT = "sample_epoch6"

# %% ../nbs/00_fileorg.ipynb 7
SAMPLE_SKETCHBOOKS_DIR = "../data/sample"
SAMPLE_CHECKPOINT = "sample_epoch6"

# %% ../nbs/00_fileorg.ipynb 14
def sketchbook_resnet34(sketchbooks_dir, load_checkpoint=None):
    dataloaders = sketchbook_dataloaders(sketchbooks_dir)
    learn = vision_learner(dls, resnet34, metrics=error_rate)
    if load_checkpoint:
        print(f"loading {load_checkpoint}")
        learn.load(load_checkpoint)
    return learn

# %% ../nbs/00_fileorg.ipynb 23
def batch_fnames_and_images(sketchbooks_dir):
    """
    Prepare data to compute embeddings over all images and store
    them along with a reference to the underlying filename.
    """
    ordered_dls = sketchbook_dataloaders(
        sketchbooks_dir, seed=42, shuffle=False, valid_pct=0.0
    )

    # compute the number of batches
    num_batches = math.ceil(len(ordered_dls.train.items) / DEFAULT_BATCH_SIZE)
    batched_fnames = [
        ordered_dls.train.items[i * 64 : (i + 1) * 64] for i in range(num_batches)
    ]
    print(
        f"total items: {len(ordered_dls.train.items)}, num batches: {len(batched_fnames)}"
    )
    return batched_fnames, ordered_dls

# %% ../nbs/00_fileorg.ipynb 25
def predict_embeddings(model, xb):
    with torch.no_grad():
        with Hook(model[-1][-2]) as hook:
            output = model.eval()(xb)
            act = hook.stored
    return act.cpu().numpy()


class Hook:
    def __init__(self, m):
        self.hook = m.register_forward_hook(self.hook_func)

    def hook_func(self, m, i, o):
        self.stored = o.detach().clone()

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        self.hook.remove()

# %% ../nbs/00_fileorg.ipynb 29
def embed_dir(input_dir, learner):
    batched_fnames, ordered_dls = batch_fnames_and_images(input_dir)
    with torch.no_grad():
        for i, batch in enumerate(zip(batched_fnames, ordered_dls.train)):
            if i > 0:
                break
            batched_fnames, (x, y) = batch
            bs = len(batched_fnames)
            assert bs == x.shape[0]
            assert bs == y.shape[0]

            # activations = predict_embeddings(learn.model, x)
            # assert bs == activations.shape[0]

            for j in range(bs):
                x_j = x[j]
                y_j = y[j]
                fname_j = batched_fnames[j]
                emb_j = activations[j]
                # label: what parent dir exists in the dataset we're processing
                label_j = ordered_dls.vocab[y_j]
                # pred_label: prediction made relative to the vocab of the learner's model
                # (may be different than what's in the dataloader we're using for input).
                pred_label_j, pred_idx_j, pred_probs_j = learn.predict(x_j.cpu())
                yield {
                    "idx": j + i * bs,
                    "fname": fname_j,
                    "label": label_j,
                    "pred_label": pred_label_j,
                    "pred_idx": pred_idx_j.cpu().numpy(),
                    "pred_probs": ",".join(
                        [f"{p:04f}" for p in pred_probs_j.cpu().numpy()]
                    ),
                    "emb_csv": ",".join([str(f) for f in list(emb_j)]),
                }
