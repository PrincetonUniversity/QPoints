# QPoints

QPoints is a tool to generate a gem5 compatible checkpoints 
using QEMU. This tool currently works for only ARM system. 
This tool was created to reduce time spent in reaching
a state state of long running applcations.

### Requirements:
1. QEMU
2. Docker
3. Python3
4. A disk image
5. (Optional) ARM Powered Apple Mac system. Needed this only to accelerate emulation.

### Setup:
Obtain a disk image of 64-bit ARM linux distribution and place it imgs directory.

### Steps to create a checkpoint:
1. Launch QEMU emulation using the **run_ubuntu.sh** file
   ```
   bash run_ubuntu.sh
   ```
3. After reaching a steady state invoke the following command to create a checkpoint
   ```
   python create_snapshot.py --m1 --disk-image ../imgs/ubuntu-arm.img --dest-dir ../checkpoints/test
   ```
