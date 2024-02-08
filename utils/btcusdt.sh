#!/bin/bash

#
# Example script to download spot data from binance.vision
#
duration=10
fmt=+%Y-%m-%d
today=$(date $fmt)
curr=$(date -d "-${duration} days" $fmt) 
while : ; do
  fname="BTCUSDT-4h-${curr}.zip"
  url="https://data.binance.vision/data/spot/daily/klines/BTCUSDT/4h/${fname}"
  if wget --quiet "$url"; then
    unzip -p "$fname"
    rm "$fname"
  fi

  [[ $curr = $today ]] && break

  curr=$(date -d "$curr +1 day" $fmt)
done
