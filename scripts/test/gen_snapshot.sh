rm -rf checkpoints/test
cd scripts
python3 create_snapshot.py --disk-image ../imgs/ubuntu-arm.img --copy-disk-img --dest-dir ../checkpoints/test
cd ..

echo A checkpoint is created at checkpoints/test directory
