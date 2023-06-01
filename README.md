# QPoints

QPoints is a tool to generate a gem5 compatible checkpoints 
using QEMU. This tool currently works for only ARM system. 
This tool was created to reduce time spent in reaching
a state state of long running applcations.

### Requirements:
1. QEMU
2. Docker
3. Python3
   - Jinja2 python module
4. gdb-multiarch
5. A disk image
6. (Optional) ARM Powered Apple Mac system. Needed this only to accelerate emulation.

### Setup:
1. Install docker, git, qemu-system packages on your host machine
   ```
   sudo apt-get install git docker qemu-system
   ```
2. Run setup script which sets up directoris and builds a docker image
   ```
   bash setup.sh
   ```
3. Download a disk image from Google Drive. Download script works in docker
   environment. Follow below steps do get the image.
   ```
   bash run_docker.sh
   bash imgs/download_image.sh
   exit
   ```
   After running above set of commands `imgs` folder contains `ubuntu-arm.img` disk image.
   
### Steps to create a checkpoint:
1. Launch QEMU emulation using the `run_ubuntu_linux.sh` file
   ```
   bash run_ubuntu.sh
   ```
2. After reaching a steady state invoke the following command to create a checkpoint
   ```
   bash gen_snapshot.sh
   ```
