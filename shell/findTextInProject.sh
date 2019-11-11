#!/bin/bash
#需要查找的文本List,空格分割
textList=$1

findDir=$2
awkDir=${findDir}/
resultDir=${findDir}/../result

#查看是否存在各个文件夹.不存在直接创建
if [[ ! -d "${resultDir}" ]];then
mkdir -p ${resultDir}
fi


##shell参数赋值时候等号左右不要有空格)
grepCmd=''
ignoreCase=$4
if ${ignoreCase}; then
    grepCmd='-i'
    echo '>>>>>>>warning<<<<<<<<'
    echo '此次查找忽略大小写:'${grepCmd}
    echo '>>>>>>>warning<<<<<<<<'
fi
##是否精确查找
exactMatch=$6
if ${exactMatch}; then
    grepCmd=${grepCmd}' -w'
    echo '>>>>>>>warning<<<<<<<<'
    echo '此次查找精确匹配:'${grepCmd}
    echo '>>>>>>>warning<<<<<<<<'
fi

for i in ${textList};
do
###取生成的result文本后缀
txtSuffix=$5
linuxUuidFile=/proc/sys/kernel/random/uuid
# 如果是
# shellcheck disable=SC1034
if [[  -f ${linuxUuidFile} ]]; then
  echo '使用linux自带uuid作为resultFile后缀.'
  txtSuffix=$(cat ${linuxUuidFile})
fi

fileName=${resultDir}/${i}_${txtSuffix}.txt

echo touch ${fileName} at $(date)
touch ${fileName}
echo  text:${i} '所在工程为:' >> ${fileName}
echo -e '\n' >> ${fileName}

cd ${findDir}
## 使用rg https://segmentfault.com/a/1190000016170184
#过滤隐藏文件：find . -not -path '*/\.*'
find . -not -path '*/\.*' -name $3 | tr '\n' '\0' | xargs -0 rg   ${grepCmd}  ${i} | awk -F '/' '{print $2}' | sort  | uniq >> ${fileName}

# -e 若字符串中出现以下字符，则特别加以处理，而不会将它当成一般文字输出：
echo -e '\n' >> ${fileName}
echo '开始打印文本:'${i}'所在工程⬇️'
cat ${fileName}
echo 文本${i} '打印完毕'
echo -e '\n'
rm -f ${fileName}
done