import json

<<<<<<< HEAD
submit_path = './submit/result.txt' # 预测的数据集
# 读取经过基于ERNIE预训练模型序列标注任务得到的预测结果txt文件
with open(submit_path,encoding='utf-8') as f:
    output = f.readlines()

train_data_path = './data/ccks/train.json' # 训练集
dev_data_path = './data/ccks/dev.json' # 验证集
# 读取训练集和验证集
with open(train_data_path,encoding='utf-8') as f:
    train_data = f.readlines()
with open(dev_data_path,encoding='utf-8') as f:
    dev_data = f.readlines()

# 构建三元组 - 预测集
def med_relation_extract(text=output,relation='药物',type1="疾病和诊断",type2="药物"):
=======
submit_path = './submit/result.txt'
# 读取经过基于ERNIE预训练模型序列标注任务得到的预测结果txt文件
with open(submit_path,encoding='utf-8') as f:
    c = f.readlines()

# 构建三元组
def med_relation_extract(text=c,relation='药物',type1="疾病和诊断",type2="药物"):
>>>>>>> 8ada55ddcd81c0229bc2b81acab38a73eacbdf57
    total = []
    for m in range(len(text)):
        a = eval(text[m])['attributes'] # return a list of dicts inside text's attributes
        num = len(a)

        tmp_type1 = []
        tmp_type2 = []
        for i in range(num):
            if a[i]['type'] == type1:
                tmp_type1.append(a[i]['entity'])
            elif a[i]['type'] == type2:
                tmp_type2.append(a[i]['entity'])
        num_type1 = len(tmp_type1)
        num_type2 = len(tmp_type2)

        subtotal = []
        for j in range(num_type1):
            for k in range(num_type2):
                subtotal.append({'entity1':tmp_type1[j],
                                 "relation":relation,
                                 'entity2':tmp_type2[k]}) #对两类实体进行排列组合，按dict格式储存
        #print(subtotal)
        for term in subtotal:
            total.append(term)
        total = [i for i in total if i != []] # 去除空值
    return(total)


<<<<<<< HEAD
# 构建三元组 - 训练集、验证集
def med_relation_extract_json(text=train_data,relation='药物',type1="疾病和诊断",type2="药物"):
    total = []
    for m in range(len(text)):
        a = eval(text[m])['event_list'] # return a list of dicts inside text's attributes
        a = a[0]['arguments']
        num = len(a)

        tmp_type1 = []
        tmp_type2 = []
        for i in range(num):
            if a[i]['role'] == type1:
                tmp_type1.append(a[i]['argument'])
            elif a[i]['role'] == type2:
                tmp_type2.append(a[i]['argument'])
        num_type1 = len(tmp_type1)
        num_type2 = len(tmp_type2)

        subtotal = []
        for j in range(num_type1):
            for k in range(num_type2):
                subtotal.append({'entity1':tmp_type1[j],
                                 "relation":relation,
                                 'entity2':tmp_type2[k]}) #对两类实体进行排列组合，按dict格式储存
        #print(subtotal)
        for term in subtotal:
            total.append(term)
        total = [i for i in total if i != []] # 去除空值
    return(total)


=======
>>>>>>> 8ada55ddcd81c0229bc2b81acab38a73eacbdf57
# 合并三元组
def expand_list_dict(list1,list2):
    for term in list2:
        list1.append(term)
    return list1


# 对list格式的dict进行去重
from functools import reduce
def remove_list_dict_duplicate(list_dict_data):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + list_dict_data)

<<<<<<< HEAD
##### PipeLine #####
def triple_from_output(output):
    # 定义4种实体3元组，共3种实体类型
    res = med_relation_extract(output,'治疗药物',type1="疾病和诊断",type2="药物")
    res2 = med_relation_extract(output,'检验方式',type1="疾病和诊断",type2="实验室检验")
    res3 = med_relation_extract(output,'检验方式',type1="疾病和诊断",type2="影像检查")
    res4 = med_relation_extract(output,'解剖部位',type1="手术",type2="解剖部位")
    # 合并三元组
    res = expand_list_dict(res,res2)
    res = expand_list_dict(res,res3)
    res = expand_list_dict(res,res4)
    # 去重
    res = remove_list_dict_duplicate(res)
    print('一共生成%s个三元组'%(len(res)))
    return res

def triple_from_input(train_data):
    # 定义4种实体3元组，共3种实体类型
    res = med_relation_extract_json(train_data,'治疗药物',type1="疾病和诊断",type2="药物")
    res2 = med_relation_extract_json(train_data,'检验方式',type1="疾病和诊断",type2="实验室检验")
    res3 = med_relation_extract_json(train_data,'检验方式',type1="疾病和诊断",type2="影像检查")
    res4 = med_relation_extract_json(train_data,'解剖部位',type1="手术",type2="解剖部位")
    # 合并三元组
    res = expand_list_dict(res,res2)
    res = expand_list_dict(res,res3)
    res = expand_list_dict(res,res4)
    # 去重
    res = remove_list_dict_duplicate(res)
    print('一共生成%s个三元组'%(len(res)))
    return res


if __name__ == "__main__":
    print("训练集%s,验证集%s,预测集%s"%(len(train_data),len(dev_data),len(output)))
    print("#### 开始构建三元组 ####")
    print("预测集：")
    res = triple_from_output(output)
    print("训练集：")
    res2 = triple_from_input(train_data)
    print("验证集：")
    res3 = triple_from_input(dev_data)

    # 合并三元组
    res = expand_list_dict(res,res2)
    res = expand_list_dict(res,res3)

    # 去重
    res = remove_list_dict_duplicate(res)
    print("#### 构建三元组完成 ####")
    print('一共生成%s个三元组'%(len(res)))

    # 导出Json文件
    file_path='submit/医疗三元组.json'
    with open(file_path,'w') as file_obj:
        for each in res:
            json.dump(each,file_obj,ensure_ascii=False)
            file_obj.write('\n')
=======




if __name__ == "__main__":

    # 定义4种实体3元组，共3种实体类型
    res = med_relation_extract(c,'治疗药物',type1="疾病和诊断",type2="药物")
    res2 = med_relation_extract(c,'检验方式',type1="疾病和诊断",type2="实验室检验")
    res3 = med_relation_extract(c,'检验方式',type1="疾病和诊断",type2="影像检查")
    res4 = med_relation_extract(c,'解剖部位',type1="手术",type2="解剖部位")
    # 合并三元组
    res = expand_list_dict(res,res2)
    res = expand_list_dict(res,res3)
    res = expand_list_dict(res,res4)
    # 去重
    res = remove_list_dict_duplicate(res)
    print('一共生成%s个三元组'%(len(res)))
    # 导出Json文件
    file_path='submit/医疗三元组.json'
    with open(file_path,'w') as file_obj:
        json.dump(res,file_obj,ensure_ascii=False)
>>>>>>> 8ada55ddcd81c0229bc2b81acab38a73eacbdf57
    print("------Task Completed------")

