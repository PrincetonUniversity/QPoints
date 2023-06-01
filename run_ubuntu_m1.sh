qemu-system-aarch64 -nographic  -accel hvf -machine virt,highmem=off -m 16G -cpu cortex-a57 -smp 1 \
-serial mon:stdio \
-monitor telnet::45454,server,nowait \
-drive file=imgs/ubuntu-arm.img,if=none,id=drive0,cache=writeback -device virtio-blk-device,indirect_desc=false,event_idx=false,drive=drive0,bootindex=0 \
-nic none \
-bios scripts/qemu/QEMU_EFI.fd
