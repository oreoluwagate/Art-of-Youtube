#!/bin/bash
# workbench bootstrap: bash boot.sh  (run detached). outputs -> /mnt/files/sh5/out
set -x
O=/mnt/files/sh5/out; mkdir -p $O
pip install -q imageio-ffmpeg faster-whisper > /dev/null 2>&1
mkdir -p /home/user/bin; ln -sf $(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") /home/user/bin/ffmpeg
export PATH=/home/user/bin:$PATH
cp Poppins-Bold.ttf /home/user/Poppins-Bold.ttf
cd sh5 && python3 setup_wb.py
for n in ${@:-178 179 180 181 182 183 184}; do
  [ -s $O/s$n.mp4 ] && continue
  nice -n 10 python3 ../pipe/vshort.py $n && cp vout/s$n.mp4 $O/s$n.mp4.tmp && mv $O/s$n.mp4.tmp $O/s$n.mp4
done
echo ALLDONE > $O/done.txt
