# code in this file is adpated from rpmcruz/autoaugment
# https://github.com/rpmcruz/autoaugment/blob/master/transformations.py
import random

import PIL, PIL.ImageOps, PIL.ImageEnhance, PIL.ImageDraw
import numpy as np
import torch
from lib.config import cfg
from collections import defaultdict

random_mirror = True


def ShearX(img, v):  # [-0.3, 0.3]
    assert -0.3 <= v <= 0.3
    if random_mirror and random.random() > 0.5:
        v = -v
    return img.transform(img.size, PIL.Image.AFFINE, (1, v, 0, 0, 1, 0))


def ShearY(img, v):  # [-0.3, 0.3]
    assert -0.3 <= v <= 0.3
    if random_mirror and random.random() > 0.5:
        v = -v
    return img.transform(img.size, PIL.Image.AFFINE, (1, 0, 0, v, 1, 0))


def TranslateX(img, v):  # [-150, 150] => percentage: [-0.45, 0.45]
    assert -0.45 <= v <= 0.45
    if random_mirror and random.random() > 0.5:
        v = -v
    v = v * img.size[0]
    return img.transform(img.size, PIL.Image.AFFINE, (1, 0, v, 0, 1, 0))


def TranslateY(img, v):  # [-150, 150] => percentage: [-0.45, 0.45]
    assert -0.45 <= v <= 0.45
    if random_mirror and random.random() > 0.5:
        v = -v
    v = v * img.size[1]
    return img.transform(img.size, PIL.Image.AFFINE, (1, 0, 0, 0, 1, v))


def TranslateXAbs(img, v):  # [-150, 150] => percentage: [-0.45, 0.45]
    assert 0 <= v <= 10
    if random.random() > 0.5:
        v = -v
    return img.transform(img.size, PIL.Image.AFFINE, (1, 0, v, 0, 1, 0))


def TranslateYAbs(img, v):  # [-150, 150] => percentage: [-0.45, 0.45]
    assert 0 <= v <= 10
    if random.random() > 0.5:
        v = -v
    return img.transform(img.size, PIL.Image.AFFINE, (1, 0, 0, 0, 1, v))


def Rotate(img, v):  # [-30, 30]
    assert -30 <= v <= 30
    if random_mirror and random.random() > 0.5:
        v = -v
    return img.rotate(v)


def AutoContrast(img, _):
    return PIL.ImageOps.autocontrast(img)


def Invert(img, _):
    return PIL.ImageOps.invert(img)


def Equalize(img, _):
    return PIL.ImageOps.equalize(img)


def Flip(img, _):  # not from the paper
    return PIL.ImageOps.mirror(img)


def Solarize(img, v):  # [0, 256]
    assert 0 <= v <= 256
    return PIL.ImageOps.solarize(img, v)


def Posterize(img, v):  # [4, 8]
    assert 4 <= v <= 8
    v = int(v)
    return PIL.ImageOps.posterize(img, v)


def Posterize2(img, v):  # [0, 4]
    assert 0 <= v <= 4
    v = int(v)
    return PIL.ImageOps.posterize(img, v)


def Contrast(img, v):  # [0.1,1.9]
    assert 0.1 <= v <= 1.9
    return PIL.ImageEnhance.Contrast(img).enhance(v)


def Color(img, v):  # [0.1,1.9]
    assert 0.1 <= v <= 1.9
    return PIL.ImageEnhance.Color(img).enhance(v)


def Brightness(img, v):  # [0.1,1.9]
    assert 0.1 <= v <= 1.9
    return PIL.ImageEnhance.Brightness(img).enhance(v)


def Sharpness(img, v):  # [0.1,1.9]
    assert 0.1 <= v <= 1.9
    return PIL.ImageEnhance.Sharpness(img).enhance(v)


def Cutout(img, v):  # [0, 60] => percentage: [0, 0.2]
    assert 0.0 <= v <= 0.2
    if v <= 0.:
        return img

    v = v * img.size[0]

    return CutoutAbs(img, v)

    # x0 = np.random.uniform(w - v)
    # y0 = np.random.uniform(h - v)
    # xy = (x0, y0, x0 + v, y0 + v)
    # color = (127, 127, 127)
    # img = img.copy()
    # PIL.ImageDraw.Draw(img).rectangle(xy, color)
    # return img


def CutoutAbs(img, v):  # [0, 60] => percentage: [0, 0.2]
    # assert 0 <= v <= 20
    if v < 0:
        return img
    w, h = img.size
    x0 = np.random.uniform(w)
    y0 = np.random.uniform(h)

    x0 = int(max(0, x0 - v / 2.))
    y0 = int(max(0, y0 - v / 2.))
    x1 = min(w, x0 + v)
    y1 = min(h, y0 + v)

    xy = (x0, y0, x1, y1)
    color = (125, 123, 114)
    # color = (0, 0, 0)
    img = img.copy()
    PIL.ImageDraw.Draw(img).rectangle(xy, color)
    return img


def SamplePairing(imgs):  # [0, 0.4]
    def f(img1, v):
        i = np.random.choice(len(imgs))
        img2 = PIL.Image.fromarray(imgs[i])
        return PIL.Image.blend(img1, img2, v)

    return f


def augment_list(for_autoaug=True):  # 16 operations and their ranges
    l = [
        (ShearX, -0.3, 0.3),  # 0
        (ShearY, -0.3, 0.3),  # 1
        (TranslateX, -0.45, 0.45),  # 2
        (TranslateY, -0.45, 0.45),  # 3
        (Rotate, -30, 30),  # 4
        (AutoContrast, 0, 1),  # 5
        (Invert, 0, 1),  # 6
        (Equalize, 0, 1),  # 7
        (Solarize, 0, 256),  # 8
        (Posterize, 4, 8),  # 9
        (Contrast, 0.1, 1.9),  # 10
        (Color, 0.1, 1.9),  # 11
        (Brightness, 0.1, 1.9),  # 12
        (Sharpness, 0.1, 1.9),  # 13
        (Cutout, 0, 0.2),  # 14
        # (SamplePairing(imgs), 0, 0.4),  # 15
    ]
    if for_autoaug:
        l += [
            (CutoutAbs, 0, 20),  # compatible with auto-augment
            (Posterize2, 0, 4),  # 9
            (TranslateXAbs, 0, 10),  # 9
            (TranslateYAbs, 0, 10),  # 9
        ]
    return l


augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augment_list()}


def get_augment(name):
    return augment_dict[name]


def apply_augment(img, name, level):
    augment_fn, low, high = get_augment(name)
    return augment_fn(img.copy(), level * (high - low) + low)


def arsaug_policy():
    exp0_0 = [
        [('Solarize', 0.66, 0.34), ('Equalize', 0.56, 0.61)],
        [('Equalize', 0.43, 0.06), ('AutoContrast', 0.66, 0.08)],
        [('Color', 0.72, 0.47), ('Contrast', 0.88, 0.86)],
        [('Brightness', 0.84, 0.71), ('Color', 0.31, 0.74)],
        [('Rotate', 0.68, 0.26), ('TranslateX', 0.38, 0.88)]]
    exp0_1 = [
        [('TranslateY', 0.88, 0.96), ('TranslateY', 0.53, 0.79)],
        [('AutoContrast', 0.44, 0.36), ('Solarize', 0.22, 0.48)],
        [('AutoContrast', 0.93, 0.32), ('Solarize', 0.85, 0.26)],
        [('Solarize', 0.55, 0.38), ('Equalize', 0.43, 0.48)],
        [('TranslateY', 0.72, 0.93), ('AutoContrast', 0.83, 0.95)]]
    exp0_2 = [
        [('Solarize', 0.43, 0.58), ('AutoContrast', 0.82, 0.26)],
        [('TranslateY', 0.71, 0.79), ('AutoContrast', 0.81, 0.94)],
        [('AutoContrast', 0.92, 0.18), ('TranslateY', 0.77, 0.85)],
        [('Equalize', 0.71, 0.69), ('Color', 0.23, 0.33)],
        [('Sharpness', 0.36, 0.98), ('Brightness', 0.72, 0.78)]]
    exp0_3 = [
        [('Equalize', 0.74, 0.49), ('TranslateY', 0.86, 0.91)],
        [('TranslateY', 0.82, 0.91), ('TranslateY', 0.96, 0.79)],
        [('AutoContrast', 0.53, 0.37), ('Solarize', 0.39, 0.47)],
        [('TranslateY', 0.22, 0.78), ('Color', 0.91, 0.65)],
        [('Brightness', 0.82, 0.46), ('Color', 0.23, 0.91)]]
    exp0_4 = [
        [('Cutout', 0.27, 0.45), ('Equalize', 0.37, 0.21)],
        [('Color', 0.43, 0.23), ('Brightness', 0.65, 0.71)],
        [('ShearX', 0.49, 0.31), ('AutoContrast', 0.92, 0.28)],
        [('Equalize', 0.62, 0.59), ('Equalize', 0.38, 0.91)],
        [('Solarize', 0.57, 0.31), ('Equalize', 0.61, 0.51)]]

    exp0_5 = [
        [('TranslateY', 0.29, 0.35), ('Sharpness', 0.31, 0.64)],
        [('Color', 0.73, 0.77), ('TranslateX', 0.65, 0.76)],
        [('ShearY', 0.29, 0.74), ('Posterize', 0.42, 0.58)],
        [('Color', 0.92, 0.79), ('Equalize', 0.68, 0.54)],
        [('Sharpness', 0.87, 0.91), ('Sharpness', 0.93, 0.41)]]
    exp0_6 = [
        [('Solarize', 0.39, 0.35), ('Color', 0.31, 0.44)],
        [('Color', 0.33, 0.77), ('Color', 0.25, 0.46)],
        [('ShearY', 0.29, 0.74), ('Posterize', 0.42, 0.58)],
        [('AutoContrast', 0.32, 0.79), ('Cutout', 0.68, 0.34)],
        [('AutoContrast', 0.67, 0.91), ('AutoContrast', 0.73, 0.83)]]

    return exp0_0 + exp0_1 + exp0_2 + exp0_3 + exp0_4 + exp0_5 + exp0_6


def autoaug2arsaug(f):
    def autoaug():
        mapper = defaultdict(lambda: lambda x: x)
        mapper.update({
            'ShearX': lambda x: float_parameter(x, 0.3),
            'ShearY': lambda x: float_parameter(x, 0.3),
            'TranslateX': lambda x: int_parameter(x, 10),
            'TranslateY': lambda x: int_parameter(x, 10),
            'Rotate': lambda x: int_parameter(x, 30),
            'Solarize': lambda x: 256 - int_parameter(x, 256),
            'Posterize2': lambda x: 4 - int_parameter(x, 4),
            'Contrast': lambda x: float_parameter(x, 1.8) + .1,
            'Color': lambda x: float_parameter(x, 1.8) + .1,
            'Brightness': lambda x: float_parameter(x, 1.8) + .1,
            'Sharpness': lambda x: float_parameter(x, 1.8) + .1,
            'CutoutAbs': lambda x: int_parameter(x, 20)
        })

        def low_high(name, prev_value):
            _, low, high = get_augment(name)
            return float(prev_value - low) / (high - low)

        policies = f()
        new_policies = []
        for policy in policies:
            new_policies.append([(name, pr, low_high(name, mapper[name](level))) for name, pr, level in policy])
        return new_policies

    return autoaug


@autoaug2arsaug
def autoaug_paper_cifar10():
    return [
        [('Invert', 0.1, 7), ('Contrast', 0.2, 6)],
        [('Rotate', 0.7, 2), ('TranslateXAbs', 0.3, 9)],
        [('Sharpness', 0.8, 1), ('Sharpness', 0.9, 3)],
        [('ShearY', 0.5, 8), ('TranslateYAbs', 0.7, 9)],
        [('AutoContrast', 0.5, 8), ('Equalize', 0.9, 2)],
        [('ShearY', 0.2, 7), ('Posterize2', 0.3, 7)],
        [('Color', 0.4, 3), ('Brightness', 0.6, 7)],
        [('Sharpness', 0.3, 9), ('Brightness', 0.7, 9)],
        [('Equalize', 0.6, 5), ('Equalize', 0.5, 1)],
        [('Contrast', 0.6, 7), ('Sharpness', 0.6, 5)],
        [('Color', 0.7, 7), ('TranslateXAbs', 0.5, 8)],
        [('Equalize', 0.3, 7), ('AutoContrast', 0.4, 8)],
        [('TranslateYAbs', 0.4, 3), ('Sharpness', 0.2, 6)],
        [('Brightness', 0.9, 6), ('Color', 0.2, 6)],
        [('Solarize', 0.5, 2), ('Invert', 0.0, 3)],
        [('Equalize', 0.2, 0), ('AutoContrast', 0.6, 0)],
        [('Equalize', 0.2, 8), ('Equalize', 0.6, 4)],
        [('Color', 0.9, 9), ('Equalize', 0.6, 6)],
        [('AutoContrast', 0.8, 4), ('Solarize', 0.2, 8)],
        [('Brightness', 0.1, 3), ('Color', 0.7, 0)],
        [('Solarize', 0.4, 5), ('AutoContrast', 0.9, 3)],
        [('TranslateYAbs', 0.9, 9), ('TranslateYAbs', 0.7, 9)],
        [('AutoContrast', 0.9, 2), ('Solarize', 0.8, 3)],
        [('Equalize', 0.8, 8), ('Invert', 0.1, 3)],
        [('TranslateYAbs', 0.7, 9), ('AutoContrast', 0.9, 1)],
    ]


@autoaug2arsaug
def autoaug_policy():
    """AutoAugment policies found on Cifar."""
    exp0_0 = [
        [('Invert', 0.1, 7), ('Contrast', 0.2, 6)],
        [('Rotate', 0.7, 2), ('TranslateXAbs', 0.3, 9)],
        [('Sharpness', 0.8, 1), ('Sharpness', 0.9, 3)],
        [('ShearY', 0.5, 8), ('TranslateYAbs', 0.7, 9)],
        [('AutoContrast', 0.5, 8), ('Equalize', 0.9, 2)]]
    exp0_1 = [
        [('Solarize', 0.4, 5), ('AutoContrast', 0.9, 3)],
        [('TranslateYAbs', 0.9, 9), ('TranslateYAbs', 0.7, 9)],
        [('AutoContrast', 0.9, 2), ('Solarize', 0.8, 3)],
        [('Equalize', 0.8, 8), ('Invert', 0.1, 3)],
        [('TranslateYAbs', 0.7, 9), ('AutoContrast', 0.9, 1)]]
    exp0_2 = [
        [('Solarize', 0.4, 5), ('AutoContrast', 0.0, 2)],
        [('TranslateYAbs', 0.7, 9), ('TranslateYAbs', 0.7, 9)],
        [('AutoContrast', 0.9, 0), ('Solarize', 0.4, 3)],
        [('Equalize', 0.7, 5), ('Invert', 0.1, 3)],
        [('TranslateYAbs', 0.7, 9), ('TranslateYAbs', 0.7, 9)]]
    exp0_3 = [
        [('Solarize', 0.4, 5), ('AutoContrast', 0.9, 1)],
        [('TranslateYAbs', 0.8, 9), ('TranslateYAbs', 0.9, 9)],
        [('AutoContrast', 0.8, 0), ('TranslateYAbs', 0.7, 9)],
        [('TranslateYAbs', 0.2, 7), ('Color', 0.9, 6)],
        [('Equalize', 0.7, 6), ('Color', 0.4, 9)]]
    exp1_0 = [
        [('ShearY', 0.2, 7), ('Posterize2', 0.3, 7)],
        [('Color', 0.4, 3), ('Brightness', 0.6, 7)],
        [('Sharpness', 0.3, 9), ('Brightness', 0.7, 9)],
        [('Equalize', 0.6, 5), ('Equalize', 0.5, 1)],
        [('Contrast', 0.6, 7), ('Sharpness', 0.6, 5)]]
    exp1_1 = [
        [('Brightness', 0.3, 7), ('AutoContrast', 0.5, 8)],
        [('AutoContrast', 0.9, 4), ('AutoContrast', 0.5, 6)],
        [('Solarize', 0.3, 5), ('Equalize', 0.6, 5)],
        [('TranslateYAbs', 0.2, 4), ('Sharpness', 0.3, 3)],
        [('Brightness', 0.0, 8), ('Color', 0.8, 8)]]
    exp1_2 = [
        [('Solarize', 0.2, 6), ('Color', 0.8, 6)],
        [('Solarize', 0.2, 6), ('AutoContrast', 0.8, 1)],
        [('Solarize', 0.4, 1), ('Equalize', 0.6, 5)],
        [('Brightness', 0.0, 0), ('Solarize', 0.5, 2)],
        [('AutoContrast', 0.9, 5), ('Brightness', 0.5, 3)]]
    exp1_3 = [
        [('Contrast', 0.7, 5), ('Brightness', 0.0, 2)],
        [('Solarize', 0.2, 8), ('Solarize', 0.1, 5)],
        [('Contrast', 0.5, 1), ('TranslateYAbs', 0.2, 9)],
        [('AutoContrast', 0.6, 5), ('TranslateYAbs', 0.0, 9)],
        [('AutoContrast', 0.9, 4), ('Equalize', 0.8, 4)]]
    exp1_4 = [
        [('Brightness', 0.0, 7), ('Equalize', 0.4, 7)],
        [('Solarize', 0.2, 5), ('Equalize', 0.7, 5)],
        [('Equalize', 0.6, 8), ('Color', 0.6, 2)],
        [('Color', 0.3, 7), ('Color', 0.2, 4)],
        [('AutoContrast', 0.5, 2), ('Solarize', 0.7, 2)]]
    exp1_5 = [
        [('AutoContrast', 0.2, 0), ('Equalize', 0.1, 0)],
        [('ShearY', 0.6, 5), ('Equalize', 0.6, 5)],
        [('Brightness', 0.9, 3), ('AutoContrast', 0.4, 1)],
        [('Equalize', 0.8, 8), ('Equalize', 0.7, 7)],
        [('Equalize', 0.7, 7), ('Solarize', 0.5, 0)]]
    exp1_6 = [
        [('Equalize', 0.8, 4), ('TranslateYAbs', 0.8, 9)],
        [('TranslateYAbs', 0.8, 9), ('TranslateYAbs', 0.6, 9)],
        [('TranslateYAbs', 0.9, 0), ('TranslateYAbs', 0.5, 9)],
        [('AutoContrast', 0.5, 3), ('Solarize', 0.3, 4)],
        [('Solarize', 0.5, 3), ('Equalize', 0.4, 4)]]
    exp2_0 = [
        [('Color', 0.7, 7), ('TranslateXAbs', 0.5, 8)],
        [('Equalize', 0.3, 7), ('AutoContrast', 0.4, 8)],
        [('TranslateYAbs', 0.4, 3), ('Sharpness', 0.2, 6)],
        [('Brightness', 0.9, 6), ('Color', 0.2, 8)],
        [('Solarize', 0.5, 2), ('Invert', 0.0, 3)]]
    exp2_1 = [
        [('AutoContrast', 0.1, 5), ('Brightness', 0.0, 0)],
        [('CutoutAbs', 0.2, 4), ('Equalize', 0.1, 1)],
        [('Equalize', 0.7, 7), ('AutoContrast', 0.6, 4)],
        [('Color', 0.1, 8), ('ShearY', 0.2, 3)],
        [('ShearY', 0.4, 2), ('Rotate', 0.7, 0)]]
    exp2_2 = [
        [('ShearY', 0.1, 3), ('AutoContrast', 0.9, 5)],
        [('TranslateYAbs', 0.3, 6), ('CutoutAbs', 0.3, 3)],
        [('Equalize', 0.5, 0), ('Solarize', 0.6, 6)],
        [('AutoContrast', 0.3, 5), ('Rotate', 0.2, 7)],
        [('Equalize', 0.8, 2), ('Invert', 0.4, 0)]]
    exp2_3 = [
        [('Equalize', 0.9, 5), ('Color', 0.7, 0)],
        [('Equalize', 0.1, 1), ('ShearY', 0.1, 3)],
        [('AutoContrast', 0.7, 3), ('Equalize', 0.7, 0)],
        [('Brightness', 0.5, 1), ('Contrast', 0.1, 7)],
        [('Contrast', 0.1, 4), ('Solarize', 0.6, 5)]]
    exp2_4 = [
        [('Solarize', 0.2, 3), ('ShearX', 0.0, 0)],
        [('TranslateXAbs', 0.3, 0), ('TranslateXAbs', 0.6, 0)],
        [('Equalize', 0.5, 9), ('TranslateYAbs', 0.6, 7)],
        [('ShearX', 0.1, 0), ('Sharpness', 0.5, 1)],
        [('Equalize', 0.8, 6), ('Invert', 0.3, 6)]]
    exp2_5 = [
        [('AutoContrast', 0.3, 9), ('CutoutAbs', 0.5, 3)],
        [('ShearX', 0.4, 4), ('AutoContrast', 0.9, 2)],
        [('ShearX', 0.0, 3), ('Posterize2', 0.0, 3)],
        [('Solarize', 0.4, 3), ('Color', 0.2, 4)],
        [('Equalize', 0.1, 4), ('Equalize', 0.7, 6)]]
    exp2_6 = [
        [('Equalize', 0.3, 8), ('AutoContrast', 0.4, 3)],
        [('Solarize', 0.6, 4), ('AutoContrast', 0.7, 6)],
        [('AutoContrast', 0.2, 9), ('Brightness', 0.4, 8)],
        [('Equalize', 0.1, 0), ('Equalize', 0.0, 6)],
        [('Equalize', 0.8, 4), ('Equalize', 0.0, 4)]]
    exp2_7 = [
        [('Equalize', 0.5, 5), ('AutoContrast', 0.1, 2)],
        [('Solarize', 0.5, 5), ('AutoContrast', 0.9, 5)],
        [('AutoContrast', 0.6, 1), ('AutoContrast', 0.7, 8)],
        [('Equalize', 0.2, 0), ('AutoContrast', 0.1, 2)],
        [('Equalize', 0.6, 9), ('Equalize', 0.4, 4)]]
    exp0s = exp0_0 + exp0_1 + exp0_2 + exp0_3
    exp1s = exp1_0 + exp1_1 + exp1_2 + exp1_3 + exp1_4 + exp1_5 + exp1_6
    exp2s = exp2_0 + exp2_1 + exp2_2 + exp2_3 + exp2_4 + exp2_5 + exp2_6 + exp2_7

    return exp0s + exp1s + exp2s


