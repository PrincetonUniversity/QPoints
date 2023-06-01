rm -rf checkpoints/test
cd scripts
python3 create_snapshot.py --m1 --disk-image ../imgs/ubuntu-arm.img --copy-disk-img --dest-dir ../checkpoints/test
cd ..
