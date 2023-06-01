set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CUR_DIR=$(pwd)
cd $SCRIPT_DIR
gdown https://drive.google.com/uc?id=1404tFqx5s3yFOFERBUau3epsfChAuyBB
gunzip ubuntu-arm.img.gz 
cd $CUR_DIR
set +x
