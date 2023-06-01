#!/bin/bash

echo Creating required directories
mkdir checkpoints

echo Please insert a softlin or copy disk image to imgs directory

echo Building Docker image
cd docker
bash docker_build.sh
echo done

echo On Linux host run create_checkpoint.sh script to generate collect a checkpoint