PARAMETER_MAX = 10


def float_parameter(level, maxval):
    return float(level) * maxval / PARAMETER_MAX


def int_parameter(level, maxval):
    return int(float_parameter(level, maxval))


def random_search2048():
    # cifar10
    _policies_fold0 = [
        [[('Posterize', 0.709699990271369, 0.8236653036749833), ('Solarize', 0.9995791432489501, 0.895546498237044)],
         [('Cutout', 0.6831149863635602, 0.562498840188238), ('ShearX', 0.9189826133108392, 0.5251302162680564)],
         [('Contrast', 0.13358405061055256, 0.1952646403453232),
          ('Brightness', 0.7280409250762175, 0.4074824007813337)],
         [('Brightness', 0.5167734333379864, 0.2364143388929607), ('Cutout', 0.7707249841521517, 0.27251655306096945)],
         [('ShearX', 0.6033636441534456, 0.40143350276942125), ('Cutout', 0.601776421964206, 0.8309211575386521)]],
        [[('ShearY', 0.2647454506260575, 0.39702273362864104), ('TranslateY', 0.2832491627826961, 0.23292367395544888)],
         [('Sharpness', 0.0009080100005474101, 0.36415669560358954),
          ('Cutout', 0.5908461871814106, 0.25970426506860234)], [('Solarize', 0.18357214497294627, 0.9756079221974562),
                                                                 ('Posterize', 0.39949622410962027,
                                                                  0.29477386092906754)],
         [('Brightness', 0.09429743375613386, 0.006386029532104098),
          ('AutoContrast', 0.9029329780551074, 0.618245983109469)],
         [('Brightness', 0.6805221664236891, 0.14520952319300118),
          ('AutoContrast', 0.9726893023125383, 0.8956889479129884)]], [
            [('AutoContrast', 0.5022944258939801, 0.7180484543995698),
             ('Sharpness', 0.5417189214004129, 0.6361117441801069)],
            [('Cutout', 0.4310015550851225, 0.6626254773281117),
             ('Sharpness', 0.9051744898059433, 0.29013044022529455)],
            [('Sharpness', 0.23402478143880234, 0.5771375764954312),
             ('TranslateX', 0.3042605080584019, 0.4831394209317993)],
            [('ShearY', 0.28294098744633145, 0.5117257776292635),
             ('TranslateX', 0.16098037819237088, 0.6787257524773109)],
            [('Invert', 0.2187145852935698, 0.45481197738805845),
             ('Sharpness', 0.6580451977055289, 0.4023285952188146)]], [
            [('Posterize', 0.016342472316007384, 0.8607494005505818),
             ('AutoContrast', 0.7262739271274912, 0.0313002073497044)],
            [('Rotate', 0.07179022433199145, 0.6118701886796194), ('Color', 0.36659463377601975, 0.5448457981737703)],
            [('Posterize', 0.8316355405301347, 0.8449372118629678),
             ('Equalize', 0.02532547691330711, 0.1864844447252464)],
            [('Brightness', 0.08459948578983079, 0.052197715510527876),
             ('Equalize', 0.22617068524447648, 0.13061858369152912)],
            [('TranslateX', 0.8845725642217469, 0.6060215475838564),
             ('Solarize', 0.6899395986026327, 0.9692836090269836)]],
        [[('Sharpness', 0.9392281799852268, 0.7363348197908195), ('ShearY', 0.9899980308449515, 0.5227266699999886)],
         [('Posterize', 0.5076864303680726, 0.6761552254345644),
          ('TranslateY', 0.1596282316962928, 0.45467456718727106)],
         [('AutoContrast', 0.06899059090029402, 0.9678821740286254),
          ('AutoContrast', 0.5649082625234694, 0.6699361749500335)],
         [('ShearY', 0.0026245862487058735, 0.34545210208272603), ('Solarize', 0.8649286616916771, 0.8331734284874224)],
         [('ShearX', 0.02935027589411332, 0.9061125355357449), ('ShearX', 0.9067387733443698, 0.44516017207290404)]], [
            [('AutoContrast', 0.8017337335962192, 0.9931376078313714),
             ('Sharpness', 0.8614521251468067, 0.40784078790560363)],
            [('ShearY', 0.36866522085599174, 0.6415594472314682),
             ('Contrast', 0.08403639928109341, 0.9873127512172337)],
            [('Posterize', 0.4511955515709096, 0.7760375562138506),
             ('Posterize', 0.5066707147413717, 0.9225458277522391)],
            [('ShearX', 0.049950630596731216, 0.04157438011541159),
             ('TranslateY', 0.31864874477508687, 0.3411553351449256)],
            [('Contrast', 0.2307344693281126, 0.19383778309110777),
             ('Posterize', 0.7381909885148881, 0.8539276575975397)]], [
            [('TranslateY', 0.041794855549646126, 0.061428527942731126),
             ('Contrast', 0.8835131198805206, 0.6685467353070597)],
            [('Contrast', 0.04328481505505355, 0.04680807461092151),
             ('ShearX', 0.1362639998937787, 0.8901316270067592)],
            [('Brightness', 0.2476840359359921, 0.8572652665880937),
             ('AutoContrast', 0.6168863361077966, 0.412254955873945)],
            [('Color', 0.4185896280190774, 0.42581238727902926), ('Contrast', 0.676262138453488, 0.7286342378517439)],
            [('Sharpness', 0.07216253437820874, 0.4613083644362227),
             ('Posterize', 0.4357885702427907, 0.9647785625837578)]],
        [[('Color', 0.01786544266736767, 0.8928746945998216), ('Cutout', 0.5660736721008677, 0.002932078269684002)],
         [('Cutout', 0.9630847176870009, 0.20265802383570886), ('Rotate', 0.2806402950159874, 0.6976007178496048)],
         [('Sharpness', 0.651517303061078, 0.3034128051173922),
          ('AutoContrast', 0.8663667218653449, 0.9130351990575076)],
         [('Color', 0.4606739405468513, 0.712098372097414), ('AutoContrast', 0.7545177887601211, 0.6772226511796795)],
         [('ShearX', 0.2723880941865423, 0.7159971457667523), ('Contrast', 0.7996069939066458, 0.5178068595671571)]], [
            [('ShearX', 0.48583524508687137, 0.5824976712930959),
             ('TranslateY', 0.02240777363245261, 0.10001974537648883)],
            [('ShearX', 0.0533228175392777, 0.21303644191130733), ('ShearY', 0.71530338945374, 0.666026284260341)],
            [('Color', 0.20515761367736907, 0.904730172154942), ('ShearY', 0.19746474181370355, 0.31356086216669854)],
            [('ShearY', 0.21369214393927238, 0.24388686415873662), ('Cutout', 0.2369975830257155, 0.7007460791592609)],
            [('Equalize', 0.33276656113451064, 0.8256611755516485),
             ('Brightness', 0.1752554813246029, 0.41695603652164037)]],
        [[('ShearY', 0.16323689094509009, 0.8788167960053922), ('Cutout', 0.09298752419796497, 0.7809046279153092)],
         [('Posterize', 0.08031582077110178, 0.22385514283051144), ('Invert', 0.351272341605097, 0.6574507003533777)],
         [('Brightness', 0.00027528124162234935, 0.3296584353947595),
          ('Cutout', 0.7987019500020938, 0.6009588044991686)],
         [('AutoContrast', 0.6219271777794793, 0.8207128657190691), ('Color', 0.8716639494976303, 0.2259065727420193)],
         [('Invert', 0.27540185595836997, 0.7485135331456082), ('Cutout', 0.5029120629187204, 0.761906897331416)]]]
    policies_fold0 = []
    for p in _policies_fold0:
        policies_fold0.extend(p)

    policies = policies_fold0
    return policies


def no_duplicates(f):
    def wrap_remove_duplicates():
        policies = f()
        return remove_duplicates(policies)

    return wrap_remove_duplicates


def remove_duplicates(policies):
    s = set()
    new_policies = []
    for ops in policies:
        key = []
        for op in ops:
            key.append(op[0])
        key = '_'.join(key)
        if key in s:
            continue
        else:
            s.add(key)
            new_policies.append(ops)

    return new_policies


