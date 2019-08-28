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
# -f 参数判断 $file 是否存在
#if [[ ! -f ${fileName} ]]; then

#fi


for i in ${textList};
do
fileName=${resultDir}/${i}.txt

rm -f ${fileName}
echo touch ${fileName} at `date`
touch ${fileName}
echo  text:${i} '所在工程为:' >> ${fileName}
echo -e '\n' >> ${fileName}

cd ${findDir}
find . -name $3 | tr '\n' '\0' | xargs -0 grep ${i}   -Rw  | grep -v target | awk -F '/' '{print $2}' | sort  | uniq >> ${fileName}

# -e 若字符串中出现以下字符，则特别加以处理，而不会将它当成一般文字输出：
echo -e '\n' >> ${fileName}
echo '开始打印文本:'${i}'所在工程⬇️'
cat ${fileName}
echo 文本${i} '打印完毕'
echo -e '\n'
done