#!/usr/bin/python
import cv2
import sys
from random import randint

import numpy as np
from sklearn.feature_extraction import image


texure = cv2.imread('textures/rice.png' if len(sys.argv) <= 2 else sys.argv[1])
source = cv2.imread('src.jpg' if len(sys.argv) <= 2 else sys.argv[2])
output = np.zeros(source.shape, np.uint8)
patch_sz = 10
init_threshold_const = 1


def print_progress(done_patches, total_patches, threshold=0):
    sys.stdout.write('\rPatcheCompleted: %d/%d | Threshold: %.1f'
                     % (done_patches, total_patches, threshold))
    sys.stdout.flush()


def extract_patches(img, patch_sz, overlap=None):
    # img = img.astype(np.int32)
    h, w, _ = img.shape
    overlap = overlap or patch_sz
    rh, rw = (h // overlap) * overlap, (w // overlap) * overlap
    patches = [
        # img[y:y + patch_sz, x:x + patch_sz]
        (y, x)
        for y in range(0, h - patch_sz, overlap)
        for x in range(0, w - patch_sz, overlap)
        if x < rw and y < rh
    ]
    return patches


def extract_texture_patches(tex, patch_sz):
    h, w, _ = tex.shape
    tex = tex.astype(np.int32)
    patches = image.extract_patches_2d(tex, (patch_sz, patch_sz))
    return patches[:h - patch_sz, :w - patch_sz]


def get_best_texture_patch(src_patch, tex_patches, threshold):
    diff = tex_patches - src_patch
    cost = np.sum(diff ** 2, axis=(1, 2, 3)) ** 0.5
    hard_example, = np.where(cost < threshold / 2)
    if hard_example.size:
        return hard_example
    soft_example, = np.where(cost < threshold)
    return soft_example


def ind2sub(n, width):
    return n // width, n % width


def fill_output(img_px, output, tex_px, texure):
    x, y = img_px
    tx, ty = tex_px
    tex = texure[tx:tx + patch_sz, ty:ty + patch_sz]
    try:
        output[x:x + patch_sz, y:y + patch_sz] = tex
    except:
        pass


def main():
    global source
    source = source.astype(np.int32)

    patches = extract_patches(source, patch_sz, 0)
    tex_patches = extract_texture_patches(texure, patch_sz)
    for num, patch in enumerate(patches):
        b, a = patch
        patch = source[b:b + patch_sz, a:a + patch_sz]

        threshold = init_threshold_const * (patch_sz ** 2)

        p_ids = np.array([])
        while not p_ids.size:
            p_ids = get_best_texture_patch(patch, tex_patches, threshold)
            threshold *= 1.05

        p_id = p_ids[randint(0, len(p_ids) - 1)]
        j, i = ind2sub(p_id, texure.shape[1] - patch_sz)
        y, x = ind2sub(num, source.shape[1] // patch_sz)
        fill_output((y * patch_sz, x * patch_sz), output, (j, i), texure)
        print_progress(num + 1, len(patches), threshold)

    cv2.imwrite('output.png', output)
    cv2.imshow('output', output)
    cv2.waitKey()

if __name__ == '__main__':
    main()