def fa_reduced_cifar10():
    p = [
        [["Contrast", 0.8320659688593578, 0.49884310562180767], ["TranslateX", 0.41849883971249136, 0.394023086494538]],
        [["Color", 0.3500483749890918, 0.43355143929883955], ["Color", 0.5120716140300229, 0.7508299643325016]],
        [["Rotate", 0.9447932604389472, 0.29723465088990375], ["Sharpness", 0.1564936149799504, 0.47169309978091745]],
        [["Rotate", 0.5430015349185097, 0.6518626678905443], ["Color", 0.5694844928020679, 0.3494533005430269]],
        [["AutoContrast", 0.5558922032451064, 0.783136004977799],
         ["TranslateY", 0.683914191471972, 0.7597025305860181]],
        [["TranslateX", 0.03489224481658926, 0.021025488042663354],
         ["Equalize", 0.4788637403857401, 0.3535481281496117]], [["Sharpness", 0.6428916269794158, 0.22791511918580576],
                                                                 ["Contrast", 0.016014045073950323,
                                                                  0.26811312269487575]],
        [["Rotate", 0.2972727228410451, 0.7654251516829896], ["AutoContrast", 0.16005809254943348, 0.5380523650108116]],
        [["Contrast", 0.5823671057717301, 0.7521166301398389], ["TranslateY", 0.9949449214751978, 0.9612671341689751]],
        [["Equalize", 0.8372126687702321, 0.6944127225621206], ["Rotate", 0.25393282929784755, 0.3261658365286546]],
        [["Invert", 0.8222011603194572, 0.6597915864008403], ["Posterize", 0.31858707654447327, 0.9541013715579584]],
        [["Sharpness", 0.41314621282107045, 0.9437344470879956], ["Cutout", 0.6610495837889337, 0.674411664255093]],
        [["Contrast", 0.780121736705407, 0.40826152397463156], ["Color", 0.344019192125256, 0.1942922781355767]],
        [["Rotate", 0.17153139555621344, 0.798745732456474], ["Invert", 0.6010555860501262, 0.320742172554767]],
        [["Invert", 0.26816063450777416, 0.27152062163148327], ["Equalize", 0.6786829200236982, 0.7469412443514213]],
        [["Contrast", 0.3920564414367518, 0.7493644582838497], ["TranslateY", 0.8941657805606704, 0.6580846856375955]],
        [["Equalize", 0.875509207399372, 0.9061130537645283], ["Cutout", 0.4940280679087308, 0.7896229623628276]],
        [["Contrast", 0.3331423298065147, 0.7170041362529597], ["ShearX", 0.7425484291842793, 0.5285117152426109]],
        [["Equalize", 0.97344237365026, 0.4745759720473106], ["TranslateY", 0.055863458430295276, 0.9625142022954672]],
        [["TranslateX", 0.6810614083109192, 0.7509937355495521],
         ["TranslateY", 0.3866463019475701, 0.5185481505576112]],
        [["Sharpness", 0.4751529944753671, 0.550464012488733], ["Cutout", 0.9472914750534814, 0.5584925992985023]],
        [["Contrast", 0.054606784909375095, 0.17257080196712182], ["Cutout", 0.6077026782754803, 0.7996504165944938]],
        [["ShearX", 0.328798428243695, 0.2769563264079157], ["Cutout", 0.9037632437023772, 0.4915809476763595]],
        [["Cutout", 0.6891202672363478, 0.9951490996172914], ["Posterize", 0.06532762462628705, 0.4005246609075227]],
        [["TranslateY", 0.6908583592523334, 0.725612120376128], ["Rotate", 0.39907735501746666, 0.36505798032223147]],
        [["TranslateX", 0.10398364107399072, 0.5913918470536627], ["Rotate", 0.7169811539340365, 0.8283850670648724]],
        [["ShearY", 0.9526373530768361, 0.4482347365639251], ["Contrast", 0.4203947336351471, 0.41526799558953864]],
        [["Contrast", 0.24894431199700073, 0.09578870500994707], ["Solarize", 0.2273713345927395, 0.6214942914963707]],
        [["TranslateX", 0.06331228870032912, 0.8961907489444944], ["Cutout", 0.5110007859958743, 0.23704875994050723]],
        [["Cutout", 0.3769183548846172, 0.6560944580253987], ["TranslateY", 0.7201924599434143, 0.4132476526938319]],
        [["Invert", 0.6707431156338866, 0.11622795952464149], ["Posterize", 0.12075972752370845, 0.18024933294172307]],
        [["Color", 0.5010057264087142, 0.5277767327434318], ["Rotate", 0.9486115946366559, 0.31485546630220784]],
        [["ShearX", 0.31741302466630406, 0.1991215806270692], ["Invert", 0.3744727015523084, 0.6914113986757578]],
        [["Brightness", 0.40348479064392617, 0.8924182735724888],
         ["Brightness", 0.1973098763857779, 0.3939288933689655]],
        [["Color", 0.01208688664030888, 0.6055693000885217], ["Equalize", 0.433259451147881, 0.420711137966155]],
        [["Cutout", 0.2620018360076487, 0.11594468278143644], ["Rotate", 0.1310401567856766, 0.7244318146544101]],
        [["ShearX", 0.15249651845933576, 0.35277277071866986], ["Contrast", 0.28221794032094016, 0.42036586509397444]],
        [["Brightness", 0.8492912150468908, 0.26386920887886056], ["Solarize", 0.8764208056263386, 0.1258195122766067]],
        [["ShearX", 0.8537058239675831, 0.8415101816171269], ["AutoContrast", 0.23958568830416294, 0.9889049529564014]],
        [["Rotate", 0.6463207930684552, 0.8750192129056532], ["Contrast", 0.6865032211768652, 0.8564981333033417]],
        [["Equalize", 0.8877190311811044, 0.7370995897848609],
         ["TranslateX", 0.9979660314391368, 0.005683998913244781]],
        [["Color", 0.6420017551677819, 0.6225337265571229], ["Solarize", 0.8344504978566362, 0.8332856969941151]],
        [["ShearX", 0.7439332981992567, 0.9747608698582039], ["Equalize", 0.6259189804002959, 0.028017478098245174]],
        [["TranslateY", 0.39794770293366843, 0.8482966537902709], ["Rotate", 0.9312935630405351, 0.5300586925826072]],
        [["Cutout", 0.8904075572021911, 0.3522934742068766], ["Equalize", 0.6431186289473937, 0.9930577962126151]],
        [["Contrast", 0.9183553386089476, 0.44974266209396685], ["TranslateY", 0.8193684583123862, 0.9633741156526566]],
        [["ShearY", 0.616078299924283, 0.19219314358924766], ["Solarize", 0.1480945914138868, 0.05922109541654652]],
        [["Solarize", 0.25332455064128157, 0.18853037431947994], ["ShearY", 0.9518390093954243, 0.14603930044061142]],
        [["Color", 0.8094378664335412, 0.37029830225408433], ["Contrast", 0.29504113617467465, 0.065096365468442]],
        [["AutoContrast", 0.7075167558685455, 0.7084621693458267],
         ["Sharpness", 0.03555539453323875, 0.5651948313888351]],
        [["TranslateY", 0.5969982600930229, 0.9857264201029572], ["Rotate", 0.9898628564873607, 0.1985685534926911]],
        [["Invert", 0.14915939942810352, 0.6595839632446547], ["Posterize", 0.768535289994361, 0.5997358684618563]],
        [["Equalize", 0.9162691815967111, 0.3331035307653627], ["Color", 0.8169118187605557, 0.7653910258006366]],
        [["Rotate", 0.43489185299530897, 0.752215269135173], ["Brightness", 0.1569828560334806, 0.8002808712857853]],
        [["Invert", 0.931876215328345, 0.029428644395760872], ["Equalize", 0.6330036052674145, 0.7235531014288485]],
        [["ShearX", 0.5216138393704968, 0.849272958911589], ["AutoContrast", 0.19572688655120263, 0.9786551568639575]],
        [["ShearX", 0.9899586208275011, 0.22580547500610293], ["Brightness", 0.9831311903178727, 0.5055159610855606]],
        [["Brightness", 0.29179117009211486, 0.48003584672937294],
         ["Solarize", 0.7544252317330058, 0.05806581735063043]],
        [["AutoContrast", 0.8919800329537786, 0.8511261613698553],
         ["Contrast", 0.49199446084551035, 0.7302297140181429]], [["Cutout", 0.7079723710644835, 0.032565015538375874],
                                                                  ["AutoContrast", 0.8259782090388609,
                                                                   0.7860708789468442]],
        [["Posterize", 0.9980262659801914, 0.6725084224935673], ["ShearY", 0.6195568269664682, 0.5444170291816751]],
        [["Posterize", 0.8687351834713217, 0.9978004914422602], ["Equalize", 0.4532646848325955, 0.6486748015710573]],
        [["Contrast", 0.2713928776950594, 0.15255249557027806], ["ShearY", 0.9276834387970199, 0.5266542862333478]],
        [["AutoContrast", 0.5240786618055582, 0.9325642258930253],
         ["Cutout", 0.38448627892037357, 0.21219415055662394]],
        [["TranslateX", 0.4299517937295352, 0.20133751201386152],
         ["TranslateX", 0.6753468310276597, 0.6985621035400441]],
        [["Rotate", 0.4006472499103597, 0.6704748473357586], ["Equalize", 0.674161668148079, 0.6528530101705237]],
        [["Equalize", 0.9139902833674455, 0.9015103149680278], ["Sharpness", 0.7289667720691948, 0.7623606352376232]],
        [["Cutout", 0.5911267429414259, 0.5953141187177585], ["Rotate", 0.5219064817468504, 0.11085141355857986]],
        [["TranslateX", 0.3620095133946267, 0.26194039409492476], ["Rotate", 0.3929841359545597, 0.4913406720338047]],
        [["Invert", 0.5175298901458896, 0.001661410821811482], ["Invert", 0.004656581318332242, 0.8157622192213624]],
        [["AutoContrast", 0.013609693335051465, 0.9318651749409604],
         ["Invert", 0.8980844358979592, 0.2268511862780368]],
        [["ShearY", 0.7717126261142194, 0.09975547983707711], ["Equalize", 0.7808494401429572, 0.4141412091009955]],
        [["TranslateX", 0.5878675721341552, 0.29813268038163376],
         ["Posterize", 0.21257276051591356, 0.2837285296666412]],
        [["Brightness", 0.4268335108566488, 0.4723784991635417], ["Cutout", 0.9386262901570471, 0.6597686851494288]],
        [["ShearX", 0.8259423807590159, 0.6215304795389204], ["Invert", 0.6663365779667443, 0.7729669184580387]],
        [["ShearY", 0.4801338723951297, 0.5220145420100984], ["Solarize", 0.9165803796596582, 0.04299335502862134]],
        [["Color", 0.17621114853558817, 0.7092601754635434], ["ShearX", 0.9014406936728542, 0.6028711944367818]],
        [["Rotate", 0.13073284972300658, 0.9088831512880851], ["ShearX", 0.4228105332316806, 0.7985249783662675]],
        [["Brightness", 0.9182753692730031, 0.0063635477774044436], ["Color", 0.4279825602663798, 0.28727149118585327]],
        [["Equalize", 0.578218285372267, 0.9611758542158054], ["Contrast", 0.5471552264150691, 0.8819635504027596]],
        [["Brightness", 0.3208589067274543, 0.45324733565167497], ["Solarize", 0.5218455808633233, 0.5946097503647126]],
        [["Equalize", 0.3790381278653, 0.8796082535775276], ["Solarize", 0.4875526773149246, 0.5186585878052613]],
        [["ShearY", 0.12026461479557571, 0.1336953429068397], ["Posterize", 0.34373988646025766, 0.8557727670803785]],
        [["Cutout", 0.2396745247507467, 0.8123036135209865], ["Equalize", 0.05022807681008945, 0.6648492261984383]],
        [["Brightness", 0.35226676470748264, 0.5950011514888855], ["Rotate", 0.27555076067000894, 0.9170063321486026]],
        [["ShearX", 0.320224630647278, 0.9683584649071976], ["Invert", 0.6905585196648905, 0.5929115667894518]],
        [["Color", 0.9941395717559652, 0.7474441679798101], ["Sharpness", 0.7559998478658021, 0.6656052889626682]],
        [["ShearY", 0.4004220568345669, 0.5737646992826074], ["Equalize", 0.9983495213746147, 0.8307907033362303]],
        [["Color", 0.13726809242038207, 0.9378850119950549], ["Equalize", 0.9853362454752445, 0.42670264496554156]],
        [["Invert", 0.13514636153298576, 0.13516363849081958], ["Sharpness", 0.2031189356693901, 0.6110226359872745]],
        [["TranslateX", 0.7360305209630797, 0.41849698571655614], ["Contrast", 0.8972161549144564, 0.7820296625565641]],
        [["Color", 0.02713118828682548, 0.717110684828096], ["TranslateY", 0.8118759006836348, 0.9120098002024992]],
        [["Sharpness", 0.2915428949403711, 0.7630303724396518], ["Solarize", 0.22030536162851078, 0.38654526772661757]],
        [["Equalize", 0.9949114839538582, 0.7193630656062793],
         ["AutoContrast", 0.00889496657931299, 0.2291400476524672]],
        [["Rotate", 0.7120948976490488, 0.7804359309791055], ["Cutout", 0.10445418104923654, 0.8022999156052766]],
        [["Equalize", 0.7941710117902707, 0.8648170634288153], ["Invert", 0.9235642581144047, 0.23810725859722381]],
        [["Cutout", 0.3669397998623156, 0.42612815083245004], ["Solarize", 0.5896322046441561, 0.40525016166956795]],
        [["Color", 0.8389858785714184, 0.4805764176488667], ["Rotate", 0.7483931487048825, 0.4731174601400677]],
        [["Sharpness", 0.19006538611394763, 0.9480745790240234],
         ["TranslateY", 0.13904429049439282, 0.04117685330615939]],
        [["TranslateY", 0.9958097661701637, 0.34853788612580905], ["Cutout", 0.2235829624082113, 0.3737887095480745]],
        [["ShearX", 0.635453761342424, 0.6063917273421382], ["Posterize", 0.8738297843709666, 0.4893042590265556]],
        [["Brightness", 0.7907245198402727, 0.7082189713070691], ["Color", 0.030313003541849737, 0.6927897798493439]],
        [["Cutout", 0.6965622481073525, 0.8103522907758203], ["ShearY", 0.6186794303078708, 0.28640671575703547]],
        [["ShearY", 0.43734910588450226, 0.32549342535621517], ["ShearX", 0.08154980987651872, 0.3286764923112455]],
        [["AutoContrast", 0.5262462005050853, 0.8175584582465848], ["Contrast", 0.8683217097363655, 0.548776281479276]],
        [["ShearY", 0.03957878500311707, 0.5102350637943197], ["Rotate", 0.13794708520303778, 0.38035687712954236]],
        [["Sharpness", 0.634288567312677, 0.6387948309075822],
         ["AutoContrast", 0.13437288694693272, 0.7150448869023095]],
        [["Contrast", 0.5198339640088544, 0.9409429390321714], ["Cutout", 0.09489154903321972, 0.6228488803821982]],
        [["Equalize", 0.8955909061806043, 0.7727336527163008],
         ["AutoContrast", 0.6459479564441762, 0.7065467781139214]],
        [["Invert", 0.07214420843537739, 0.15334721382249505], ["ShearX", 0.9242027778363903, 0.5809187849982554]],
        [["Equalize", 0.9144084379856188, 0.9457539278608998], ["Sharpness", 0.14337499858300173, 0.5978054365425495]],
        [["Posterize", 0.18894269796951202, 0.14676331276539045], ["Equalize", 0.846204299950047, 0.0720601838168885]],
        [["Contrast", 0.47354445405741163, 0.1793650330107468], ["Solarize", 0.9086106327264657, 0.7578807802091502]],
        [["AutoContrast", 0.11805466892967886, 0.6773620948318575],
         ["TranslateX", 0.584222568299264, 0.9475693349391936]],
        [["Brightness", 0.5833017701352768, 0.6892593824176294],
         ["AutoContrast", 0.9073141314561828, 0.5823085733964589]],
        [["TranslateY", 0.5711231614144834, 0.6436240447620021], ["Contrast", 0.21466964050052473, 0.8042843954486391]],
        [["Contrast", 0.22967904487976765, 0.2343103109298762], ["Invert", 0.5502897289159286, 0.386181060792375]],
        [["Invert", 0.7008423439928628, 0.4234003051405053], ["Rotate", 0.77270460187611, 0.6650852696828039]],
        [["Invert", 0.050618322309703534, 0.24277027926683614], ["TranslateX", 0.789703489736613, 0.5116446685339312]],
        [["Color", 0.363898083076868, 0.7870323584210503], ["ShearY", 0.009608425513626617, 0.6188625018465327]],
        [["TranslateY", 0.9447601615216088, 0.8605867115798349], ["Equalize", 0.24139180127003634, 0.9587337957930782]],
        [["Equalize", 0.3968589440144503, 0.626206375426996], ["Solarize", 0.3215967960673186, 0.826785464835443]],
        [["TranslateX", 0.06947339047121326, 0.016705969558222122],
         ["Contrast", 0.6203392406528407, 0.6433525559906872]],
        [["Solarize", 0.2479835265518212, 0.6335009955617831], ["Sharpness", 0.6260191862978083, 0.18998095149428562]],
        [["Invert", 0.9818841924943431, 0.03252098144087934], ["TranslateY", 0.9740718042586802, 0.32038951753031475]],
        [["Solarize", 0.8795784664090814, 0.7014953994354041],
         ["AutoContrast", 0.8508018319577783, 0.09321935255338443]],
        [["Color", 0.8067046326105318, 0.13732893832354054], ["Contrast", 0.7358549680271418, 0.7880588355974301]],
        [["Posterize", 0.5005885536838065, 0.7152229305267599], ["ShearX", 0.6714249591308944, 0.7732232697859908]],
        [["TranslateY", 0.5657943483353953, 0.04622399873706862],
         ["AutoContrast", 0.2787442688649845, 0.567024378767143]],
        [["ShearY", 0.7589839214283295, 0.041071003934029404], ["Equalize", 0.3719852873722692, 0.43285778682687326]],
        [["Posterize", 0.8841266183653291, 0.42441306955476366], ["Cutout", 0.06578801759412933, 0.5961125797961526]],
        [["Rotate", 0.4057875004314082, 0.20241115848366442],
         ["AutoContrast", 0.19331542807918067, 0.7175484678480565]],
        [["Contrast", 0.20331327116693088, 0.17135387852218742], ["Cutout", 0.6282459410351067, 0.6690015305529187]],
        [["ShearX", 0.4309850328306535, 0.99321178125828], ["AutoContrast", 0.01809604030453338, 0.693838277506365]],
        [["Rotate", 0.24343531125298268, 0.5326412444169899], ["Sharpness", 0.8663989992597494, 0.7643990609130789]],
        [["Rotate", 0.9785019204622459, 0.8941922576710696], ["ShearY", 0.3823185048761075, 0.9258854046017292]],
        [["ShearY", 0.5502613342963388, 0.6193478797355644], ["Sharpness", 0.2212116534610532, 0.6648232390110979]],
        [["TranslateY", 0.43222920981513757, 0.5657636397633089], ["ShearY", 0.9153733286073634, 0.4868521171273169]],
        [["Posterize", 0.12246560519738336, 0.9132288825898972], ["Cutout", 0.6058471327881816, 0.6426901876150983]],
        [["Color", 0.3693970222695844, 0.038929141432555436], ["Equalize", 0.6228052875653781, 0.05064436511347281]],
        [["Color", 0.7172600331356893, 0.2824542634766688], ["Color", 0.425293116261649, 0.1796441283313972]],
        [["Cutout", 0.7539608428122959, 0.9896141728228921], ["Solarize", 0.17811081117364758, 0.9064195503634402]],
        [["AutoContrast", 0.6761242607012717, 0.6484842446399923],
         ["AutoContrast", 0.1978135076901828, 0.42166879492601317]],
        [["ShearY", 0.25901666379802524, 0.4770778270322449], ["Solarize", 0.7640963173407052, 0.7548463227094349]],
        [["TranslateY", 0.9222487731783499, 0.33658389819616463], ["Equalize", 0.9159112511468139, 0.8877136302394797]],
        [["TranslateX", 0.8994836977137054, 0.11036053676846591],
         ["Sharpness", 0.9040333410652747, 0.007266095214664592]],
        [["Invert", 0.627758632524958, 0.8075245097227242], ["Color", 0.7525387912148516, 0.05950239294733184]],
        [["TranslateX", 0.43505193292761857, 0.38108822876120796],
         ["TranslateY", 0.7432578052364004, 0.685678116134759]],
        [["Contrast", 0.9293507582470425, 0.052266842951356196],
         ["Posterize", 0.45187123977747456, 0.8228290399726782]],
        [["ShearX", 0.07240786542746291, 0.8945667925365756], ["Brightness", 0.5305443506561034, 0.12025274552427578]],
        [["Invert", 0.40157564448143335, 0.5364745514006678], ["Posterize", 0.3316124671813876, 0.43002413237035997]],
        [["ShearY", 0.7152314630009072, 0.1938339083417453], ["Invert", 0.14102478508140615, 0.41047623580174253]],
        [["Equalize", 0.19862832613849246, 0.5058521685279254],
         ["Sharpness", 0.16481208629549782, 0.29126323102770557]],
        [["Equalize", 0.6951591703541872, 0.7294822018800076], ["ShearX", 0.8726656726111219, 0.3151484225786487]],
        [["Rotate", 0.17234370554263745, 0.9356543193000078], ["TranslateX", 0.4954374070084091, 0.05496727345849217]],
        [["Contrast", 0.347405480122842, 0.831553005022885], ["ShearX", 0.28946367213071134, 0.11905898704394013]],
        [["Rotate", 0.28096672507990683, 0.16181284050307398], ["Color", 0.6554918515385365, 0.8739728050797386]],
        [["Solarize", 0.05408073374114053, 0.5357087283758337],
         ["Posterize", 0.42457175211495335, 0.051807130609045515]],
        [["TranslateY", 0.6216669362331361, 0.9691341207381867], ["Rotate", 0.9833579358130944, 0.12227426932415297]],
        [["AutoContrast", 0.7572619475282892, 0.8062834082727393],
         ["Contrast", 0.1447865402875591, 0.40242646573228436]],
        [["Rotate", 0.7035658783466086, 0.9840285268256428], ["Contrast", 0.04613961510519471, 0.7666683217450163]],
        [["TranslateX", 0.4580462177951252, 0.6448678609474686],
         ["AutoContrast", 0.14845695613708987, 0.1581134188537895]],
        [["Color", 0.06795037145259564, 0.9115552821158709], ["TranslateY", 0.9972953449677655, 0.6791016521791214]],
        [["Cutout", 0.3586908443690823, 0.11578558293480945], ["Color", 0.49083981719164294, 0.6924851425917189]],
        [["Brightness", 0.7994717831637873, 0.7887316255321768],
         ["Posterize", 0.01280463502435425, 0.2799086732858721]], [["ShearY", 0.6733451536131859, 0.8122332639516706],
                                                                   ["AutoContrast", 0.20433889615637357,
                                                                    0.29023346867819966]],
        [["TranslateY", 0.709913512385177, 0.6538196931503809], ["Invert", 0.06629795606579203, 0.40913219547548296]],
        [["Sharpness", 0.4704559834362948, 0.4235993305308414], ["Equalize", 0.7578132044306966, 0.9388824249397175]],
        [["AutoContrast", 0.5281702802395268, 0.8077253610116979], ["Equalize", 0.856446858814119, 0.0479755681647559]],
        [["Color", 0.8244145826797791, 0.038409264586238945], ["Equalize", 0.4933123249234237, 0.8251940933672189]],
        [["TranslateX", 0.23949314158035084, 0.13576027004706692], ["ShearX", 0.8547563771688399, 0.8309262160483606]],
        [["Cutout", 0.4655680937486001, 0.2819807000622825], ["Contrast", 0.8439552665937905, 0.4843617871587037]],
        [["TranslateX", 0.19142454476784831, 0.7516148119169537],
         ["AutoContrast", 0.8677128351329768, 0.34967990912346336]],
        [["Contrast", 0.2997868299880966, 0.919508054854469], ["AutoContrast", 0.3003418493384957, 0.812314984368542]],
        [["Invert", 0.1070424236198183, 0.614674386498809], ["TranslateX", 0.5010973510899923, 0.20828478805259465]],
        [["Contrast", 0.6775882415611454, 0.6938564815591685], ["Cutout", 0.4814634264207498, 0.3086844939744179]],
        [["TranslateY", 0.939427105020265, 0.02531043619423201], ["Contrast", 0.793754257944812, 0.6676072472565451]],
        [["Sharpness", 0.09833672397575444, 0.5937214638292085], ["Rotate", 0.32530675291753763, 0.08302275740932441]],
        [["Sharpness", 0.3096455511562728, 0.6726732004553959],
         ["TranslateY", 0.43268997648796537, 0.8755012330217743]],
        [["ShearY", 0.9290771880324833, 0.22114736271319912], ["Equalize", 0.5520199288501478, 0.34269650332060553]],
        [["AutoContrast", 0.39763980746649374, 0.4597414582725454],
         ["Contrast", 0.941507852412761, 0.24991270562477041]],
        [["Contrast", 0.19419400547588095, 0.9127524785329233], ["Invert", 0.40544905179551727, 0.770081532844878]],
        [["Invert", 0.30473757368608334, 0.23534811781828846], ["Cutout", 0.26090722356706686, 0.5478390909877727]],
        [["Posterize", 0.49434361308057373, 0.05018423270527428], ["Color", 0.3041910676883317, 0.2603810415446437]],
        [["Invert", 0.5149061746764011, 0.9507449210221298], ["TranslateY", 0.4458076521892904, 0.8235358255774426]],
        [["Cutout", 0.7900006753351625, 0.905578861382507], ["Cutout", 0.6707153655762056, 0.8236715672258502]],
        [["Solarize", 0.8750534386579575, 0.10337670467100568], ["Posterize", 0.6102379615481381, 0.9264503915416868]],
        [["ShearY", 0.08448689377082852, 0.13981233725811626], ["TranslateX", 0.13979689669329498, 0.768774869872818]],
        [["TranslateY", 0.35752572266759985, 0.22827299847812488],
         ["Solarize", 0.3906957174236011, 0.5663314388307709]],
        [["ShearY", 0.29155240367061563, 0.8427516352971683], ["ShearX", 0.988825367441916, 0.9371258864857649]],
        [["Posterize", 0.3470780859769458, 0.5467686612321239], ["Rotate", 0.5758606274160093, 0.8843838082656007]],
        [["Cutout", 0.07825368363221841, 0.3230799425855425], ["Equalize", 0.2319163865298529, 0.42133965674727325]],
        [["Invert", 0.41972172597448654, 0.34618622513582953], ["ShearX", 0.33638469398198834, 0.9098575535928108]],
        [["Invert", 0.7322652233340448, 0.7747502957687412], ["Cutout", 0.9643121397298106, 0.7983335094634907]],
        [["TranslateY", 0.30039942808098496, 0.229018798182827],
         ["TranslateY", 0.27009499739380194, 0.6435577237846236]],
        [["Color", 0.38245274994070644, 0.7030758568461645], ["ShearX", 0.4429321461666281, 0.6963787864044149]],
        [["AutoContrast", 0.8432798685515605, 0.5775214369578088],
         ["Brightness", 0.7140899735355927, 0.8545854720117658]],
        [["Rotate", 0.14418935535613786, 0.5637968282213426], ["Color", 0.7115231912479835, 0.32584796564566776]],
        [["Sharpness", 0.4023501062807533, 0.4162097130412771],
         ["Brightness", 0.5536372686153666, 0.03004023273348777]],
        [["TranslateX", 0.7526053265574295, 0.5365938133399961], ["Cutout", 0.07914142706557492, 0.7544953091603148]],
        [["TranslateY", 0.6932934644882822, 0.5302211727137424], ["Invert", 0.5040606028391255, 0.6074863635108957]],
        [["Sharpness", 0.5013938602431629, 0.9572417724333157],
         ["TranslateY", 0.9160516359783026, 0.41798927975391675]],
        [["ShearY", 0.5130018836722556, 0.30209438428424185], ["Color", 0.15017170588500262, 0.20653495360587826]],
        [["TranslateX", 0.5293300090022314, 0.6407011888285266], ["Rotate", 0.4809817860439001, 0.3537850070371702]],
        [["Equalize", 0.42243081336551014, 0.13472721311046565], ["Posterize", 0.4700309639484068, 0.5197704360874883]],
        [["AutoContrast", 0.40674959899687235, 0.7312824868168921],
         ["TranslateX", 0.7397527975920833, 0.7068339877944815]],
        [["TranslateY", 0.5880995184787206, 0.41294111378078946], ["ShearX", 0.3181387627799316, 0.4810010147143413]],
        [["Color", 0.9898680233928507, 0.13241525577655167], ["Contrast", 0.9824932511238534, 0.5081145010853807]],
        [["Invert", 0.1591854062582687, 0.9760371953250404], ["Color", 0.9913399302056851, 0.8388709501056177]],
        [["Rotate", 0.6427451962231163, 0.9486793975292853],
         ["AutoContrast", 0.8501937877930463, 0.021326757974406196]],
        [["Contrast", 0.13611684531087598, 0.3050858709483848], ["Posterize", 0.06618644756084646, 0.8776928511951034]],
        [["TranslateX", 0.41021065663839407, 0.4965319749091702], ["Rotate", 0.07088831484595115, 0.4435516708223345]],
        [["Sharpness", 0.3151707977154323, 0.28275482520179296], ["Invert", 0.36980384682133804, 0.20813616084536624]],
        [["Cutout", 0.9979060206661017, 0.39712948644725854], ["Brightness", 0.42451052896163466, 0.942623075649937]],
        [["Equalize", 0.5300853308425644, 0.010183500830128867],
         ["AutoContrast", 0.06930788523716991, 0.5403125318991522]],
        [["Contrast", 0.010385458959237814, 0.2588311035539086], ["ShearY", 0.9347048553928764, 0.10439028366854963]],
        [["ShearY", 0.9867649486508592, 0.8409258132716434], ["ShearX", 0.48031199530836444, 0.7703375364614137]],
        [["ShearY", 0.04835889473136512, 0.2671081675890492], ["Brightness", 0.7856432618509617, 0.8032169570159564]],
        [["Posterize", 0.11112884927351185, 0.7116956530752987],
         ["TranslateY", 0.7339151092128607, 0.3331241226029017]],
        [["Invert", 0.13527036207875454, 0.8425980515358883], ["Color", 0.7836395778298139, 0.5517059252678862]],
        [["Sharpness", 0.012541163521491816, 0.013197550692292892],
         ["Invert", 0.6295957932861318, 0.43276521236056054]],
        [["AutoContrast", 0.7681480991225756, 0.3634284648496289],
         ["Brightness", 0.09708289828517969, 0.45016725043529726]],
        [["Brightness", 0.5839450499487329, 0.47525965678316795],
         ["Posterize", 0.43096581990183735, 0.9332382960125196]],
        [["Contrast", 0.9725334964552795, 0.9142902966863341], ["Contrast", 0.12376116410622995, 0.4355916974126801]],
        [["TranslateX", 0.8572708473690132, 0.02544522678265526],
         ["Sharpness", 0.37902120723460364, 0.9606092969833118]],
        [["TranslateY", 0.8907359001296927, 0.8011363927236099], ["Color", 0.7693777154407178, 0.0936768686746503]],
        [["Equalize", 0.0002657688243309364, 0.08190798535970034], ["Rotate", 0.5215478065240905, 0.5773519995038368]],
        [["TranslateY", 0.3383007813932477, 0.5733428274739165], ["Sharpness", 0.2436110797174722, 0.4757790814590501]],
        [["Cutout", 0.0957402176213592, 0.8914395928996034], ["Cutout", 0.4959915628586883, 0.25890349461645246]],
        [["AutoContrast", 0.594787300189186, 0.9627455357634459], ["ShearY", 0.5136027621132064, 0.10419602450259002]],
        [["Solarize", 0.4684077211553732, 0.6592850629431414], ["Sharpness", 0.2382385935956325, 0.6589291408243176]],
        [["Cutout", 0.4478786947325877, 0.6893616643143388], ["TranslateX", 0.2761781720270474, 0.21750622627277727]],
        [["Sharpness", 0.39476077929016484, 0.930902796668923], ["Cutout", 0.9073012208742808, 0.9881122386614257]],
        [["TranslateY", 0.0933719180021565, 0.7206252503441172], ["ShearX", 0.5151400441789256, 0.6307540083648309]],
        [["AutoContrast", 0.7772689258806401, 0.8159317013156503],
         ["AutoContrast", 0.5932793713915097, 0.05262217353927168]],
        [["Equalize", 0.38017352056118914, 0.8084724050448412], ["ShearY", 0.7239725628380852, 0.4246314890359326]],
        [["Cutout", 0.741157483503503, 0.13244380646497977], ["Invert", 0.03395378056675935, 0.7140036618098844]],
        [["Rotate", 0.0662727247460636, 0.7099861732415447], ["Rotate", 0.3168532707508249, 0.3553167425022127]],
        [["AutoContrast", 0.7429303516734129, 0.07117444599776435],
         ["Posterize", 0.5379537435918104, 0.807221330263993]],
        [["TranslateY", 0.9788586874795164, 0.7967243851346594], ["Invert", 0.4479103376922362, 0.04260360776727545]],
        [["Cutout", 0.28318121763188997, 0.7748680701406292],
         ["AutoContrast", 0.9109258369403016, 0.17126397858002085]],
        [["Color", 0.30183727885272027, 0.46718354750112456], ["TranslateX", 0.9628952256033627, 0.10269543754135535]],
        [["AutoContrast", 0.6316709389784041, 0.84287698792044],
         ["Brightness", 0.5544761629904337, 0.025264772745200004]],
        [["Rotate", 0.08803313299532567, 0.306059720523696], ["Invert", 0.5222165872425064, 0.045935208620454304]],
        [["TranslateY", 0.21912346831923835, 0.48529224559004436],
         ["TranslateY", 0.15466734731903942, 0.8929485418495068]],
        [["ShearX", 0.17141022847016563, 0.8607600402165531], ["ShearX", 0.6890511341106859, 0.7540899265679949]],
        [["Invert", 0.9417455522972059, 0.9021733684991224], ["Solarize", 0.7693107057723746, 0.7268007946568782]],
        [["Posterize", 0.02376991543373752, 0.6768442864453844], ["Rotate", 0.7736875065112697, 0.6706331753139825]],
        [["Contrast", 0.3623841610390669, 0.15023657344457686], ["Equalize", 0.32975472189318666, 0.05629246869510651]],
        [["Sharpness", 0.7874882420165824, 0.49535778020457066],
         ["Posterize", 0.09485578893387558, 0.6170768580482466]],
        [["Brightness", 0.7099280202949585, 0.021523012961427335],
         ["Posterize", 0.2076371467666719, 0.17168118578815206]],
        [["Color", 0.8546367645761538, 0.832011891505731], ["Equalize", 0.6429734783051777, 0.2618995960561532]],
        [["Rotate", 0.8780793721476224, 0.5920897827664297], ["ShearX", 0.5338303685064825, 0.8605424531336439]],
        [["Sharpness", 0.7504493806631884, 0.9723552387375258], ["Sharpness", 0.3206385634203266, 0.45127845905824693]],
        [["ShearX", 0.23794709526711355, 0.06257530645720066], ["Solarize", 0.9132374030587093, 0.6240819934824045]],
        [["Sharpness", 0.790583587969259, 0.28551171786655405], ["Contrast", 0.39872982844590554, 0.09644706751019538]],
        [["Equalize", 0.30681999237432944, 0.5645045018157916], ["Posterize", 0.525966242669736, 0.7360106111256014]],
        [["TranslateX", 0.4881014179825114, 0.6317220208872226], ["ShearX", 0.2935158995550958, 0.23104608987381758]],
        [["Rotate", 0.49977116738568395, 0.6610761068306319], ["TranslateY", 0.7396566602715687, 0.09386747830045217]],
        [["ShearY", 0.5909773790018789, 0.16229529902832718], ["Equalize", 0.06461394468918358, 0.6661349001143908]],
        [["TranslateX", 0.7218443721851834, 0.04435720302810153], ["Cutout", 0.986686540951642, 0.734771197038724]],
        [["ShearX", 0.5353800096911666, 0.8120139502148365], ["Equalize", 0.4613239578449774, 0.5159528929124512]],
        [["Color", 0.0871713897628631, 0.7708895183198486], ["Solarize", 0.5811386808912219, 0.35260648120785887]],
        [["Posterize", 0.3910857927477053, 0.4329219555775561], ["Color", 0.9115983668789468, 0.6043069944145293]],
        [["Posterize", 0.07493067637060635, 0.4258000066006725],
         ["AutoContrast", 0.4740957581389772, 0.49069587151651295]],
        [["Rotate", 0.34086200894268937, 0.9812149332288828], ["Solarize", 0.6801012471371733, 0.17271491146753837]],
        [["Color", 0.20542270872895207, 0.5532087457727624], ["Contrast", 0.2718692536563381, 0.20313287569510108]],
        [["Equalize", 0.05199827210980934, 0.0832859890912212],
         ["AutoContrast", 0.8092395764794107, 0.7778945136511004]],
        [["Sharpness", 0.1907689513066838, 0.7705754572256907], ["Color", 0.3911178658498049, 0.41791326933095485]],
        [["Solarize", 0.19611855804748257, 0.2407807485604081],
         ["AutoContrast", 0.5343964972940493, 0.9034209455548394]],
        [["Color", 0.43586520148538865, 0.4711164626521439], ["ShearY", 0.28635408186820555, 0.8417816793020271]],
        [["Cutout", 0.09818482420382535, 0.1649767430954796], ["Cutout", 0.34582392911178494, 0.3927982995799828]],
        [["ShearX", 0.001253882705272269, 0.48661629027584596], ["Solarize", 0.9229221435457137, 0.44374894836659073]],
        [["Contrast", 0.6829734655718668, 0.8201750485099037], ["Cutout", 0.7886756837648936, 0.8423285219631946]],
        [["TranslateY", 0.857017093561528, 0.3038537151773969], ["Invert", 0.12809228606383538, 0.23637166191748027]],
        [["Solarize", 0.9829027723424164, 0.9723093910674763], ["Color", 0.6346495302126811, 0.5405494753107188]],
        [["AutoContrast", 0.06868643520377715, 0.23758659417688077],
         ["AutoContrast", 0.6648225411500879, 0.5618315648260103]],
        [["Invert", 0.44202305603311676, 0.9945938909685547], ["Equalize", 0.7991650497684454, 0.16014142656347097]],
        [["AutoContrast", 0.8778631604769588, 0.03951977631894088],
         ["ShearY", 0.8495160088963707, 0.35771447321250416]],
        [["Color", 0.5365078341001592, 0.21102444169782308], ["ShearX", 0.7168869678248874, 0.3904298719872734]],
        [["TranslateX", 0.6517203786101899, 0.6467598990650437], ["Invert", 0.26552491504364517, 0.1210812827294625]],
        [["Posterize", 0.35196021684368994, 0.8420648319941891], ["Invert", 0.7796829363930631, 0.9520895999240896]],
        [["Sharpness", 0.7391572148971984, 0.4853940393452846], ["TranslateX", 0.7641915295592839, 0.6351349057666782]],
        [["Posterize", 0.18485880221115913, 0.6117603277356728], ["Rotate", 0.6541660490605724, 0.5704041108375348]],
        [["TranslateY", 0.27517423188070533, 0.6610080904072458], ["Contrast", 0.6091250547289317, 0.7702443247557892]],
        [["Equalize", 0.3611798581067118, 0.6623615672642768], ["TranslateX", 0.9537265090885917, 0.06352772509358584]],
        [["ShearX", 0.09720029389103535, 0.7800423126320308], ["Invert", 0.30314352455858884, 0.8519925470889914]],
        [["Brightness", 0.06931529763458055, 0.57760829499712], ["Cutout", 0.637251974467394, 0.7184346129191052]],
        [["AutoContrast", 0.5026722100286064, 0.32025257156541886],
         ["Contrast", 0.9667478703047919, 0.14178519432669368]],
        [["Equalize", 0.5924463845816984, 0.7187610262181517], ["TranslateY", 0.7059479079159405, 0.06551471830655187]],
        [["Sharpness", 0.18161164512332928, 0.7576138481173385],
         ["Brightness", 0.19191138767695282, 0.7865880269424701]],
        [["Brightness", 0.36780861866078696, 0.0677855546737901],
         ["AutoContrast", 0.8491446654142264, 0.09217782099938121]],
        [["TranslateY", 0.06011399855120858, 0.8374487034710264],
         ["TranslateY", 0.8373922962070498, 0.1991295720254297]],
        [["Posterize", 0.702559916122481, 0.30257509683007755], ["Rotate", 0.249899495398891, 0.9370437251176267]],
        [["ShearX", 0.9237874098232075, 0.26241907483351146], ["Brightness", 0.7221766836146657, 0.6880749752986671]],
        [["Cutout", 0.37994098189193104, 0.7836874473657957], ["ShearX", 0.9212861960976824, 0.8140948561570449]],
        [["Posterize", 0.2584098274786417, 0.7990847652004848], ["Invert", 0.6357731737590063, 0.1066304859116326]],
        [["Sharpness", 0.4412790857539922, 0.9692465283229825], ["Color", 0.9857401617339051, 0.26755393929808713]],
        [["Equalize", 0.22348671644912665, 0.7370019910830038], ["Posterize", 0.5396106339575417, 0.5559536849843303]],
        [["Equalize", 0.8742967663495852, 0.2797122599926307], ["Rotate", 0.4697322053105951, 0.8769872942579476]],
        [["Sharpness", 0.44279911640509206, 0.07729581896071613], ["Cutout", 0.3589177366154631, 0.2704031551235969]],
        [["TranslateX", 0.614216412574085, 0.47929659784170453],
         ["Brightness", 0.6686234118438007, 0.05700784068205689]],
        [["ShearY", 0.17920614630857634, 0.4699685075827862], ["Color", 0.38251870810870003, 0.7262706923005887]],
        [["Solarize", 0.4951799001144561, 0.212775278026479], ["TranslateX", 0.8666105646463097, 0.6750496637519537]],
        [["Color", 0.8110864170849051, 0.5154263861958484], ["Sharpness", 0.2489044083898776, 0.3763372541462343]],
        [["Cutout", 0.04888193613483871, 0.06041664638981603], ["Color", 0.06438587718683708, 0.5797881428892969]],
        [["Rotate", 0.032427448352152166, 0.4445797818376559], ["Posterize", 0.4459357828482998, 0.5879865187630777]],
        [["ShearX", 0.1617179557693058, 0.050796802246318884], ["Cutout", 0.8142465452060423, 0.3836391305618707]],
        [["TranslateY", 0.1806857249209416, 0.36697730355422675], ["Rotate", 0.9897576550818276, 0.7483432452225264]],
        [["Brightness", 0.18278016458098223, 0.952352527690299], ["Cutout", 0.3269735224453044, 0.3924869905012752]],
        [["ShearX", 0.870832707718742, 0.3214743207190739], ["Cutout", 0.6805560681792573, 0.6984188155282459]],
        [["TranslateX", 0.4157118388833776, 0.3964216288135384], ["TranslateX", 0.3253012682285006, 0.624835513104391]],
        [["Contrast", 0.7678168037628158, 0.31033802162621793], ["ShearX", 0.27022424855977134, 0.3773245605126201]],
        [["TranslateX", 0.37812621869017593, 0.7657993810740699], ["Rotate", 0.18081890120092914, 0.8893511219618171]],
        [["Posterize", 0.8735859716088367, 0.18243793043074286], ["TranslateX", 0.90435994250313, 0.24116383818819453]],
        [["Invert", 0.06666709253664793, 0.3881076083593933], ["TranslateX", 0.3783333964963522, 0.14411014979589543]],
        [["Equalize", 0.8741147867162096, 0.14203839235846816], ["TranslateX", 0.7801536758037405, 0.6952401607812743]],
        [["Cutout", 0.6095335117944475, 0.5679026063718094], ["Posterize", 0.06433868172233115, 0.07139559616012303]],
        [["TranslateY", 0.3020364047315408, 0.21459810361176246], ["Cutout", 0.7097677414888889, 0.2942144632587549]],
        [["Brightness", 0.8223662419048653, 0.195700694016108], ["Invert", 0.09345407040803999, 0.779843655582099]],
        [["TranslateY", 0.7353462929356228, 0.0468520680237382], ["Cutout", 0.36530918247940425, 0.3897292909049672]],
        [["Invert", 0.9676896451721213, 0.24473302189463453], ["Invert", 0.7369271521408992, 0.8193267003356975]],
        [["Sharpness", 0.8691871972054326, 0.4441713912682772], ["ShearY", 0.47385584832119887, 0.23521684584675429]],
        [["ShearY", 0.9266946026184021, 0.7611986713358834], ["TranslateX", 0.6195820760253926, 0.14661428669483678]],
        [["Sharpness", 0.08470870576026868, 0.3380219099907229],
         ["TranslateX", 0.3062343307496658, 0.7135777338095889]],
        [["Sharpness", 0.5246448204194909, 0.3193061215236702], ["ShearX", 0.8160637208508432, 0.9720697396582731]],
        [["Posterize", 0.5249259956549405, 0.3492042382504774], ["Invert", 0.8183138799547441, 0.11107271762524618]],
        [["TranslateY", 0.210869733350744, 0.7138905840721885], ["Sharpness", 0.7773226404450125, 0.8005353621959782]],
        [["Posterize", 0.33067522385556025, 0.32046239220630124],
         ["AutoContrast", 0.18918147708798405, 0.4646281070474484]],
        [["TranslateX", 0.929502026131094, 0.8029128121556285], ["Invert", 0.7319794306118105, 0.5421878712623392]],
        [["ShearX", 0.25645940834182723, 0.42754710760160963], ["ShearX", 0.44640695310173306, 0.8132185532296811]],
        [["Color", 0.018436846416536312, 0.8439313862001113], ["Sharpness", 0.3722867661453415, 0.5103570873163251]],
        [["TranslateX", 0.7285989086776543, 0.4809027697099264],
         ["TranslateY", 0.9740807004893643, 0.8241085438636939]],
        [["Posterize", 0.8721868989693397, 0.5700907310383815], ["Posterize", 0.4219074410577852, 0.8032643572845402]],
        [["Contrast", 0.9811380092558266, 0.8498397471632105], ["Sharpness", 0.8380884329421594, 0.18351306571903125]],
        [["TranslateY", 0.3878939366762001, 0.4699103438753077], ["Invert", 0.6055556353233807, 0.8774727658400134]],
        [["TranslateY", 0.052317005261018346, 0.39471450378745787],
         ["ShearX", 0.8612486845942395, 0.28834103278807466]],
        [["Color", 0.511993351208063, 0.07251427040525904], ["Solarize", 0.9898097047354855, 0.299761565689576]],
        [["Equalize", 0.2721248231619904, 0.6870975927455507], ["Cutout", 0.8787327242363994, 0.06228061428917098]],
        [["Invert", 0.8931880335225408, 0.49720931867378193], ["Posterize", 0.9619698792159256, 0.17859639696940088]],
        [["Posterize", 0.0061688075074411985, 0.08082938731035938],
         ["Brightness", 0.27745128028826993, 0.8638528796903816]],
        [["ShearY", 0.9140200609222026, 0.8240421430867707], ["Invert", 0.651734417415332, 0.08871906369930926]],
        [["Color", 0.45585010413511196, 0.44705070078574316], ["Color", 0.26394624901633146, 0.11242877788650807]],
        [["ShearY", 0.9200278466372522, 0.2995901331149652], ["Cutout", 0.8445407215116278, 0.7410524214287446]],
        [["ShearY", 0.9950483746990132, 0.112964468262847], ["ShearY", 0.4118332303218585, 0.44839613407553636]],
        [["Contrast", 0.7905821952255192, 0.23360046159385106], ["Posterize", 0.8611787233956044, 0.8984260048943528]],
        [["TranslateY", 0.21448061359312853, 0.8228112806838331], ["Contrast", 0.8992297266152983, 0.9179231590570998]],
        [["Invert", 0.3924194798946006, 0.31830516468371495], ["Rotate", 0.8399556845248508, 0.3764892022932781]],
        [["Cutout", 0.7037916990046816, 0.9214620769502728],
         ["AutoContrast", 0.02913794613018239, 0.07808607528954048]],
        [["ShearY", 0.6041490474263381, 0.6094184590800105], ["Equalize", 0.2932954517354919, 0.5840888946081727]],
        [["ShearX", 0.6056801676269449, 0.6948580442549543], ["Cutout", 0.3028001021044615, 0.15117101733894078]],
        [["Brightness", 0.8011486803860253, 0.18864079729374195],
         ["Solarize", 0.014965327213230961, 0.8842620292527029]],
        [["Invert", 0.902244007904273, 0.5634673798052033], ["Equalize", 0.13422913507398349, 0.4110956745883727]],
        [["TranslateY", 0.9981773319103838, 0.09568550987216096], ["Color", 0.7627662124105109, 0.8494409737419493]],
        [["Cutout", 0.3013527640416782, 0.03377226729898486], ["ShearX", 0.5727964831614619, 0.8784196638222834]],
        [["TranslateX", 0.6050722426803684, 0.3650103962378708],
         ["TranslateX", 0.8392084589130886, 0.6479816470292911]],
        [["Rotate", 0.5032806606500023, 0.09276980118866307], ["TranslateY", 0.7800234515261191, 0.18896454379343308]],
        [["Invert", 0.9266027256244017, 0.8246111062199752], ["Contrast", 0.12112023357797697, 0.33870762271759436]],
        [["Brightness", 0.8688784756993134, 0.17263759696106606], ["ShearX", 0.5133700431071326, 0.6686811994542494]],
        [["Invert", 0.8347840440941976, 0.03774897445901726], ["Brightness", 0.24925057499276548, 0.04293631677355758]],
        [["Color", 0.5998145279485104, 0.4820093200092529], ["TranslateY", 0.6709586184077769, 0.07377334081382858]],
        [["AutoContrast", 0.7898846202957984, 0.325293526672498], ["Contrast", 0.5156435596826767, 0.2889223168660645]],
        [["ShearX", 0.08147389674998307, 0.7978924681113669], ["Contrast", 0.7270003309106291, 0.009571215234092656]],
        [["Sharpness", 0.417607614440786, 0.9532566433338661], ["Posterize", 0.7186586546796782, 0.6936509907073302]],
        [["ShearX", 0.9555300215926675, 0.1399385550263872], ["Color", 0.9981041061848231, 0.5037462398323248]],
        [["Equalize", 0.8003487831375474, 0.5413759363796945], ["ShearY", 0.0026607045117773565, 0.019262273030984933]],
        [["TranslateY", 0.04845391502469176, 0.10063445212118283], ["Cutout", 0.8273170186786745, 0.5045257728554577]],
        [["TranslateX", 0.9690985344978033, 0.505202991815533],
         ["TranslateY", 0.7255326592928096, 0.02103609500701631]],
        [["Solarize", 0.4030771176836736, 0.8424237871457034], ["Cutout", 0.28705805963928965, 0.9601617893682582]],
        [["Sharpness", 0.16865290353070606, 0.6899673563468826], ["Posterize", 0.3985430034869616, 0.6540651997730774]],
        [["ShearY", 0.21395578485362032, 0.09519358818949009], ["Solarize", 0.6692821708524135, 0.6462523623552485]],
        [["AutoContrast", 0.912360598054091, 0.029800239085051583],
         ["Invert", 0.04319256403746308, 0.7712501517098587]],
        [["ShearY", 0.9081969961839055, 0.4581560239984739], ["AutoContrast", 0.5313894814729159, 0.5508393335751848]],
        [["ShearY", 0.860528568424097, 0.8196987216301588], ["Posterize", 0.41134650331494205, 0.3686632018978778]],
        [["AutoContrast", 0.8753670810078598, 0.3679438326304749],
         ["Invert", 0.010444228965415858, 0.9581244779208277]], [["Equalize", 0.07071836206680682, 0.7173594756186462],
                                                                 ["Brightness", 0.06111434312497388,
                                                                  0.16175064669049277]],
        [["AutoContrast", 0.10522219073562122, 0.9768776621069855],
         ["TranslateY", 0.2744795945215529, 0.8577967957127298]],
        [["AutoContrast", 0.7628146493166175, 0.996157376418147], ["Contrast", 0.9255565598518469, 0.6826126662976868]],
        [["TranslateX", 0.017225816199011312, 0.2470332491402908],
         ["Solarize", 0.44048494909493807, 0.4492422515972162]],
        [["ShearY", 0.38885252627795064, 0.10272256704901939], ["Equalize", 0.686154959829183, 0.8973517148655337]],
        [["Rotate", 0.29628991573592967, 0.16639926575004715], ["ShearX", 0.9013782324726413, 0.0838318162771563]],
        [["Color", 0.04968391374688563, 0.6138600739645352], ["Invert", 0.11177127838716283, 0.10650198522261578]],
        [["Invert", 0.49655016367624016, 0.8603374164829688], ["ShearY", 0.40625439617553727, 0.4516437918820778]],
        [["TranslateX", 0.15015718916062992, 0.13867777502116208],
         ["Brightness", 0.3374464418810188, 0.7613355669536931]],
        [["Invert", 0.644644393321966, 0.19005804481199562], ["AutoContrast", 0.2293259789431853, 0.30335723256340186]],
        [["Solarize", 0.004968793254801596, 0.5370892072646645], ["Contrast", 0.9136902637865596, 0.9510587477779084]],
        [["Rotate", 0.38991518440867123, 0.24796987467455756], ["Sharpness", 0.9911180315669776, 0.5265657122981591]],
        [["Solarize", 0.3919646484436238, 0.6814994037194909], ["Sharpness", 0.4920838987787103, 0.023425724294012018]],
        [["TranslateX", 0.25107587874378867, 0.5414936560189212], ["Cutout", 0.7932919623814599, 0.9891303444820169]],
        [["Brightness", 0.07863012174272999, 0.045175652208389594],
         ["Solarize", 0.889609658064552, 0.8228793315963948]],
        [["Cutout", 0.20477096178169596, 0.6535063675027364], ["ShearX", 0.9216318577173639, 0.2908690977359947]],
        [["Contrast", 0.7035118947423187, 0.45982709058312454], ["Contrast", 0.7130268070749464, 0.8635123354235471]],
        [["Sharpness", 0.26319477541228997, 0.7451278726847078], ["Rotate", 0.8170499362173754, 0.13998593411788207]],
        [["Rotate", 0.8699365715164192, 0.8878057721750832], ["Equalize", 0.06682350555715044, 0.7164702080630689]],
        [["ShearY", 0.3137466057521987, 0.6747433496011368], ["Rotate", 0.42118828936218133, 0.980121180104441]],
        [["Solarize", 0.8470375049950615, 0.15287589264139223], ["Cutout", 0.14438435054693055, 0.24296463267973512]],
        [["TranslateY", 0.08822241792224905, 0.36163911974799356],
         ["TranslateY", 0.11729726813270003, 0.6230889726445291]],
        [["ShearX", 0.7720112337718541, 0.2773292905760122], ["Sharpness", 0.756290929398613, 0.27830353710507705]],
        [["Color", 0.33825031007968287, 0.4657590047522816], ["ShearY", 0.3566628994713067, 0.859750504071925]],
        [["TranslateY", 0.06830147433378053, 0.9348778582086664],
         ["TranslateX", 0.15509346516378553, 0.26320778885339435]],
        [["Posterize", 0.20266751150740858, 0.008351463842578233],
         ["Sharpness", 0.06506971109417259, 0.7294471760284555]],
        [["TranslateY", 0.6278911394418829, 0.8702181892620695], ["Invert", 0.9367073860264247, 0.9219230428944211]],
        [["Sharpness", 0.1553425337673321, 0.17601557714491345], ["Solarize", 0.7040449681338888, 0.08764313147327729]],
        [["Equalize", 0.6082233904624664, 0.4177428549911376],
         ["AutoContrast", 0.04987405274618151, 0.34516208204700916]],
        [["Brightness", 0.9616085936167699, 0.14561237331885468],
         ["Solarize", 0.8927707736296572, 0.31176907850205704]],
        [["Brightness", 0.6707778304730988, 0.9046457117525516],
         ["Brightness", 0.6801448953060988, 0.20015313057149042]],
        [["Color", 0.8292680845499386, 0.5181603879593888], ["Brightness", 0.08549161770369762, 0.6567870536463203]],
        [["ShearY", 0.267802208078051, 0.8388133819588173], ["Sharpness", 0.13453409120796123, 0.10028351311149486]],
        [["Posterize", 0.775796593610272, 0.05359034561289766], ["Cutout", 0.5067360625733027, 0.054451986840317934]],
        [["TranslateX", 0.5845238647690084, 0.7507147553486293],
         ["Brightness", 0.2642051786121197, 0.2578358927056452]],
        [["Cutout", 0.10787517610922692, 0.8147986902794228], ["Contrast", 0.2190149206329539, 0.902210615462459]],
        [["TranslateX", 0.5663614214181296, 0.05309965916414028], ["ShearX", 0.9682797885154938, 0.41791929533938466]],
        [["ShearX", 0.2345325577621098, 0.383780128037189], ["TranslateX", 0.7298083748149163, 0.644325797667087]],
        [["Posterize", 0.5138725709682734, 0.7901809917259563],
         ["AutoContrast", 0.7966018627776853, 0.14529337543427345]],
        [["Invert", 0.5973031989249785, 0.417399314592829], ["Solarize", 0.9147539948653116, 0.8221272315548086]],
        [["Posterize", 0.601596043336383, 0.18969646160963938], ["Color", 0.7527275484079655, 0.431793831326888]],
        [["Equalize", 0.6731483454430538, 0.7866786558207602], ["TranslateX", 0.97574396899191, 0.5970255778044692]],
        [["Cutout", 0.15919495850169718, 0.8916094305850562], ["Invert", 0.8351348834751027, 0.4029937360314928]],
        [["Invert", 0.5894085405226027, 0.7283806854157764], ["Brightness", 0.3973976860470554, 0.949681121498567]],
        [["AutoContrast", 0.3707914135327408, 0.21192068592079616],
         ["ShearX", 0.28040127351140676, 0.6754553511344856]],
        [["Solarize", 0.07955132378694896, 0.15073572961927306], ["ShearY", 0.5735850168851625, 0.27147326850217746]],
        [["Equalize", 0.678653949549764, 0.8097796067861455], ["Contrast", 0.2283048527510083, 0.15507804874474185]],
        [["Equalize", 0.286013868374536, 0.186785848694501], ["Posterize", 0.16319021740810458, 0.1201304443285659]],
        [["Sharpness", 0.9601590830563757, 0.06267915026513238],
         ["AutoContrast", 0.3813920685124327, 0.294224403296912]],
        [["Brightness", 0.2703246632402241, 0.9168405377492277], ["ShearX", 0.6156009855831097, 0.4955986055846403]],
        [["Color", 0.9065504424987322, 0.03393612216080133], ["ShearY", 0.6768595880405884, 0.9981068127818191]],
        [["Equalize", 0.28812842368483904, 0.300387487349145], ["ShearY", 0.28812248704858345, 0.27105076231533964]],
        [["Brightness", 0.6864882730513477, 0.8205553299102412], ["Cutout", 0.45995236371265424, 0.5422030370297759]],
        [["Color", 0.34941404877084326, 0.25857961830158516], ["AutoContrast", 0.3451390878441899, 0.5000938249040454]],
        [["Invert", 0.8268247541815854, 0.6691380821226468], ["Cutout", 0.46489193601530476, 0.22620873109485895]],
        [["Rotate", 0.17879730528062376, 0.22670425330593935], ["Sharpness", 0.8692795688221834, 0.36586055020855723]],
        [["Brightness", 0.31203975139659634, 0.6934046293010939], ["Cutout", 0.31649437872271236, 0.08078625004157935]],
        [["Cutout", 0.3119482836150119, 0.6397160035509996], ["Contrast", 0.8311248624784223, 0.22897510169718616]],
        [["TranslateX", 0.7631157841429582, 0.6482890521284557],
         ["Brightness", 0.12681196272427664, 0.3669813784257344]],
        [["TranslateX", 0.06027722649179801, 0.3101104512201861],
         ["Sharpness", 0.5652076706249394, 0.05210008400968136]],
        [["AutoContrast", 0.39213552101583127, 0.5047021194355596], ["ShearY", 0.7164003055682187, 0.8063370761002899]],
        [["Solarize", 0.9574307011238342, 0.21472064809226854],
         ["AutoContrast", 0.8102612285047174, 0.716870148067014]], [["Rotate", 0.3592634277567387, 0.6452602893051465],
                                                                    ["AutoContrast", 0.27188430331411506,
                                                                     0.06003099168464854]],
        [["Cutout", 0.9529536554825503, 0.5285505311027461], ["Solarize", 0.08478231903311029, 0.15986449762728216]],
        [["TranslateY", 0.31176130458018936, 0.5642853506158253],
         ["Equalize", 0.008890883901317648, 0.5146121040955942]],
        [["Color", 0.40773645085566157, 0.7110398926612682], ["Color", 0.18233100156439364, 0.7830036002758337]],
        [["Posterize", 0.5793809197821732, 0.043748553135581236], ["Invert", 0.4479962016131668, 0.7349663010359488]],
        [["TranslateX", 0.1994882312299382, 0.05216859488899439], ["Rotate", 0.48288726352035416, 0.44713829026777585]],
        [["Posterize", 0.22122838185154603, 0.5034546841241283],
         ["TranslateX", 0.2538745835410222, 0.6129055170893385]],
        [["Color", 0.6786559960640814, 0.4529749369803212], ["Equalize", 0.30215879674415336, 0.8733394611096772]],
        [["Contrast", 0.47316062430673456, 0.46669538897311447], ["Invert", 0.6514906551984854, 0.3053339444067804]],
        [["Equalize", 0.6443202625334524, 0.8689731394616441], ["Color", 0.7549183794057628, 0.8889001426329578]],
        [["Solarize", 0.616709740662654, 0.7792180816399313], ["ShearX", 0.9659155537406062, 0.39436937531179495]],
        [["Equalize", 0.23694011299406226, 0.027711152164392128],
         ["TranslateY", 0.1677339686527083, 0.3482126536808231]],
        [["Solarize", 0.15234175951790285, 0.7893840414281341],
         ["TranslateX", 0.2396395768284183, 0.27727219214979715]],
        [["Contrast", 0.3792017455380605, 0.32323660409845334], ["Contrast", 0.1356037413846466, 0.9127772969992305]],
        [["ShearX", 0.02642732222284716, 0.9184662576502115], ["Equalize", 0.11504884472142995, 0.8957638893097964]],
        [["TranslateY", 0.3193812913345325, 0.8828100030493128], ["ShearY", 0.9374975727563528, 0.09909415611083694]],
        [["AutoContrast", 0.025840721736048122, 0.7941037581373024],
         ["TranslateY", 0.498518003323313, 0.5777122846572548]],
        [["ShearY", 0.6042199307830248, 0.44809668754508836], ["Cutout", 0.3243978207701482, 0.9379740926294765]],
        [["ShearY", 0.6858549297583574, 0.9993252035788924], ["Sharpness", 0.04682428732773203, 0.21698099707915652]],
        [["ShearY", 0.7737469436637263, 0.8810127181224531], ["ShearY", 0.8995655445246451, 0.4312416220354539]],
        [["TranslateY", 0.4953094136709374, 0.8144161580138571], ["Solarize", 0.26301211718928097, 0.518345311180405]],
        [["Brightness", 0.8820246486031275, 0.571075863786249], ["ShearX", 0.8586669146703955, 0.0060476383595142735]],
        [["Sharpness", 0.20519233710982254, 0.6144574759149729],
         ["Posterize", 0.07976625267460813, 0.7480145046726968]],
        [["ShearY", 0.374075419680195, 0.3386105402023202], ["ShearX", 0.8228083637082115, 0.5885174783155361]],
        [["Brightness", 0.3528780713814561, 0.6999884884306623],
         ["Sharpness", 0.3680348120526238, 0.16953358258959617]],
        [["Brightness", 0.24891223104442084, 0.7973853494920095],
         ["TranslateX", 0.004256803835524736, 0.0470216343108546]],
        [["Posterize", 0.1947344282646012, 0.7694802711054367], ["Cutout", 0.9594385534844785, 0.5469744140592429]],
        [["Invert", 0.19012504762806026, 0.7816140211434693],
         ["TranslateY", 0.17479746932338402, 0.024249345245078602]],
        [["Rotate", 0.9669262055946796, 0.510166180775991], ["TranslateX", 0.8990602034610352, 0.6657802719304693]],
        [["ShearY", 0.5453049050407278, 0.8476872739603525], ["Cutout", 0.14226529093962592, 0.15756960661106634]],
        [["Equalize", 0.5895291156113004, 0.6797218994447763], ["TranslateY", 0.3541442192192753, 0.05166001155849864]],
        [["Equalize", 0.39530681662726097, 0.8448335365081087], ["Brightness", 0.6785483272734143, 0.8805568647038574]],
        [["Cutout", 0.28633258271917905, 0.7750870268336066], ["Equalize", 0.7221097824537182, 0.5865506280531162]],
        [["Posterize", 0.9044429629421187, 0.4620266401793388], ["Invert", 0.1803008045494473, 0.8073190766288534]],
        [["Sharpness", 0.7054649148075851, 0.3877207948962055],
         ["TranslateX", 0.49260224225927285, 0.8987462620731029]],
        [["Sharpness", 0.11196934729294483, 0.5953704422694938],
         ["Contrast", 0.13969334315069737, 0.19310569898434204]],
        [["Posterize", 0.5484346101051778, 0.7914140118600685],
         ["Brightness", 0.6428044691630473, 0.18811316670808076]],
        [["Invert", 0.22294834094984717, 0.05173157689962704], ["Cutout", 0.6091129168510456, 0.6280845506243643]],
        [["AutoContrast", 0.5726444076195267, 0.2799840903601295], ["Cutout", 0.3055752727786235, 0.591639807512993]],
        [["Brightness", 0.3707116723204462, 0.4049175910826627], ["Rotate", 0.4811601625588309, 0.2710760253723644]],
        [["ShearY", 0.627791719653608, 0.6877498291550205], ["TranslateX", 0.8751753308366824, 0.011164650018719358]],
        [["Posterize", 0.33832547954522263, 0.7087039872581657], ["Posterize", 0.6247474435007484, 0.7707784192114796]],
        [["Contrast", 0.17620186308493468, 0.9946224854942095], ["Solarize", 0.5431896088395964, 0.5867904203742308]],
        [["ShearX", 0.4667959516719652, 0.8938082224109446], ["TranslateY", 0.7311343008292865, 0.6829842246020277]],
        [["ShearX", 0.6130281467237769, 0.9924010909612302], ["Brightness", 0.41039241699696916, 0.9753218875311392]],
        [["TranslateY", 0.0747250386427123, 0.34602725521067534], ["Rotate", 0.5902597465515901, 0.361094672021087]],
        [["Invert", 0.05234890878959486, 0.36914978664919407], ["Sharpness", 0.42140532878231374, 0.19204058551048275]],
        [["ShearY", 0.11590485361909497, 0.6518540857972316], ["Invert", 0.6482444740361704, 0.48256237896163945]],
        [["Rotate", 0.4931329446923608, 0.037076242417301675], ["Contrast", 0.9097939772412852, 0.5619594905306389]],
        [["Posterize", 0.7311032479626216, 0.4796364593912915], ["Color", 0.13912123993932402, 0.03997286439663705]],
        [["AutoContrast", 0.6196602944085344, 0.2531430457527588], ["Rotate", 0.5583937060431972, 0.9893379795224023]],
        [["AutoContrast", 0.8847753125072959, 0.19123028952580057],
         ["TranslateY", 0.494361716097206, 0.14232297727461696]], [["Invert", 0.6212360716340707, 0.033898871473033165],
                                                                   ["AutoContrast", 0.30839896957008295,
                                                                    0.23603569542166247]],
        [["Equalize", 0.8255583546605049, 0.613736933157845], ["AutoContrast", 0.6357166629525485, 0.7894617347709095]],
        [["Brightness", 0.33840706322846814, 0.07917167871493658], ["ShearY", 0.15693175752528676, 0.6282773652129153]],
        [["Cutout", 0.7550520024859294, 0.08982367300605598], ["ShearX", 0.5844942417320858, 0.36051195083380105]]]
    return p


