#!/bin/bash

# 获取当前日期作为日志文件名
current_date=$(date +"%Y-%m-%d")
nohup python3 main.py > "nohup_${current_date}.log" 2>&1 &

# 获取进程ID
pid=$!
echo "程序已在后台启动，进程ID: $pid"
echo "可以通过以下命令查看日志："
echo "tail -f nohup_${current_date}.log"
echo "可以通过以下命令停止程序："
echo "kill $pid" 