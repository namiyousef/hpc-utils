get_gpu_modules () {
  module unload compilers mpi
  module load compilers/gnu/4.9.2
  module load python/3.7.4
  module load cuda/10.1.243/gnu-4.9.2
  module load cudnn/7.5.0.56/cuda-10.1
}

install_torch_gpu () {
  echo "Installing torch version 1.7.1 on cuda 10.1"
  get_gpu_modules

  python3 -m venv $1
  source $1/bin/activate
  pip install --no-cache-dir torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
}

install_library_ssh () {
  pip install --no-cache-dir git+ssh://git@github.com/$1/$2.git@$3
}

prepare_virtualenv () {
  install_torch_gpu $1
  pip install -U pip
  install_library_ssh $2 $3 $4
}
# := will save the variable globally
# :- will not save the variable, but you can specify using local

generate_script_file () {
  local var="${job:=testing}" # NOTE this actually declares the variable outside scope of function, may not be ideal
  echo $var
}


echo "Successfully loaded Myriad Helpers"