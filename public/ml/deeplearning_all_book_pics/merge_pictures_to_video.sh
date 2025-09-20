#!/bin/bash

if [ $# -lt 2 ]; then
    echo "用法: $0 <起始编号-结束编号> <输出前缀>"
    exit 1
fi

# 参数格式校验
if [[ ! "$1" =~ ^[0-9]{3}-[0-9]{3}$ ]]; then
    echo "错误：参数格式应为起始编号-结束编号（如：043-046）"
    exit 1
fi

# 解析起始结束编号
start=$((10#${1%-*}))
end=$((10#${1#*-}))

# 校验编号有效性
if [ "$start" -gt "$end" ]; then
    echo "错误：起始编号不能大于结束编号"
    exit 1
fi

# 生成目标目录
target_dir="$start-$end"
mkdir -p "$target_dir" || exit 1

# 生成文件列表并迁移
for ((i=start; i<=end; i++)); do
    filename=$(printf "page_%03d.jpg" "$i")
    if [ ! -f "$filename" ]; then
        echo "错误：文件 $filename 不存在"
        exit 1
    fi
    mv "$filename" "$target_dir/"
done

ffmpeg -framerate 1 -pattern_type glob -i "./${target_dir}/*.jpg" -vf "scale=iw:-2,format=yuv420p" -c:v libx264 -movflags +faststart "${target_dir}/$2.mp4"