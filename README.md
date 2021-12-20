# Entity-Relation-Extraction
Event & Entity Extraction Based on Paddlepaddle. 金融/医疗等领域实体抽取（事件元素抽取）解决方案。

基于ccks2021金融事件元素抽取解决方案，出处可查看博客 [CCKS 2021篇章级事件元素抽取](https://blog.csdn.net/m0_63642362/article/details/121188673)。

## 项目说明
整个项目的运行方式是基于脚本文件`run_event_element_extraction.sh`来实现。
```
# 定义任务
if [ ${process_name} == ccks2lic_data_prepare ]; then
    echo -e "\nstart ${dataset_name} ccks2lic data prepare"
    python ccks2lic.py
    echo -e "end ${dataset_name} ccks2lic data prepare"
elif [ ${process_name} == ccksmed2lic_data_prepare ]; then # add ccksmed2lic.py
    echo -e "\nstart ${dataset_name}ccksmed2lic data prepare"
    python ccksmed2lic.py
    echo -e "end ${dataset_name}ccksmed2lic data prepare"
elif [ ${process_name} == data_prepare ]; then
    echo -e "\nstart ${dataset_name}lic2021 data prepare"
    python data_prepare.py
    echo -e "end ${dataset_name}lic2021 data prepare"
elif [ ${process_name} == role_train ]; then
    echo -e "\nstart ${dataset_name} role train"
    run_sequence_labeling_model role True
    echo -e "end ${dataset_name} role train"
elif [ ${process_name} == role_predict ]; then
    echo -e "\nstart ${dataset_name} role predict"
    run_sequence_labeling_model role False
    echo -e "end ${dataset_name} role predict"
elif [ ${process_name} == get_submit ]; then
    echo -e "\nstart ${dataset_name} predict data merge to submit fotmat"
    python post_process.py
    echo -e "end ${dataset_name} role predict data merge"
else
    echo "no process name ${process_name}"
fi
```

事件元素抽取任务需要从文本中抽取到命名实体以及对应的类型，因此采用了序列标注方案，首先对数据集进行BIO标注处理，然后使用基于基于ERNIE的序列标注方案进行事件元素及其对应类型的识别。

整个流程中，一共定义了5步：
- 数据预处理 
- 模型训练
- 事件元素的预测
- 调整数据输出格式
- 根据实体关系生成三元组

## 运行环境
请参考```requirement.txt```文件。

## 运行命令

运行支持notebook格式，可以在```run_event_element_extract.ipynb```进行运行。

```
# 安装paddlenlp最新版本
!pip install --upgrade paddlenlp

# 
%cd event_element_extract/
...
```

数据格式处理对齐（将数据集转换成LIC2021训练集格式）
```
!bash ./run_event_element_extraction.sh ccksmed2lic_data_prepare # 处理医疗数据集
# !bash ./run_event_element_extraction.sh ccks2lic_data_prepare #处理金融数据集
```

将原始数据预处理成序列标注格式数据（BIO标注）
```
!bash ./run_event_element_extraction.sh data_prepare
```

模型训练（Ernie）
```
!bash run_event_element_extraction.sh role_train
```

测试集事件主体元素预测
```
!bash run_event_element_extraction.sh role_predict
```

将预测结果处理成比赛指定格式
```
!bash run_event_element_extraction.sh get_submit
```

将输出结果根据定义的实体关系进行三元组的转换
```
# 生成三元组
%run 3n_term_extract.py
```





#### 输出数据
给定实体（entity）类型和实体间关系（即类型A实体和类型B实体之间的关系），输出句子中所有满足实体类型约束的实体元素：
```Entity={'type':"疾病和诊断",'entity':"骨髓抑制",start:39,end:43}```

最后根据不同类型实体间所定义的关系，生成三元组：
```
{"entity1": "慢性肾功能不全", "relation": "检验方式", "entity2": "肾穿刺"}
{"entity1": "陈旧右髌骨骨折", "relation": "治疗药物", "entity2": "芬必得"}
```

SPO三元组知识Triples=[(E1, R1, E2), (E1, R1, E2)…]。


### 数据简介
原始数据（训练和验证集）都储存在'./data/ccks/raw'，共分为医疗和金融类数据集，实体相关标注由ccks2021比赛举办方提供。

医疗比赛数据：[医疗命名实体识别子任务一 医疗命名实体识别](https://www.biendata.xyz/competition/ccks_2019_1/)

金融比赛数据：[面向金融领域的篇章级事件元素抽取](https://www.biendata.xyz/competition/ccks_2021_task6_1/)。

本次竞赛使用的SKE数据集是业界规模最大的基于schema的中文信息抽取数据集，其包含超过43万三元组数据、21万中文句子及50个已定义好的schema，表1中展示了SKE数据集中包含的50个schema及对应的例子。数据集中的句子来自百度百科和百度信息流文本。数据集划分为17万训练集，2万验证集和2万测试集。其中训练集和验证集用于训练，可供自由下载，测试集分为两个，测试集1供参赛者在平台上自主验证，测试集2在比赛结束前一周发布，不能在平台上自主验证，并将作为最终的评测排名。



### Ernie模型训练
路径和初始化参数
```
dataset_name=ccks
data_dir=./data/${dataset_name}
conf_dir=./conf/${dataset_name}
ckpt_dir=./ckpt/${dataset_name}
submit_data_path=./submit/result.txt
pred_data=${data_dir}/sentence/test.json  

learning_rate=5e-5
max_seq_len=400
batch_size=16 #金融数据集里设为32
epoch=20 #金融数据集里设为10
```


模型参数
```
if [ "$is_train" = True ]; then
    unset CUDA_VISIBLE_DEVICES
    python -m paddle.distributed.launch --gpus "0"  sequence_labeling.py \
                            --num_epoch ${epoch} \
                            --learning_rate ${learning_rate} \
                            --tag_path ${conf_path} \
                            --train_data ${data_dir}/train.tsv \
                            --dev_data ${data_dir}/dev.tsv \
                            --test_data ${data_dir}/test.tsv \
                            --predict_data ${predict_data} \
                            --do_train True \
                            --do_predict False \
                            --max_seq_len ${max_seq_len} \
                            --batch_size ${batch_size} \
                            --skip_step 10 \
                            --valid_step 50 \
                            --checkpoints ${ckpt_dir} \
                            --init_ckpt ${ckpt_dir}/best.pdparams \
                            --predict_save_path ${pred_save_path} \
                            --device gpu
else
    export CUDA_VISIBLE_DEVICES=0
    python sequence_labeling.py \
            --num_epoch ${epoch} \
            --learning_rate ${learning_rate} \
            --tag_path ${conf_path} \
            --train_data ${data_dir}/train.tsv \
            --dev_data ${data_dir}/dev.tsv \
            --test_data ${data_dir}/test.tsv \
            --predict_data ${predict_data} \
            --do_train False \
            --do_predict True \
            --max_seq_len ${max_seq_len} \
            --batch_size ${batch_size} \
            --skip_step 10 \
            --valid_step 50 \
            --checkpoints ${ckpt_dir} \
            --init_ckpt ${ckpt_dir}/best.pdparams \
            --predict_save_path ${pred_save_path} \
            --device gpu
fi
```


## 评估阶段
模型的训练结果采用精确率（Precision, P）、召回率（Recall, R）、F1值（F1-measure, F1）来评估篇章事件要素的识别效果。采用微平均计算F值即所有样本一起计算P和R。

