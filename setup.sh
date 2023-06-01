#!/bin/bash

echo Creating required directories
mkdir checkpoints

echo cloning gem5 repo
git clone -b cassandra-issue-fix https://github.com/bgodala/gem5_ARM_FDIP.git  gem5

echo Building Docker image
cd docker
bash docker_build.sh
echo done

echo Pull gem5 docker image
docker pull gcr.io/gem5-test/ubuntu-20.04_all-dependencies:v22-1
bash gem5_docker_build.sh
cd ..

echo Getting ARM kernel image files for gem5
cd bin/m5
wget http://dist.gem5.org/dist/v22-0/arm/aarch-system-20220707.tar.bz2
tar -xvf aarch-system-20220707.tar.bz2
cd ../../

echo On Linux host run create_checkpoint.sh script to generate collect a checkpoint
