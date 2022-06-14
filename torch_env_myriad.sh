#!/usr/bin/env bash

module unload compilers mpi
module load compilers/gnu/4.9.2
module load python/3.7.4
module load cuda/10.1.243/gnu-4.9.2
module load cudnn/7.5.0.56/cuda-10.1

pip install --no-cache-dir torch=1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
pip install --no-cache-dir git+ssh://git@github.com/$1/$2.git