def fa_reduced_imagenet():
    p = [[["ShearY", 0.14143816458479197, 0.513124791615952], ["Sharpness", 0.9290316227291179, 0.9788406212603302]],
         [["Color", 0.21502874228385338, 0.3698477943880306], ["TranslateY", 0.49865058747734736, 0.4352676987103321]],
         [["Brightness", 0.6603452126485386, 0.6990174510500261], ["Cutout", 0.7742953773992511, 0.8362550883640804]],
         [["Posterize", 0.5188375788270497, 0.9863648925446865],
          ["TranslateY", 0.8365230108655313, 0.6000972236440252]],
         [["ShearY", 0.9714994964711299, 0.2563663552809896], ["Equalize", 0.8987567223581153, 0.1181761775609772]],
         [["Sharpness", 0.14346409304565366, 0.5342189791746006],
          ["Sharpness", 0.1219714162835897, 0.44746801278319975]],
         [["TranslateX", 0.08089260772173967, 0.028011721602479833],
          ["TranslateX", 0.34767877352421406, 0.45131294688688794]],
         [["Brightness", 0.9191164585327378, 0.5143232242627864], ["Color", 0.9235247849934283, 0.30604586249462173]],
         [["Contrast", 0.4584173187505879, 0.40314219914942756], ["Rotate", 0.550289356406774, 0.38419022293237126]],
         [["Posterize", 0.37046156420799325, 0.052693291117634544], ["Cutout", 0.7597581409366909, 0.7535799791937421]],
         [["Color", 0.42583964114658746, 0.6776641859552079], ["ShearY", 0.2864805671096011, 0.07580175477739545]],
         [["Brightness", 0.5065952125552232, 0.5508640233704984],
          ["Brightness", 0.4760021616081475, 0.3544313318097987]],
         [["Posterize", 0.5169630851995185, 0.9466018906715961], ["Posterize", 0.5390336503396841, 0.1171015788193209]],
         [["Posterize", 0.41153170909576176, 0.7213063942615204], ["Rotate", 0.6232230424824348, 0.7291984098675746]],
         [["Color", 0.06704687234714028, 0.5278429246040438], ["Sharpness", 0.9146652195810183, 0.4581415618941407]],
         [["ShearX", 0.22404644446773492, 0.6508620171913467],
          ["Brightness", 0.06421961538672451, 0.06859528721039095]],
         [["Rotate", 0.29864103693134797, 0.5244313199644495], ["Sharpness", 0.4006161706584276, 0.5203708477368657]],
         [["AutoContrast", 0.5748186910788027, 0.8185482599354216],
          ["Posterize", 0.9571441684265188, 0.1921474117448481]],
         [["ShearY", 0.5214786760436251, 0.8375629059785009], ["Invert", 0.6872393349333636, 0.9307694335024579]],
         [["Contrast", 0.47219838080793364, 0.8228524484275648],
          ["TranslateY", 0.7435518856840543, 0.5888865560614439]],
         [["Posterize", 0.10773482839638836, 0.6597021018893648], ["Contrast", 0.5218466423129691, 0.562985661685268]],
         [["Rotate", 0.4401753067886466, 0.055198255925702475], ["Rotate", 0.3702153509335602, 0.5821574425474759]],
         [["TranslateY", 0.6714729117832363, 0.7145542887432927],
          ["Equalize", 0.0023263758097700205, 0.25837341854887885]],
         [["Cutout", 0.3159707561240235, 0.19539664199170742], ["TranslateY", 0.8702824829864558, 0.5832348977243467]],
         [["AutoContrast", 0.24800812729140026, 0.08017301277245716],
          ["Brightness", 0.5775505849482201, 0.4905904775616114]],
         [["Color", 0.4143517886294533, 0.8445937742921498], ["ShearY", 0.28688910858536587, 0.17539366839474402]],
         [["Brightness", 0.6341134194059947, 0.43683815933640435],
          ["Brightness", 0.3362277685899835, 0.4612826163288225]],
         [["Sharpness", 0.4504035748829761, 0.6698294470467474],
          ["Posterize", 0.9610055612671645, 0.21070714173174876]],
         [["Posterize", 0.19490421920029832, 0.7235798208354267], ["Rotate", 0.8675551331308305, 0.46335565746433094]],
         [["Color", 0.35097958351003306, 0.42199181561523186], ["Invert", 0.914112788087429, 0.44775583211984815]],
         [["Cutout", 0.223575616055454, 0.6328591417299063], ["TranslateY", 0.09269465212259387, 0.5101073959070608]],
         [["Rotate", 0.3315734525975911, 0.9983593458299167], ["Sharpness", 0.12245416662856974, 0.6258689139914664]],
         [["ShearY", 0.696116760180471, 0.6317805202283014], ["Color", 0.847501151593963, 0.4440116609830195]],
         [["Solarize", 0.24945891607225948, 0.7651150206105561], ["Cutout", 0.7229677092930331, 0.12674657348602494]],
         [["TranslateX", 0.43461945065713675, 0.06476571036747841], ["Color", 0.6139316940180952, 0.7376264330632316]],
         [["Invert", 0.1933003530637138, 0.4497819016184308], ["Invert", 0.18391634069983653, 0.3199769100951113]],
         [["Color", 0.20418296626476137, 0.36785101882029814], ["Posterize", 0.624658293920083, 0.8390081535735991]],
         [["Sharpness", 0.5864963540530814, 0.586672446690273], ["Posterize", 0.1980280647652339, 0.222114611452575]],
         [["Invert", 0.3543654961628104, 0.5146369635250309], ["Equalize", 0.40751271919434434, 0.4325310837291978]],
         [["ShearY", 0.22602859359451877, 0.13137880879778158], ["Posterize", 0.7475029061591305, 0.803900538461099]],
         [["Sharpness", 0.12426276165599924, 0.5965912716602046], ["Invert", 0.22603903038966913, 0.4346802001255868]],
         [["TranslateY", 0.010307035630661765, 0.16577665156754046],
          ["Posterize", 0.4114319141395257, 0.829872913683949]],
         [["TranslateY", 0.9353069865746215, 0.5327821671247214], ["Color", 0.16990443486261103, 0.38794866007484197]],
         [["Cutout", 0.1028174322829021, 0.3955952903458266], ["ShearY", 0.4311995281335693, 0.48024695395374734]],
         [["Posterize", 0.1800334334284686, 0.0548749478418862],
          ["Brightness", 0.7545808536793187, 0.7699080551646432]],
         [["Color", 0.48695305373084197, 0.6674269768464615], ["ShearY", 0.4306032279086781, 0.06057690550239343]],
         [["Brightness", 0.4919399683825053, 0.677338905806407],
          ["Brightness", 0.24112708387760828, 0.42761103121157656]],
         [["Posterize", 0.4434818644882532, 0.9489450593207714],
          ["Posterize", 0.40957675116385955, 0.015664946759584186]],
         [["Posterize", 0.41307949855153797, 0.6843276552020272], ["Rotate", 0.8003545094091291, 0.7002300783416026]],
         [["Color", 0.7038570031770905, 0.4697612983649519], ["Sharpness", 0.9700016496081002, 0.25185103545948884]],
         [["AutoContrast", 0.714641656154856, 0.7962423001719023],
          ["Sharpness", 0.2410097684093468, 0.5919171048019731]],
         [["TranslateX", 0.8101567644494714, 0.7156447005337443], ["Solarize", 0.5634727831229329, 0.8875158446846]],
         [["Sharpness", 0.5335258857303261, 0.364743126378182], ["Color", 0.453280875871377, 0.5621962714743068]],
         [["Cutout", 0.7423678127672542, 0.7726370777867049], ["Invert", 0.2806161382641934, 0.6021111986900146]],
         [["TranslateY", 0.15190341320343761, 0.3860373175487939], ["Cutout", 0.9980805818665679, 0.05332384819400854]],
         [["Posterize", 0.36518675678786605, 0.2935819027397963],
          ["TranslateX", 0.26586180351840005, 0.303641300745208]],
         [["Brightness", 0.19994509744377761, 0.90813953707639], ["Equalize", 0.8447217761297836, 0.3449396603478335]],
         [["Sharpness", 0.9294773669936768, 0.999713346583839], ["Brightness", 0.1359744825665662, 0.1658489221872924]],
         [["TranslateX", 0.11456529257659381, 0.9063795878367734],
          ["Equalize", 0.017438134319894553, 0.15776887259743755]],
         [["ShearX", 0.9833726383270114, 0.5688194948373335], ["Equalize", 0.04975615490994345, 0.8078130016227757]],
         [["Brightness", 0.2654654830488695, 0.8989789725280538],
          ["TranslateX", 0.3681535065952329, 0.36433345713161036]],
         [["Rotate", 0.04956524209892327, 0.5371942433238247], ["ShearY", 0.0005527499145153714, 0.56082571605602]],
         [["Rotate", 0.7918337108932019, 0.5906896260060501], ["Posterize", 0.8223967034091191, 0.450216998388943]],
         [["Color", 0.43595106766978337, 0.5253013785221605], ["Sharpness", 0.9169421073531799, 0.8439997639348893]],
         [["TranslateY", 0.20052300197155504, 0.8202662448307549],
          ["Sharpness", 0.2875792108435686, 0.6997181624527842]],
         [["Color", 0.10568089980973616, 0.3349467065132249], ["Brightness", 0.13070947282207768, 0.5757725013960775]],
         [["AutoContrast", 0.3749999712869779, 0.6665578760607657],
          ["Brightness", 0.8101178402610292, 0.23271946112218125]],
         [["Color", 0.6473605933679651, 0.7903409763232029], ["ShearX", 0.588080941572581, 0.27223524148254086]],
         [["Cutout", 0.46293361616697304, 0.7107761001833921],
          ["AutoContrast", 0.3063766931658412, 0.8026114219854579]],
         [["Brightness", 0.7884854981520251, 0.5503669863113797],
          ["Brightness", 0.5832456158675261, 0.5840349298921661]],
         [["Solarize", 0.4157539625058916, 0.9161905834309929], ["Sharpness", 0.30628197221802017, 0.5386291658995193]],
         [["Sharpness", 0.03329610069672856, 0.17066672983670506], ["Invert", 0.9900547302690527, 0.6276238841220477]],
         [["Solarize", 0.551015648982762, 0.6937104775938737], ["Color", 0.8838491591064375, 0.31596634380795385]],
         [["AutoContrast", 0.16224182418148447, 0.6068227969351896],
          ["Sharpness", 0.9599468096118623, 0.4885289719905087]],
         [["TranslateY", 0.06576432526133724, 0.6899544605400214],
          ["Posterize", 0.2177096480169678, 0.9949164789616582]], [["Solarize", 0.529820544480292, 0.7576047224165541],
                                                                   ["Sharpness", 0.027047878909321643,
                                                                    0.45425231553970685]],
         [["Sharpness", 0.9102526010473146, 0.8311987141993857], ["Invert", 0.5191838751826638, 0.6906136644742229]],
         [["Solarize", 0.4762773516008588, 0.7703654263842423], ["Color", 0.8048437792602289, 0.4741523094238038]],
         [["Sharpness", 0.7095055508594206, 0.7047344238075169], ["Sharpness", 0.5059623654132546, 0.6127255499234886]],
         [["TranslateY", 0.02150725921966186, 0.3515764519224378],
          ["Posterize", 0.12482170119714735, 0.7829851754051393]],
         [["Color", 0.7983830079184816, 0.6964694521670339], ["Brightness", 0.3666527856286296, 0.16093151636495978]],
         [["AutoContrast", 0.6724982375829505, 0.536777706678488],
          ["Sharpness", 0.43091754837597646, 0.7363240924241439]],
         [["Brightness", 0.2889770401966227, 0.4556557902380539],
          ["Sharpness", 0.8805303296690755, 0.6262218017754902]],
         [["Sharpness", 0.5341939854581068, 0.6697109101429343], ["Rotate", 0.6806606655137529, 0.4896914517968317]],
         [["Sharpness", 0.5690509737059344, 0.32790632371915096],
          ["Posterize", 0.7951894258661069, 0.08377850335209162]],
         [["Color", 0.6124132978216081, 0.5756485920709012], ["Brightness", 0.33053544654445344, 0.23321841707002083]],
         [["TranslateX", 0.0654795026615917, 0.5227246924310244], ["ShearX", 0.2932320531132063, 0.6732066478183716]],
         [["Cutout", 0.6226071187083615, 0.01009274433736012], ["ShearX", 0.7176799968189801, 0.3758780240463811]],
         [["Rotate", 0.18172339508029314, 0.18099184896819184], ["ShearY", 0.7862658331645667, 0.295658135767252]],
         [["Contrast", 0.4156099177015862, 0.7015784500878446], ["Sharpness", 0.6454135310009, 0.32335858947955287]],
         [["Color", 0.6215885089922037, 0.6882673235388836], ["Brightness", 0.3539881732605379, 0.39486736455795496]],
         [["Invert", 0.8164816716866418, 0.7238192000817796], ["Sharpness", 0.3876355847343607, 0.9870077619731956]],
         [["Brightness", 0.1875628712629315, 0.5068115936257], ["Sharpness", 0.8732419122060423, 0.5028019258530066]],
         [["Sharpness", 0.6140734993408259, 0.6458239834366959], ["Rotate", 0.5250107862824867, 0.533419456933602]],
         [["Sharpness", 0.5710893143725344, 0.15551651073007305], ["ShearY", 0.6548487860151722, 0.021365083044319146]],
         [["Color", 0.7610250354649954, 0.9084452893074055], ["Brightness", 0.6934611792619156, 0.4108071412071374]],
         [["ShearY", 0.07512550098923898, 0.32923768385754293], ["ShearY", 0.2559588911696498, 0.7082337365398496]],
         [["Cutout", 0.5401319018926146, 0.004750568603408445], ["ShearX", 0.7473354415031975, 0.34472481968368773]],
         [["Rotate", 0.02284154583679092, 0.1353450082435801], ["ShearY", 0.8192458031684238, 0.2811653613473772]],
         [["Contrast", 0.21142896718139154, 0.7230739568811746],
          ["Sharpness", 0.6902690582665707, 0.13488436112901683]],
         [["Posterize", 0.21701219600958138, 0.5900695769640687], ["Rotate", 0.7541095031505971, 0.5341162375286219]],
         [["Posterize", 0.5772853064792737, 0.45808311743269936],
          ["Brightness", 0.14366050177823675, 0.4644871239446629]],
         [["Cutout", 0.8951718842805059, 0.4970074074310499], ["Equalize", 0.3863835903119882, 0.9986531042150006]],
         [["Equalize", 0.039411354473938925, 0.7475477254908457],
          ["Sharpness", 0.8741966378291861, 0.7304822679596362]],
         [["Solarize", 0.4908704265218634, 0.5160677350249471], ["Color", 0.24961813832742435, 0.09362352627360726]],
         [["Rotate", 7.870457075154214e-05, 0.8086950025500952],
          ["Solarize", 0.10200484521793163, 0.12312889222989265]],
         [["Contrast", 0.8052564975559727, 0.3403813036543645], ["Solarize", 0.7690158533600184, 0.8234626822018851]],
         [["AutoContrast", 0.680362728854513, 0.9415320040873628],
          ["TranslateY", 0.5305871824686941, 0.8030609611614028]],
         [["Cutout", 0.1748050257378294, 0.06565343731910589], ["TranslateX", 0.1812738872339903, 0.6254461448344308]],
         [["Brightness", 0.4230502644722749, 0.3346463682905031], ["ShearX", 0.19107198973659312, 0.6715789128604919]],
         [["ShearX", 0.1706528684548394, 0.7816570201200446], ["TranslateX", 0.494545185948171, 0.4710810058360291]],
         [["TranslateX", 0.42356251508933324, 0.23865307292867322],
          ["TranslateX", 0.24407503619326745, 0.6013778508137331]],
         [["AutoContrast", 0.7719512185744232, 0.3107905373009763],
          ["ShearY", 0.49448082925617176, 0.5777951230577671]],
         [["Cutout", 0.13026983827940525, 0.30120438757485657], ["Brightness", 0.8857896834516185, 0.7731541459513939]],
         [["AutoContrast", 0.6422800349197934, 0.38637401090264556],
          ["TranslateX", 0.25085431400995084, 0.3170642592664873]],
         [["Sharpness", 0.22336654455367122, 0.4137774852324138], ["ShearY", 0.22446851054920894, 0.518341735882535]],
         [["Color", 0.2597579403253848, 0.7289643913060193], ["Sharpness", 0.5227416670468619, 0.9239943674030637]],
         [["Cutout", 0.6835337711563527, 0.24777620448593812],
          ["AutoContrast", 0.37260245353051846, 0.4840361183247263]],
         [["Posterize", 0.32756602788628375, 0.21185124493743707],
          ["ShearX", 0.25431504951763967, 0.19585996561416225]],
         [["AutoContrast", 0.07930627591849979, 0.5719381348340309],
          ["AutoContrast", 0.335512380071304, 0.4208050118308541]],
         [["Rotate", 0.2924360268257798, 0.5317629242879337], ["Sharpness", 0.4531050021499891, 0.4102650087199528]],
         [["Equalize", 0.5908862210984079, 0.468742362277498], ["Brightness", 0.08571766548550425, 0.5629320703375056]],
         [["Cutout", 0.52751122383816, 0.7287774744737556], ["Equalize", 0.28721628275296274, 0.8075179887475786]],
         [["AutoContrast", 0.24208377391366226, 0.34616549409607644],
          ["TranslateX", 0.17454707403766834, 0.5278055700078459]],
         [["Brightness", 0.5511881924749478, 0.999638675514418], ["Equalize", 0.14076197797220913, 0.2573030693317552]],
         [["ShearX", 0.668731433926434, 0.7564253049646743], ["Color", 0.63235486543845, 0.43954436063340785]],
         [["ShearX", 0.40511960873276237, 0.5710419512142979], ["Contrast", 0.9256769948746423, 0.7461350716211649]],
         [["Cutout", 0.9995917204023061, 0.22908419326246265], ["TranslateX", 0.5440902956629469, 0.9965570051216295]],
         [["Color", 0.22552987172228894, 0.4514558960849747], ["Sharpness", 0.638058150559443, 0.9987829481002615]],
         [["Contrast", 0.5362775837534763, 0.7052133185951871], ["ShearY", 0.220369845547023, 0.7593922994775721]],
         [["ShearX", 0.0317785822935219, 0.775536785253455], ["TranslateX", 0.7939510227015061, 0.5355620618496535]],
         [["Cutout", 0.46027969917602196, 0.31561199122527517], ["Color", 0.06154066467629451, 0.5384660000729091]],
         [["Sharpness", 0.7205483743301113, 0.552222392539886], ["Posterize", 0.5146496404711752, 0.9224333144307473]],
         [["ShearX", 0.00014547730356910538, 0.3553954298642108], ["TranslateY", 0.9625736029090676, 0.57403418640424]],
         [["Posterize", 0.9199917903297341, 0.6690259107633706],
          ["Posterize", 0.0932558110217602, 0.22279303372106138]],
         [["Invert", 0.25401453476874863, 0.3354329544078385], ["Posterize", 0.1832673201325652, 0.4304718799821412]],
         [["TranslateY", 0.02084122674367607, 0.12826181437197323], ["ShearY", 0.655862534043703, 0.3838330909470975]],
         [["Contrast", 0.35231797644104523, 0.3379356652070079], ["Cutout", 0.19685599014304822, 0.1254328595280942]],
         [["Sharpness", 0.18795594984191433, 0.09488678946484895], ["ShearX", 0.33332876790679306, 0.633523782574133]],
         [["Cutout", 0.28267175940290246, 0.7901991550267817], ["Contrast", 0.021200195312951198, 0.4733128702798515]],
         [["ShearX", 0.966231043411256, 0.7700673327786812], ["TranslateX", 0.7102390777763321, 0.12161245817120675]],
         [["Cutout", 0.5183324259533826, 0.30766086003013055], ["Color", 0.48399078150128927, 0.4967477809069189]],
         [["Sharpness", 0.8160855187385873, 0.47937658961644], ["Posterize", 0.46360395447862535, 0.7685454058155061]],
         [["ShearX", 0.10173571421694395, 0.3987290690178754], ["TranslateY", 0.8939980277379345, 0.5669994143735713]],
         [["Posterize", 0.6768089584801844, 0.7113149244621721],
          ["Posterize", 0.054896856043358935, 0.3660837250743921]],
         [["AutoContrast", 0.5915576211896306, 0.33607718177676493],
          ["Contrast", 0.3809408206617828, 0.5712201773913784]],
         [["AutoContrast", 0.012321347472748323, 0.06379072432796573],
          ["Rotate", 0.0017964439160045656, 0.7598026295973337]],
         [["Contrast", 0.6007100085192627, 0.36171972473370206], ["Invert", 0.09553573684975913, 0.12218510774295901]],
         [["AutoContrast", 0.32848604643836266, 0.2619457656206414],
          ["Invert", 0.27082113532501784, 0.9967965642293485]],
         [["AutoContrast", 0.6156282120903395, 0.9422706516080884],
          ["Sharpness", 0.4215509247379262, 0.4063347716503587]],
         [["Solarize", 0.25059210436331264, 0.7215305521159305], ["Invert", 0.1654465185253614, 0.9605851884186778]],
         [["AutoContrast", 0.4464438610980994, 0.685334175815482], ["Cutout", 0.24358625461158645, 0.4699066834058694]],
         [["Rotate", 0.5931657741857909, 0.6813978655574067], ["AutoContrast", 0.9259100547738681, 0.4903201223870492]],
         [["Color", 0.8203976071280751, 0.9777824466585101], ["Posterize", 0.4620669369254169, 0.2738895968716055]],
         [["Contrast", 0.13754352055786848, 0.3369433962088463],
          ["Posterize", 0.48371187792441916, 0.025718004361451302]],
         [["Rotate", 0.5208233630704999, 0.1760188899913535], ["TranslateX", 0.49753461392937226, 0.4142935276250922]],
         [["Cutout", 0.5967418240931212, 0.8028675552639539], ["Cutout", 0.20021854152659121, 0.19426330549590076]],
         [["ShearY", 0.549583567386676, 0.6601326640171705], ["Cutout", 0.6111813470383047, 0.4141935587984994]],
         [["Brightness", 0.6354891977535064, 0.31591459747846745],
          ["AutoContrast", 0.7853952208711621, 0.6555861906702081]],
         [["AutoContrast", 0.7333725370546154, 0.9919410576081586], ["Cutout", 0.9984177877923588, 0.2938253683694291]],
         [["Color", 0.33219296307742263, 0.6378995578424113],
          ["AutoContrast", 0.15432820754183288, 0.7897899838932103]],
         [["Contrast", 0.5905289460222578, 0.8158577207653422], ["Cutout", 0.3980284381203051, 0.43030531250317217]],
         [["TranslateX", 0.452093693346745, 0.5251475931559115], ["Rotate", 0.991422504871258, 0.4556503729269001]],
         [["Color", 0.04560406292983776, 0.061574671308480766],
          ["Brightness", 0.05161079440128734, 0.6718398142425688]],
         [["Contrast", 0.02913302416506853, 0.14402056093217708], ["Rotate", 0.7306930378774588, 0.47088249057922094]],
         [["Solarize", 0.3283072384190169, 0.82680847744367], ["Invert", 0.21632614168418854, 0.8792241691482687]],
         [["Equalize", 0.4860808352478527, 0.9440534949023064], ["Cutout", 0.31395897639184694, 0.41805859306017523]],
         [["Rotate", 0.2816043232522335, 0.5451282807926706], ["Color", 0.7388520447173302, 0.7706503658143311]],
         [["Color", 0.9342776719536201, 0.9039981381514299], ["Rotate", 0.6646389177840164, 0.5147917008383647]],
         [["Cutout", 0.08929430082050335, 0.22416445996932374], ["Posterize", 0.454485751267457, 0.500958345348237]],
         [["TranslateX", 0.14674201106374488, 0.7018633472428202],
          ["Sharpness", 0.6128796723832848, 0.743535235614809]],
         [["TranslateX", 0.5189900164469432, 0.6491132403587601],
          ["Contrast", 0.26309555778227806, 0.5976857969656114]],
         [["Solarize", 0.23569808291972655, 0.3315781686591778], ["ShearY", 0.07292078937544964, 0.7460326987587573]],
         [["ShearY", 0.7090542757477153, 0.5246437008439621], ["Sharpness", 0.9666919148538443, 0.4841687888767071]],
         [["Solarize", 0.3486952615189488, 0.7012877201721799], ["Invert", 0.1933387967311534, 0.9535472742828175]],
         [["AutoContrast", 0.5393460721514914, 0.6924005011697713],
          ["Cutout", 0.16988156769247176, 0.3667207571712882]],
         [["Rotate", 0.5815329514554719, 0.5390406879316949], ["AutoContrast", 0.7370538341589625, 0.7708822194197815]],
         [["Color", 0.8463701017918459, 0.9893491045831084], ["Invert", 0.06537367901579016, 0.5238468509941635]],
         [["Contrast", 0.8099771812443645, 0.39371603893945184],
          ["Posterize", 0.38273629875646487, 0.46493786058573966]],
         [["Color", 0.11164686537114032, 0.6771450570033168], ["Posterize", 0.27921361289661406, 0.7214300893597819]],
         [["Contrast", 0.5958265906571906, 0.5963959447666958], ["Sharpness", 0.2640889223630885, 0.3365870842641453]],
         [["Color", 0.255634146724125, 0.5610029792926452], ["ShearY", 0.7476893976084721, 0.36613194760395557]],
         [["ShearX", 0.2167581882130063, 0.022978065071245002], ["TranslateX", 0.1686864409720319, 0.4919575435512007]],
         [["Solarize", 0.10702753776284957, 0.3954707963684698], ["Contrast", 0.7256100635368403, 0.48845259655719686]],
         [["Sharpness", 0.6165615058519549, 0.2624079463213861], ["ShearX", 0.3804820351860919, 0.4738994677544202]],
         [["TranslateX", 0.18066394808448177, 0.8174509422318228],
          ["Solarize", 0.07964569396290502, 0.45495935736800974]],
         [["Sharpness", 0.2741884021129658, 0.9311045302358317], ["Cutout", 0.0009101326429323388, 0.5932102256756948]],
         [["Rotate", 0.8501796375826188, 0.5092564038282137], ["Brightness", 0.6520146983999912, 0.724091283316938]],
         [["Brightness", 0.10079744898900078, 0.7644088017429471],
          ["AutoContrast", 0.33540215138213575, 0.1487538541758792]],
         [["ShearY", 0.10632545944757177, 0.9565164562996977], ["Rotate", 0.275833816849538, 0.6200731548023757]],
         [["Color", 0.6749819274397422, 0.41042188598168844],
          ["AutoContrast", 0.22396590966461932, 0.5048018491863738]],
         [["Equalize", 0.5044277111650255, 0.2649182381110667],
          ["Brightness", 0.35715133289571355, 0.8653260893016869]],
         [["Cutout", 0.49083594426355326, 0.5602781291093129], ["Posterize", 0.721795488514384, 0.5525847430754974]],
         [["Sharpness", 0.5081835448947317, 0.7453323423804428],
          ["TranslateX", 0.11511932212234266, 0.4337766796030984]],
         [["Solarize", 0.3817050641766593, 0.6879004573473403], ["Invert", 0.0015041436267447528, 0.9793134066888262]],
         [["AutoContrast", 0.5107410439697935, 0.8276720355454423],
          ["Cutout", 0.2786270701864015, 0.43993387208414564]],
         [["Rotate", 0.6711202569428987, 0.6342930903972932], ["Posterize", 0.802820231163559, 0.42770002619222053]],
         [["Color", 0.9426854321337312, 0.9055431782458764], ["AutoContrast", 0.3556422423506799, 0.2773922428787449]],
         [["Contrast", 0.10318991257659992, 0.30841372533347416],
          ["Posterize", 0.4202264962677853, 0.05060395018085634]],
         [["Invert", 0.549305630337048, 0.886056156681853], ["Cutout", 0.9314157033373055, 0.3485836940307909]],
         [["ShearX", 0.5642891775895684, 0.16427372934801418], ["Invert", 0.228741164726475, 0.5066345406806475]],
         [["ShearY", 0.5813123201003086, 0.33474363490586106], ["Equalize", 0.11803439432255824, 0.8583936440614798]],
         [["Sharpness", 0.1642809706111211, 0.6958675237301609], ["ShearY", 0.5989560762277414, 0.6194018060415276]],
         [["Rotate", 0.05092104774529638, 0.9358045394527796], ["Cutout", 0.6443254331615441, 0.28548414658857657]],
         [["Brightness", 0.6986036769232594, 0.9618046340942727],
          ["Sharpness", 0.5564490243465492, 0.6295231286085622]],
         [["Brightness", 0.42725649792574105, 0.17628028916784244],
          ["Equalize", 0.4425109360966546, 0.6392872650036018]],
         [["ShearY", 0.5758622795525444, 0.8773349286588288], ["ShearX", 0.038525646435423666, 0.8755366512394268]],
         [["Sharpness", 0.3704459924265827, 0.9236361456197351], ["Color", 0.6379842432311235, 0.4548767717224531]],
         [["Contrast", 0.1619523824549347, 0.4506528800882731],
          ["AutoContrast", 0.34513874426188385, 0.3580290330996726]],
         [["Contrast", 0.728699731513527, 0.6932238009822878], ["Brightness", 0.8602917375630352, 0.5341445123280423]],
         [["Equalize", 0.3574552353044203, 0.16814745124536548], ["Rotate", 0.24191717169379262, 0.3279497108179034]],
         [["ShearY", 0.8567478695576244, 0.37746117240238164], ["ShearX", 0.9654125389830487, 0.9283047610798827]],
         [["ShearY", 0.4339052480582405, 0.5394548246617406], ["Cutout", 0.5070570647967001, 0.7846286976687882]],
         [["AutoContrast", 0.021620100406875065, 0.44425839772845227],
          ["AutoContrast", 0.33978157614075183, 0.47716564815092244]],
         [["Contrast", 0.9727600659025666, 0.6651758819229426],
          ["Brightness", 0.9893133904996626, 0.39176397622636105]],
         [["Equalize", 0.283428620586305, 0.18727922861893637], ["Rotate", 0.3556063466797136, 0.3722839913107821]],
         [["ShearY", 0.7276172841941864, 0.4834188516302227], ["ShearX", 0.010783217950465884, 0.9756458772142235]],
         [["ShearY", 0.2901753295101581, 0.5684700238749064], ["Cutout", 0.655585564610337, 0.9490071307790201]],
         [["AutoContrast", 0.008507193981450278, 0.4881150103902877],
          ["AutoContrast", 0.6561989723231185, 0.3715071329838596]],
         [["Contrast", 0.7702505530948414, 0.6961371266519999], ["Brightness", 0.9953051630261895, 0.3861962467326121]],
         [["Equalize", 0.2805270012472756, 0.17715406116880994], ["Rotate", 0.3111256593947474, 0.15824352183820073]],
         [["Brightness", 0.9888680802094193, 0.4856236485253163], ["ShearX", 0.022370252047332284, 0.9284975906226682]],
         [["ShearY", 0.4065719044318099, 0.7468528006921563],
          ["AutoContrast", 0.19494427109708126, 0.8613186475174786]],
         [["AutoContrast", 0.023296727279367765, 0.9170949567425306],
          ["AutoContrast", 0.11663051100921168, 0.7908646792175343]],
         [["AutoContrast", 0.7335191671571732, 0.4958357308292425], ["Color", 0.7964964008349845, 0.4977687544324929]],
         [["ShearX", 0.19905221600021472, 0.3033081933150046], ["Equalize", 0.9383410219319321, 0.3224669877230161]],
         [["ShearX", 0.8265450331466404, 0.6509091423603757], ["Sharpness", 0.7134181178748723, 0.6472835976443643]],
         [["ShearY", 0.46962439525486044, 0.223433110541722], ["Rotate", 0.7749806946212373, 0.5337060376916906]],
         [["Posterize", 0.1652499695106796, 0.04860659068586126],
          ["Brightness", 0.6644577712782511, 0.4144528269429337]],
         [["TranslateY", 0.6220449565731829, 0.4917495676722932],
          ["Posterize", 0.6255000355409635, 0.8374266890984867]],
         [["AutoContrast", 0.4887160797052227, 0.7106426020530529],
          ["Sharpness", 0.7684218571497236, 0.43678474722954763]],
         [["Invert", 0.13178101535845366, 0.8301141976359813], ["Color", 0.002820877424219378, 0.49444413062487075]],
         [["TranslateX", 0.9920683666478188, 0.5862245842588877],
          ["Posterize", 0.5536357075855376, 0.5454300367281468]],
         [["Brightness", 0.8150181219663427, 0.1411060258870707], ["Sharpness", 0.8548823004164599, 0.77008691072314]],
         [["Brightness", 0.9580478020413399, 0.7198667636628974], ["ShearY", 0.8431585033377366, 0.38750016565010803]],
         [["Solarize", 0.2331505347152334, 0.25754361489084787], ["TranslateY", 0.447431373734262, 0.5782399531772253]],
         [["TranslateY", 0.8904927998691309, 0.25872872455072315],
          ["AutoContrast", 0.7129888139716263, 0.7161603231650524]],
         [["ShearY", 0.6336216800247362, 0.5247508616674911], ["Cutout", 0.9167315119726633, 0.2060557387978919]],
         [["ShearX", 0.001661782345968199, 0.3682225725445044], ["Solarize", 0.12303352043754572, 0.5014989548584458]],
         [["Brightness", 0.9723625105116246, 0.6555444729681099], ["Contrast", 0.5539208721135375, 0.7819973409318487]],
         [["Equalize", 0.3262607499912611, 0.0006745572802121513],
          ["Contrast", 0.35341551623767103, 0.36814689398886347]],
         [["ShearY", 0.7478539900243613, 0.37322078030129185], ["TranslateX", 0.41558847793529247, 0.7394615158544118]],
         [["Invert", 0.13735541232529067, 0.5536403864332143], ["Cutout", 0.5109718190377135, 0.0447509485253679]],
         [["AutoContrast", 0.09403602327274725, 0.5909250807862687], ["ShearY", 0.53234060616395, 0.5316981359469398]],
         [["ShearX", 0.5651922367876323, 0.6794110241313183], ["Posterize", 0.7431624856363638, 0.7896861463783287]],
         [["Brightness", 0.30949179379286806, 0.7650569096019195],
          ["Sharpness", 0.5461629122105034, 0.6814369444005866]],
         [["Sharpness", 0.28459340191768434, 0.7802208350806028], ["Rotate", 0.15097973114238117, 0.5259683294104645]],
         [["ShearX", 0.6430803693700531, 0.9333735880102375], ["Contrast", 0.7522209520030653, 0.18831747966185058]],
         [["Contrast", 0.4219455937915647, 0.29949769435499646], ["Color", 0.6925322933509542, 0.8095523885795443]],
         [["ShearX", 0.23553236193043048, 0.17966207900468323],
          ["AutoContrast", 0.9039700567886262, 0.21983629944639108]],
         [["ShearX", 0.19256223146671514, 0.31200739880443584], ["Sharpness", 0.31962196883294713, 0.6828107668550425]],
         [["Cutout", 0.5947690279080912, 0.21728220253899178], ["Rotate", 0.6757188879871141, 0.489460599679474]],
         [["ShearY", 0.18365897125470526, 0.3988571115918058], ["Brightness", 0.7727489489504, 0.4790369956329955]],
         [["Contrast", 0.7090301084131432, 0.5178303607560537], ["ShearX", 0.16749258277688506, 0.33061773301592356]],
         [["ShearX", 0.3706690885419934, 0.38510677124319415],
          ["AutoContrast", 0.8288356276501032, 0.16556487668770264]],
         [["TranslateY", 0.16758043046445614, 0.30127092823893986],
          ["Brightness", 0.5194636577132354, 0.6225165310621702]],
         [["Cutout", 0.6087289363049726, 0.10439287037803044], ["Rotate", 0.7503452083033819, 0.7425316019981433]],
         [["ShearY", 0.24347189588329932, 0.5554979486672325], ["Brightness", 0.9468115239174161, 0.6132449358023568]],
         [["Brightness", 0.7144508395807994, 0.4610594769966929], ["ShearX", 0.16466683833092968, 0.3382903812375781]],
         [["Sharpness", 0.27743648684265465, 0.17200038071656915], ["Color", 0.47404262107546236, 0.7868991675614725]],
         [["Sharpness", 0.8603993513633618, 0.324604728411791], ["TranslateX", 0.3331597130403763, 0.9369586812977804]],
         [["Color", 0.1535813630595832, 0.4700116846558207], ["Color", 0.5435647971896318, 0.7639291483525243]],
         [["Brightness", 0.21486188101947656, 0.039347277341450576],
          ["Cutout", 0.7069526940684954, 0.39273934115015696]],
         [["ShearY", 0.7267130888840517, 0.6310800726389485], ["AutoContrast", 0.662163190824139, 0.31948540372237766]],
         [["ShearX", 0.5123132117185981, 0.1981015909438834],
          ["AutoContrast", 0.9009347363863067, 0.26790399126924036]],
         [["Brightness", 0.24245061453231648, 0.2673478678291436], ["ShearX", 0.31707976089283946, 0.6800582845544948]],
         [["Cutout", 0.9257780138367764, 0.03972673526848819], ["Rotate", 0.6807858944518548, 0.46974332280612097]],
         [["ShearY", 0.1543443071262312, 0.6051682587030671], ["Brightness", 0.9758203119828304, 0.4941406868162414]],
         [["Contrast", 0.07578049236491124, 0.38953819133407647], ["ShearX", 0.20194918288164293, 0.4141510791947318]],
         [["Color", 0.27826402243792286, 0.43517491081531157],
          ["AutoContrast", 0.6159269026143263, 0.2021846783488046]],
         [["AutoContrast", 0.5039377966534692, 0.19241507605941105],
          ["Invert", 0.5563931144385394, 0.7069728937319112]],
         [["Sharpness", 0.19031632433810566, 0.26310171056096743], ["Color", 0.4724537593175573, 0.6715201448387876]],
         [["ShearY", 0.2280910467786642, 0.33340559088059313], ["ShearY", 0.8858560034869303, 0.2598627441471076]],
         [["ShearY", 0.07291814128021593, 0.5819462692986321], ["Cutout", 0.27605696060512147, 0.9693427371868695]],
         [["Posterize", 0.4249871586563321, 0.8256952014328607],
          ["Posterize", 0.005907466926447169, 0.8081353382152597]],
         [["Brightness", 0.9071305290601128, 0.4781196213717954],
          ["Posterize", 0.8996214311439275, 0.5540717376630279]],
         [["Brightness", 0.06560728936236392, 0.9920627849065685],
          ["TranslateX", 0.04530789794044952, 0.5318568944702607]],
         [["TranslateX", 0.6800263601084814, 0.4611536772507228], ["Rotate", 0.7245888375283157, 0.0914772551375381]],
         [["Sharpness", 0.879556061897963, 0.42272481462067535],
          ["TranslateX", 0.4600350422524085, 0.5742175429334919]],
         [["AutoContrast", 0.5005776243176145, 0.22597121331684505],
          ["Invert", 0.10763286370369299, 0.6841782704962373]], [["Sharpness", 0.7422908472000116, 0.6850324203882405],
                                                                 ["TranslateX", 0.3832914614128403,
                                                                  0.34798646673324896]],
         [["ShearY", 0.31939465302679326, 0.8792088167639516], ["Brightness", 0.4093604352811235, 0.21055483197261338]],
         [["AutoContrast", 0.7447595860998638, 0.19280222555998586],
          ["TranslateY", 0.317754779431227, 0.9983454520593591]],
         [["Equalize", 0.27706973689750847, 0.6447455020660622], ["Contrast", 0.5626579126863761, 0.7920049962776781]],
         [["Rotate", 0.13064369451773816, 0.1495367590684905], ["Sharpness", 0.24893941981801215, 0.6295943894521504]],
         [["ShearX", 0.6856269993063254, 0.5167938584189854], ["Sharpness", 0.24835352574609537, 0.9990550493102627]],
         [["AutoContrast", 0.461654115871693, 0.43097388896245004], ["Cutout", 0.366359682416437, 0.08011826474215511]],
         [["AutoContrast", 0.993892672935951, 0.2403608711236933], ["ShearX", 0.6620817870694181, 0.1744814077869482]],
         [["ShearY", 0.6396747719986443, 0.15031017143644265], ["Brightness", 0.9451954879495629, 0.26490678840264714]],
         [["Color", 0.19311480787397262, 0.15712300697448575], ["Posterize", 0.05391448762015258, 0.6943963643155474]],
         [["Sharpness", 0.6199669674684085, 0.5412492335319072], ["Invert", 0.14086213450149815, 0.2611850277919339]],
         [["Posterize", 0.5533129268803405, 0.5332478159319912], ["ShearX", 0.48956244029096635, 0.09223930853562916]],
         [["ShearY", 0.05871590849449765, 0.19549715278943228],
          ["TranslateY", 0.7208521362741379, 0.36414003004659434]],
         [["ShearY", 0.7316263417917531, 0.0629747985768501], ["Contrast", 0.036359793501448245, 0.48658745414898386]],
         [["Rotate", 0.3301497610942963, 0.5686622043085637], ["ShearX", 0.40581487555676843, 0.5866127743850192]],
         [["ShearX", 0.6679039628249283, 0.5292270693200821], ["Sharpness", 0.25901391739310703, 0.9778360586541461]],
         [["AutoContrast", 0.27373222012596854, 0.14456771405730712],
          ["Contrast", 0.3877220783523938, 0.7965158941894336]],
         [["Solarize", 0.29440905483979096, 0.06071633809388455],
          ["Equalize", 0.5246736285116214, 0.37575084834661976]],
         [["TranslateY", 0.2191269464520395, 0.7444942293988484],
          ["Posterize", 0.3840878524812771, 0.31812671711741247]],
         [["Solarize", 0.25159267140731356, 0.5833264622559661],
          ["Brightness", 0.07552262572348738, 0.33210648549288435]],
         [["AutoContrast", 0.9770099298399954, 0.46421915310428197],
          ["AutoContrast", 0.04707358934642503, 0.24922048012183493]],
         [["Cutout", 0.5379685806621965, 0.02038212605928355], ["Brightness", 0.5900728303717965, 0.28807872931416956]],
         [["Sharpness", 0.11596624872886108, 0.6086947716949325],
          ["AutoContrast", 0.34876470059667525, 0.22707897759730578]],
         [["Contrast", 0.276545513135698, 0.8822580384226156], ["Rotate", 0.04874027684061846, 0.6722214281612163]],
         [["ShearY", 0.595839851757025, 0.4389866852785822], ["Equalize", 0.5225492356128832, 0.2735290854063459]],
         [["Sharpness", 0.9918029636732927, 0.9919926583216121],
          ["Sharpness", 0.03672376137997366, 0.5563865980047012]],
         [["AutoContrast", 0.34169589759999847, 0.16419911552645738],
          ["Invert", 0.32995953043129234, 0.15073174739720568]],
         [["Posterize", 0.04600255098477292, 0.2632612790075844],
          ["TranslateY", 0.7852153329831825, 0.6990722310191976]],
         [["AutoContrast", 0.4414653815356372, 0.2657468780017082],
          ["Posterize", 0.30647061536763337, 0.3688222724948656]],
         [["Contrast", 0.4239361091421837, 0.6076562806342001], ["Cutout", 0.5780707784165284, 0.05361325256745192]],
         [["Sharpness", 0.7657895907855394, 0.9842407321667671], ["Sharpness", 0.5416352696151596, 0.6773681575200902]],
         [["AutoContrast", 0.13967381098331305, 0.10787258006315015],
          ["Posterize", 0.5019536507897069, 0.9881978222469807]],
         [["Brightness", 0.030528346448984903, 0.31562058762552847],
          ["TranslateY", 0.0843808140595676, 0.21019213305350526]],
         [["AutoContrast", 0.6934579165006736, 0.2530484168209199],
          ["Rotate", 0.0005751408130693636, 0.43790043943210005]],
         [["TranslateX", 0.611258547664328, 0.25465240215894935],
          ["Sharpness", 0.5001446909868196, 0.36102204109889413]],
         [["Contrast", 0.8995127327150193, 0.5493190695343996], ["Brightness", 0.242708780669213, 0.5461116653329015]],
         [["AutoContrast", 0.3751825351022747, 0.16845985803896962],
          ["Cutout", 0.25201103287363663, 0.0005893331783358435]],
         [["ShearX", 0.1518985779435941, 0.14768180777304504], ["Color", 0.85133530274324, 0.4006641163378305]],
         [["TranslateX", 0.5489668255504668, 0.4694591826554948], ["Rotate", 0.1917354490155893, 0.39993269385802177]],
         [["ShearY", 0.6689267479532809, 0.34304285013663577], ["Equalize", 0.24133154048883143, 0.279324043138247]],
         [["Contrast", 0.3412544002099494, 0.20217358823930232], ["Color", 0.8606984790510235, 0.14305503544676373]],
         [["Cutout", 0.21656155695311988, 0.5240101349572595], ["Brightness", 0.14109877717636352, 0.2016827341210295]],
         [["Sharpness", 0.24764371218833872, 0.19655480259925423],
          ["Posterize", 0.19460398862039913, 0.4975414350200679]],
         [["Brightness", 0.6071850094982323, 0.7270716448607151], ["Solarize", 0.111786402398499, 0.6325641684614275]],
         [["Contrast", 0.44772949532200856, 0.44267502710695955],
          ["AutoContrast", 0.360117506402693, 0.2623958228760273]],
         [["Sharpness", 0.8888131688583053, 0.936897400764746], ["Sharpness", 0.16080674198274894, 0.5681119841445879]],
         [["AutoContrast", 0.8004456226590612, 0.1788600469525269],
          ["Brightness", 0.24832285390647374, 0.02755350284841604]],
         [["ShearY", 0.06910320102646594, 0.26076407321544054], ["Contrast", 0.8633703022354964, 0.38968514704043056]],
         [["AutoContrast", 0.42306251382780613, 0.6883260271268138],
          ["Rotate", 0.3938724346852023, 0.16740881249086037]],
         [["Contrast", 0.2725343884286728, 0.6468194318074759], ["Sharpness", 0.32238942646494745, 0.6721149242783824]],
         [["AutoContrast", 0.942093919956842, 0.14675331481712853],
          ["Posterize", 0.5406276708262192, 0.683901182218153]],
         [["Cutout", 0.5386811894643584, 0.04498833938429728], ["Posterize", 0.17007257321724775, 0.45761177118620633]],
         [["Contrast", 0.13599408935104654, 0.53282738083886], ["Solarize", 0.26941667995081114, 0.20958261079465895]],
         [["Color", 0.6600788518606634, 0.9522228302165842], ["Invert", 0.0542722262516899, 0.5152431169321683]],
         [["Contrast", 0.5328934819727553, 0.2376220512388278], ["Posterize", 0.04890422575781711, 0.3182233123739474]],
         [["AutoContrast", 0.9289628064340965, 0.2976678437448435], ["Color", 0.20936893798507963, 0.9649612821434217]],
         [["Cutout", 0.9019423698575457, 0.24002036989728096],
          ["Brightness", 0.48734445615892974, 0.047660899809176316]],
         [["Sharpness", 0.09347824275711591, 0.01358686275590612],
          ["Posterize", 0.9248539660538934, 0.4064232632650468]],
         [["Brightness", 0.46575675383704634, 0.6280194775484345],
          ["Invert", 0.17276207634499413, 0.21263495428839635]],
         [["Brightness", 0.7238014711679732, 0.6178946027258592],
          ["Equalize", 0.3815496086340364, 0.07301281068847276]],
         [["Contrast", 0.754557393588416, 0.895332753570098], ["Color", 0.32709957750707447, 0.8425486003491515]],
         [["Rotate", 0.43406698081696576, 0.28628263254953723],
          ["TranslateY", 0.43949548709125374, 0.15927082198238685]],
         [["Brightness", 0.0015838339831640708, 0.09341692553352654],
          ["AutoContrast", 0.9113966907329718, 0.8345900469751112]],
         [["ShearY", 0.46698796308585017, 0.6150701348176804], ["Invert", 0.14894062704815722, 0.2778388046184728]],
         [["Color", 0.30360499169455957, 0.995713092016834], ["Contrast", 0.2597016288524961, 0.8654420870658932]],
         [["Brightness", 0.9661642031891435, 0.7322006407169436],
          ["TranslateY", 0.4393502786333408, 0.33934762664274265]],
         [["Color", 0.9323638351992302, 0.912776309755293], ["Brightness", 0.1618274755371618, 0.23485741708056307]],
         [["Color", 0.2216470771158821, 0.3359240197334976], ["Sharpness", 0.6328691811471494, 0.6298393874452548]],
         [["Solarize", 0.4772769142265505, 0.7073470698713035], ["ShearY", 0.2656114148206966, 0.31343097010487253]],
         [["Solarize", 0.3839017339304234, 0.5985505779429036],
          ["Equalize", 0.002412059429196589, 0.06637506181196245]],
         [["Contrast", 0.12751196553017863, 0.46980311434237976],
          ["Sharpness", 0.3467487455865491, 0.4054907610444406]],
         [["AutoContrast", 0.9321813669127206, 0.31328471589533274],
          ["Rotate", 0.05801738717432747, 0.36035756254444273]],
         [["TranslateX", 0.52092390458353, 0.5261722561643886], ["Contrast", 0.17836804476171306, 0.39354333443158535]],
         [["Posterize", 0.5458100909925713, 0.49447244994482603],
          ["Brightness", 0.7372536822363605, 0.5303409097463796]],
         [["Solarize", 0.1913974941725724, 0.5582966653986761], ["Equalize", 0.020733669175727026, 0.9377467166472878]],
         [["Equalize", 0.16265732137763889, 0.5206282340874929], ["Sharpness", 0.2421533133595281, 0.506389065871883]],
         [["AutoContrast", 0.9787324801448523, 0.24815051941486466],
          ["Rotate", 0.2423487151245957, 0.6456493129745148]], [["TranslateX", 0.6809867726670327, 0.6949687002397612],
                                                                ["Contrast", 0.16125673359747458, 0.7582679978218987]],
         [["Posterize", 0.8212000950994955, 0.5225012157831872],
          ["Brightness", 0.8824891856626245, 0.4499216779709508]],
         [["Solarize", 0.12061313332505218, 0.5319371283368052], ["Equalize", 0.04120865969945108, 0.8179402157299602]],
         [["Rotate", 0.11278256686005855, 0.4022686554165438], ["ShearX", 0.2983451019112792, 0.42782525461812604]],
         [["ShearY", 0.8847385513289983, 0.5429227024179573], ["Rotate", 0.21316428726607445, 0.6712120087528564]],
         [["TranslateX", 0.46448081241068717, 0.4746090648963252],
          ["Brightness", 0.19973580961271142, 0.49252862676553605]],
         [["Posterize", 0.49664100539481526, 0.4460713166484651],
          ["Brightness", 0.6629559985581529, 0.35192346529003693]],
         [["Color", 0.22710733249173676, 0.37943185764616194], ["ShearX", 0.015809774971472595, 0.8472080190835669]],
         [["Contrast", 0.4187366322381491, 0.21621979869256666],
          ["AutoContrast", 0.7631045030367304, 0.44965231251615134]],
         [["Sharpness", 0.47240637876720515, 0.8080091811749525], ["Cutout", 0.2853425420104144, 0.6669811510150936]],
         [["Posterize", 0.7830320527127324, 0.2727062685529881], ["Solarize", 0.527834000867504, 0.20098218845222998]],
         [["Contrast", 0.366380535288225, 0.39766001659663075], ["Cutout", 0.8708808878088891, 0.20669525734273086]],
         [["ShearX", 0.6815427281122932, 0.6146858582671569], ["AutoContrast", 0.28330622372053493, 0.931352024154997]],
         [["AutoContrast", 0.8668174463154519, 0.39961453880632863],
          ["AutoContrast", 0.5718557712359253, 0.6337062930797239]],
         [["ShearY", 0.8923152519411871, 0.02480062504737446], ["Cutout", 0.14954159341231515, 0.1422219808492364]],
         [["Rotate", 0.3733718175355636, 0.3861928572224287], ["Sharpness", 0.5651126520194574, 0.6091103847442831]],
         [["Posterize", 0.8891714191922857, 0.29600154265251016],
          ["TranslateY", 0.7865351723963945, 0.5664998548985523]],
         [["TranslateX", 0.9298214806998273, 0.729856565052017],
          ["AutoContrast", 0.26349082482341846, 0.9638882609038888]],
         [["Sharpness", 0.8387378377527128, 0.42146721129032494],
          ["AutoContrast", 0.9860522000876452, 0.4200699464169384]],
         [["ShearY", 0.019609159303115145, 0.37197835936879514], ["Cutout", 0.22199340461754258, 0.015932573201085848]],
         [["Rotate", 0.43871085583928443, 0.3283504258860078], ["Sharpness", 0.6077702068037776, 0.6830305349618742]],
         [["Contrast", 0.6160211756538094, 0.32029451083389626], ["Cutout", 0.8037631428427006, 0.4025688837399259]],
         [["TranslateY", 0.051637820936985435, 0.6908417834391846],
          ["Sharpness", 0.7602756948473368, 0.4927111506643095]],
         [["Rotate", 0.4973618638052235, 0.45931479729281227], ["TranslateY", 0.04701789716427618, 0.9408779705948676]],
         [["Rotate", 0.5214194592768602, 0.8371249272013652], ["Solarize", 0.17734812472813338, 0.045020798970228315]],
         [["ShearX", 0.7457999920079351, 0.19025612553075893], ["Sharpness", 0.5994846101703786, 0.5665094068864229]],
         [["Contrast", 0.6172655452900769, 0.7811432139704904], ["Cutout", 0.09915620454670282, 0.3963692287596121]],
         [["TranslateX", 0.2650112299235817, 0.7377261946165307],
          ["AutoContrast", 0.5019539734059677, 0.26905046992024506]],
         [["Contrast", 0.6646299821370135, 0.41667784809592945], ["Cutout", 0.9698457154992128, 0.15429001887703997]],
         [["Sharpness", 0.9467079029475773, 0.44906457469098204], ["Cutout", 0.30036908747917396, 0.4766149689663106]],
         [["Equalize", 0.6667517691051055, 0.5014839828447363], ["Solarize", 0.4127890336820831, 0.9578274770236529]],
         [["Cutout", 0.6447384874120834, 0.2868806107728985], ["Cutout", 0.4800990488106021, 0.4757538246206956]],
         [["Solarize", 0.12560195032363236, 0.5557473475801568],
          ["Equalize", 0.019957161871490228, 0.5556797187823773]],
         [["Contrast", 0.12607637375759484, 0.4300633627435161],
          ["Sharpness", 0.3437273670109087, 0.40493203127714417]],
         [["AutoContrast", 0.884353334807183, 0.5880138314357569], ["Rotate", 0.9846032404597116, 0.3591877296622974]],
         [["TranslateX", 0.6862295865975581, 0.5307482119690076],
          ["Contrast", 0.19439251187251982, 0.3999195825722808]],
         [["Posterize", 0.4187641835025246, 0.5008988942651585],
          ["Brightness", 0.6665805605402482, 0.3853288204214253]],
         [["Posterize", 0.4507470690013903, 0.4232437206624681],
          ["TranslateX", 0.6054107416317659, 0.38123828040922203]],
         [["AutoContrast", 0.29562338573283276, 0.35608605102687474],
          ["TranslateX", 0.909954785390274, 0.20098894888066549]],
         [["Contrast", 0.6015278411777212, 0.6049140992035096], ["Cutout", 0.47178713636517855, 0.5333747244651914]],
         [["TranslateX", 0.490851976691112, 0.3829593925141144], ["Sharpness", 0.2716675173824095, 0.5131696240367152]],
         [["Posterize", 0.4190558294646337, 0.39316689077269873], ["Rotate", 0.5018526072725914, 0.295712490156129]],
         [["AutoContrast", 0.29624715560691617, 0.10937329832409388],
          ["Posterize", 0.8770505275992637, 0.43117765012206943]],
         [["Rotate", 0.6649970092751698, 0.47767131373391974], ["ShearX", 0.6257923540490786, 0.6643337040198358]],
         [["Sharpness", 0.5553620705849509, 0.8467799429696928], ["Cutout", 0.9006185811918932, 0.3537270716262]],
         [["ShearY", 0.0007619678283789788, 0.9494591850536303], ["Invert", 0.24267733654007673, 0.7851608409575828]],
         [["Contrast", 0.9730916198112872, 0.404670123321921], ["Sharpness", 0.5923587793251186, 0.7405792404430281]],
         [["Cutout", 0.07393909593373034, 0.44569630026328344], ["TranslateX", 0.2460593252211425, 0.4817527814541055]],
         [["Brightness", 0.31058654119340867, 0.7043749950260936], ["ShearX", 0.7632161538947713, 0.8043681264908555]],
         [["AutoContrast", 0.4352334371415373, 0.6377550087204297],
          ["Rotate", 0.2892714673415678, 0.49521052050510556]],
         [["Equalize", 0.509071051375276, 0.7352913414974414], ["ShearX", 0.5099959429711828, 0.7071566714593619]],
         [["Posterize", 0.9540506532512889, 0.8498853304461906], ["ShearY", 0.28199061357155397, 0.3161715627214629]],
         [["Posterize", 0.6740855359097433, 0.684004694936616], ["Posterize", 0.6816720350737863, 0.9654766942980918]],
         [["Solarize", 0.7149344531717328, 0.42212789795181643], ["Brightness", 0.686601460864528, 0.4263050070610551]],
         [["Cutout", 0.49577164991501, 0.08394890892056037], ["Rotate", 0.5810369852730606, 0.3320732965776973]],
         [["TranslateY", 0.1793755480490623, 0.6006520265468684],
          ["Brightness", 0.3769016576438939, 0.7190746300828186]],
         [["TranslateX", 0.7226363597757153, 0.3847027238123509],
          ["Brightness", 0.7641713191794035, 0.36234003077512544]],
         [["TranslateY", 0.1211227055347106, 0.6693523474608023],
          ["Brightness", 0.13011180247738063, 0.5126647617294864]],
         [["Equalize", 0.1501070550869129, 0.0038548909451806557],
          ["Posterize", 0.8266535939653881, 0.5502199643499207]], [["Sharpness", 0.550624117428359, 0.2023044586648523],
                                                                   ["Brightness", 0.06291556314780017,
                                                                    0.7832635398703937]],
         [["Color", 0.3701578205508141, 0.9051537973590863], ["Contrast", 0.5763972727739397, 0.4905511239739898]],
         [["Rotate", 0.7678527224046323, 0.6723066265307555], ["Solarize", 0.31458533097383207, 0.38329324335154524]],
         [["Brightness", 0.292050127929522, 0.7047582807953063], ["ShearX", 0.040541891910333805, 0.06639328601282746]],
         [["TranslateY", 0.4293891393238555, 0.6608516902234284],
          ["Sharpness", 0.7794685477624004, 0.5168044063408147]],
         [["Color", 0.3682450402286552, 0.17274523597220048], ["ShearY", 0.3936056470397763, 0.5702597289866161]],
         [["Equalize", 0.43436990310624657, 0.9207072627823626], ["Contrast", 0.7608688260846083, 0.4759023148841439]],
         [["Brightness", 0.7926088966143935, 0.8270093925674497], ["ShearY", 0.4924174064969461, 0.47424347505831244]],
         [["Contrast", 0.043917555279430476, 0.15861903591675125], ["ShearX", 0.30439480405505853, 0.1682659341098064]],
         [["TranslateY", 0.5598255583454538, 0.721352536005039], ["Posterize", 0.9700921973303752, 0.6882015184440126]],
         [["AutoContrast", 0.3620887415037668, 0.5958176322317132],
          ["TranslateX", 0.14213781552733287, 0.6230799786459947]],
         [["Color", 0.490366889723972, 0.9863152892045195], ["Color", 0.817792262022319, 0.6755656429452775]],
         [["Brightness", 0.7030707021937771, 0.254633187122679], ["Color", 0.13977318232688843, 0.16378180123959793]],
         [["AutoContrast", 0.2933247831326118, 0.6283663376211102],
          ["Sharpness", 0.85430478154147, 0.9753613184208796]],
         [["Rotate", 0.6674299955457268, 0.48571208708018976], ["Contrast", 0.47491370175907016, 0.6401079552479657]],
         [["Sharpness", 0.37589579644127863, 0.8475131989077025],
          ["TranslateY", 0.9985149867598191, 0.057815729375099975]],
         [["Equalize", 0.0017194373841596389, 0.7888361311461602], ["Contrast", 0.6779293670669408, 0.796851411454113]],
         [["TranslateY", 0.3296782119072306, 0.39765117357271834],
          ["Sharpness", 0.5890554357001884, 0.6318339473765834]],
         [["Posterize", 0.25423810893163856, 0.5400430289894207],
          ["Sharpness", 0.9273643918988342, 0.6480913470982622]],
         [["Cutout", 0.850219975768305, 0.4169812455601289], ["Solarize", 0.5418755745870089, 0.5679666650495466]],
         [["Brightness", 0.008881361977310959, 0.9282562314720516],
          ["TranslateY", 0.7736066471553994, 0.20041167606029642]],
         [["Brightness", 0.05382537581401925, 0.6405265501035952],
          ["Contrast", 0.30484329473639593, 0.5449338155734242]],
         [["Color", 0.613257119787967, 0.4541503912724138], ["Brightness", 0.9061572524724674, 0.4030159294447347]],
         [["Brightness", 0.02739111568942537, 0.006028056532326534],
          ["ShearX", 0.17276751958646486, 0.05967365780621859]],
         [["TranslateY", 0.4376298213047888, 0.7691816164456199],
          ["Sharpness", 0.8162292718857824, 0.6054926462265117]],
         [["Color", 0.37963069679121214, 0.5946919433483344], ["Posterize", 0.08485417284005387, 0.5663580913231766]],
         [["Equalize", 0.49785780226818316, 0.9999137109183761], ["Sharpness", 0.7685879484682496, 0.6260846154212211]],
         [["AutoContrast", 0.4190931409670763, 0.2374852525139795],
          ["Posterize", 0.8797422264608563, 0.3184738541692057]],
         [["Rotate", 0.7307269024632872, 0.41523609600701106], ["ShearX", 0.6166685870692289, 0.647133807748274]],
         [["Sharpness", 0.5633713231039904, 0.8276694754755876], ["Cutout", 0.8329340776895764, 0.42656043027424073]],
         [["ShearY", 0.14934828370884312, 0.8622510773680372], ["Invert", 0.25925989086863277, 0.8813283584888576]],
         [["Contrast", 0.9457071292265932, 0.43228655518614034], ["Sharpness", 0.8485316947644338, 0.7590298998732413]],
         [["AutoContrast", 0.8386103589399184, 0.5859583131318076],
          ["Solarize", 0.466758711343543, 0.9956215363818983]],
         [["Rotate", 0.9387133710926467, 0.19180564509396503], ["Rotate", 0.5558247609706255, 0.04321698692007105]],
         [["ShearX", 0.3608716600695567, 0.15206159451532864], ["TranslateX", 0.47295292905710146, 0.5290760596129888]],
         [["TranslateX", 0.8357685981547495, 0.5991305115727084],
          ["Posterize", 0.5362929404188211, 0.34398525441943373]],
         [["ShearY", 0.6751984031632811, 0.6066293622133011], ["Contrast", 0.4122723990263818, 0.4062467515095566]],
         [["Color", 0.7515349936021702, 0.5122124665429213], ["Contrast", 0.03190514292904123, 0.22903520154660545]],
         [["Contrast", 0.5448962625054385, 0.38655673938910545],
          ["AutoContrast", 0.4867400684894492, 0.3433111101096984]],
         [["Rotate", 0.0008372434310827959, 0.28599951781141714],
          ["Equalize", 0.37113686925530087, 0.5243929348114981]],
         [["Color", 0.720054993488857, 0.2010177651701808], ["TranslateX", 0.23036196506059398, 0.11152764304368781]],
         [["Cutout", 0.859134208332423, 0.6727345740185254], ["ShearY", 0.02159833505865088, 0.46390076266538544]],
         [["Sharpness", 0.3428232157391428, 0.4067874527486514],
          ["Brightness", 0.5409415136577347, 0.3698432231874003]],
         [["Solarize", 0.27303978936454776, 0.9832186173589548], ["ShearY", 0.08831127213044043, 0.4681870331149774]],
         [["TranslateY", 0.2909309268736869, 0.4059460811623174],
          ["Sharpness", 0.6425125139803729, 0.20275737203293587]],
         [["Contrast", 0.32167626214661627, 0.28636162794046977], ["Invert", 0.4712405253509603, 0.7934644799163176]],
         [["Color", 0.867993060896951, 0.96574321666213], ["Color", 0.02233897320328512, 0.44478933557303063]],
         [["AutoContrast", 0.1841254751814967, 0.2779992148017741], ["Color", 0.3586283093530607, 0.3696246850445087]],
         [["Posterize", 0.2052935984046965, 0.16796913860308244], ["ShearX", 0.4807226832843722, 0.11296747254563266]],
         [["Cutout", 0.2016411266364791, 0.2765295444084803], ["Brightness", 0.3054112810424313, 0.695924264931216]],
         [["Rotate", 0.8405872184910479, 0.5434142541450815], ["Cutout", 0.4493615138203356, 0.893453735250007]],
         [["Contrast", 0.8433310507685494, 0.4915423577963278], ["ShearX", 0.22567799557913246, 0.20129892537008834]],
         [["Contrast", 0.045954277103674224, 0.5043900167190442], ["Cutout", 0.5552992473054611, 0.14436447810888237]],
         [["AutoContrast", 0.7719296115130478, 0.4440417544621306],
          ["Sharpness", 0.13992809206158283, 0.7988278670709781]],
         [["Color", 0.7838574233513952, 0.5971351401625151], ["TranslateY", 0.13562290583925385, 0.2253039635819158]],
         [["Cutout", 0.24870301109385806, 0.6937886690381568], ["TranslateY", 0.4033400068952813, 0.06253378991880915]],
         [["TranslateX", 0.0036059390486775644, 0.5234723884081843],
          ["Solarize", 0.42724862530733526, 0.8697702564187633]],
         [["Equalize", 0.5446026737834311, 0.9367992979112202], ["ShearY", 0.5943478903735789, 0.42345889214100046]],
         [["ShearX", 0.18611885697957506, 0.7320849092947314], ["ShearX", 0.3796416430900566, 0.03817761920009881]],
         [["Posterize", 0.37636778506979124, 0.26807924785236537],
          ["Brightness", 0.4317372554383255, 0.5473346211870932]],
         [["Brightness", 0.8100436240916665, 0.3817612088285007],
          ["Brightness", 0.4193974619003253, 0.9685902764026623]],
         [["Contrast", 0.701776402197012, 0.6612786008858009], ["Color", 0.19882787177960912, 0.17275597188875483]],
         [["Color", 0.9538303302832989, 0.48362384535228686], ["ShearY", 0.2179980837345602, 0.37027290936457313]],
         [["TranslateY", 0.6068028691503798, 0.3919346523454841], ["Cutout", 0.8228303342563138, 0.18372280287814613]],
         [["Equalize", 0.016416758802906828, 0.642838949194916], ["Cutout", 0.5761717838655257, 0.7600661153497648]],
         [["Color", 0.9417761826818639, 0.9916074035986558], ["Equalize", 0.2524209308597042, 0.6373703468715077]],
         [["Brightness", 0.75512589439513, 0.6155072321007569], ["Contrast", 0.32413476940254515, 0.4194739830159837]],
         [["Sharpness", 0.3339450765586968, 0.9973297539194967],
          ["AutoContrast", 0.6523930242124429, 0.1053482471037186]],
         [["ShearX", 0.2961391955838801, 0.9870036064904368], ["ShearY", 0.18705025965909403, 0.4550895821154484]],
         [["TranslateY", 0.36956447983807883, 0.36371471767143543],
          ["Sharpness", 0.6860051967688487, 0.2850190720087796]],
         [["Cutout", 0.13017742151902967, 0.47316674150067195], ["Invert", 0.28923829959551883, 0.9295585654924601]],
         [["Contrast", 0.7302368472279086, 0.7178974949876642],
          ["TranslateY", 0.12589674152030433, 0.7485392909494947]],
         [["Color", 0.6474693117772619, 0.5518269515590674], ["Contrast", 0.24643004970708016, 0.3435581358079418]],
         [["Contrast", 0.5650327855750835, 0.4843031798040887], ["Brightness", 0.3526684005761239, 0.3005305004600969]],
         [["Rotate", 0.09822284968122225, 0.13172798244520356], ["Equalize", 0.38135066977857157, 0.5135129123554154]],
         [["Contrast", 0.5902590645585712, 0.2196062383730596], ["ShearY", 0.14188379126120954, 0.1582612142182743]],
         [["Cutout", 0.8529913814417812, 0.89734031211874], ["Color", 0.07293767043078672, 0.32577659205278897]],
         [["Equalize", 0.21401668971453247, 0.040015259500028266], ["ShearY", 0.5126400895338797, 0.4726484828276388]],
         [["Brightness", 0.8269430025954498, 0.9678362841865166], ["ShearY", 0.17142069814830432, 0.4726727848289514]],
         [["Brightness", 0.699707089334018, 0.2795501395789335], ["ShearX", 0.5308818178242845, 0.10581814221896294]],
         [["Equalize", 0.32519644258946145, 0.15763390340309183],
          ["TranslateX", 0.6149090364414208, 0.7454832565718259]],
         [["AutoContrast", 0.5404508567155423, 0.7472387762067986],
          ["Equalize", 0.05649876539221024, 0.5628180219887216]]]
    return p


