export NCCL_LL_THRESHOLD=0
CUDA_VISIBLE_DEVICES=0,1,2,3 python -m torch.distributed.launch --nproc_per_node=4 main.py --config ./configs/0923_se152_real_painting_no_aug_round_2_v2.yml
