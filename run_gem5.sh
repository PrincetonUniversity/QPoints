export M5_PATH=$(pwd)/bin/m5
GEM5_HOME=$(pwd)/gem5
GEM5_CFG=$GEM5_HOME/configs/example/arm/starter_fs.py

TEST=test
CKPT_DIR=$(pwd)/checkpoints/${TEST}

OUTDIR=sim_outs/m5out.$TEST
mkdir -p $OUTDIR
touch ${OUTDIR}

$GEM5_HOME/build/ARM/gem5.opt  --outdir=${OUTDIR} --debug-file=debug.insts  $GEM5_CFG -I 100000000000 --disk-image="${CKPT_DIR}/ubuntu-arm.img" --bootloader="${M5_PATH}/binaries/boot_v2_qemu_virt.arm64" --caches --cpu-type AtomicSimpleCPU --fdip --bp-type TAGE --restore "${CKPT_DIR}" --num-cores 1 -n 1 --mem-size 16384MiB