_IMAGENET_PCA = {
    'eigval': torch.Tensor([0.2175, 0.0188, 0.0045]),
    'eigvec': torch.Tensor([
        [-0.5675, 0.7192, 0.4009],
        [-0.5808, -0.0045, -0.8140],
        [-0.5836, -0.6948, 0.4203],
    ])
}

from torchvision import transforms


def get_default_transform():
    trans = []
    if cfg.AUG.RESIZE[0] > 0 and cfg.AUG.RESIZE[1] > 0:
        trans.append(transforms.Resize(cfg.AUG.RESIZE))
    if cfg.AUG.V_FLIP > 0:
        trans.append(transforms.RandomVerticalFlip(p=cfg.AUG.V_FLIP))
    if cfg.AUG.H_FLIP > 0:
        trans.append(transforms.RandomHorizontalFlip(p=cfg.AUG.H_FLIP))
    if cfg.AUG.ROTATION > 0:
        trans.append(transforms.RandomRotation(cfg.AUG.ROTATION, expand=False))
    if cfg.AUG.BRIGHTNESS > 0 or cfg.AUG.CONTRAST > 0 or cfg.AUG.SATURATION > 0 or cfg.AUG.HUE > 0:
        trans.append(transforms.ColorJitter(brightness=cfg.AUG.BRIGHTNESS,
                                            contrast=cfg.AUG.CONTRAST, saturation=cfg.AUG.SATURATION, hue=cfg.AUG.HUE))
    if cfg.AUG.RND_CROP[0] > 0 and cfg.AUG.RND_CROP[1] > 0:
        trans.append(transforms.RandomCrop(cfg.AUG.RND_CROP))

    trans.append(transforms.ToTensor())
    trans.append(transforms.Normalize(cfg.MEAN, cfg.STD))
    return trans


