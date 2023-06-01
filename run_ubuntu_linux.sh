qemu-system-aarch64 -nographic -machine virt,gic-version=3 -m 16384M -cpu cortex-a57 -smp 1 \
-snapshot \
-serial mon:stdio \
-qmp tcp:localhost:4444,server,nowait -monitor telnet::45454,server,nowait \
-drive file=imgs/ubuntu-arm.img,if=none,id=drive0,cache=writeback -device virtio-blk-device,indirect_desc=false,event_idx=false,drive=drive0,bootindex=0 \
-nic none \
-bios scripts/qemu/QEMU_EFI.fd
#-kernel kernel_arm_built_img -append "root=/dev/vda2 ro  splash quiet" \
#-initrd initrd.img \

