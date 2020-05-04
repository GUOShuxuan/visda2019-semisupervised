#!/usr/bin/env bash
export NCCL_LL_THRESHOLD=0

CUDA_VISIBLE_DEVICES=0,1,2,3 python -m torch.distributed.launch --nproc_per_node=4 main.py --config ./configs/0917_eff5_real_clipart_no_aug_re_train.yml