def get_advanced_augmentation():
    trans = [
        Augmentation(fa_reduced_imagenet()),
        transforms.RandomResizedCrop(cfg.AUG.RND_CROP[0]),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(
            brightness=0.4,
            contrast=0.4,
            saturation=0.4,
            hue=0.2,
        ),
        transforms.ToTensor(),
        transforms.Normalize(cfg.MEAN, cfg.STD),
        # CutoutDefault(C.get()['cutout'])
    ]
    return trans


def get_transform(advance=False):
    if advance:
        return get_advanced_augmentation()
    else:
        return get_default_transform()


class CutoutDefault(object):
    """
    Reference : https://github.com/quark0/darts/blob/master/cnn/utils.py
    """

    def __init__(self, length):
        self.length = length

    def __call__(self, img):
        h, w = img.size(1), img.size(2)
        mask = np.ones((h, w), np.float32)
        y = np.random.randint(h)
        x = np.random.randint(w)

        y1 = np.clip(y - self.length // 2, 0, h)
        y2 = np.clip(y + self.length // 2, 0, h)
        x1 = np.clip(x - self.length // 2, 0, w)
        x2 = np.clip(x + self.length // 2, 0, w)

        mask[y1: y2, x1: x2] = 0.
        mask = torch.from_numpy(mask)
        mask = mask.expand_as(img)
        img *= mask
        return img


class Lighting(object):
    """Lighting noise(AlexNet - style PCA - based noise)"""

    def __init__(self, alphastd, eigval, eigvec):
        self.alphastd = alphastd
        self.eigval = eigval
        self.eigvec = eigvec

    def __call__(self, img):
        if self.alphastd == 0:
            return img

        alpha = img.new().resize_(3).normal_(0, self.alphastd)
        rgb = self.eigvec.type_as(img).clone() \
            .mul(alpha.view(1, 3).expand(3, 3)) \
            .mul(self.eigval.view(1, 3).expand(3, 3)) \
            .sum(1).squeeze()

        return img.add(rgb.view(3, 1, 1).expand_as(img))


class Augmentation(object):
    def __init__(self, policies):
        self.policies = policies

    def __call__(self, img):
        for _ in range(1):
            policy = random.choice(self.policies)
            for name, pr, level in policy:
                if random.random() > pr:
                    continue
                img = apply_augment(img, name, level)
        return img
