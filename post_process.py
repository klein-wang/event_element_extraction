import json
import pandas as pd
import numpy as np



def merge(x):
    x.reset_index(inplace=True)
    num = len(x)
    if num > 1:
        text,labels = '',''
        for i in range(1,num):
            text += x['text'][i]
            if i <= num-2:
                labels = labels + x['labels'][i] + '\t'
            else:
                labels += x['labels'][i]
    else:
        text, labels = x['text'][0], x['labels'][0]
    return pd.DataFrame({'text':[text],'labels':[labels]})


# 适配groupby apply的函数，此时传入函数的x还是逐字符形式，将entity进行拼接，同时start就是第一个index，end是最后的index
def final_process(x):
    len_ = len(x)
    entity = ''
    type_ = x['type'].iloc[0] # x是一个dataframe
    start = x['index'].iloc[0]
    end = x['index'].iloc[-1]
    for i in range(len_):
        entity += x['word_x'].iloc[i]
    return pd.DataFrame({'type':[type_],'entity':[entity],'start':[start],'end':[end]})

# 这里是对1000条数据中的一条进行的处理，每一条都转成DataFrame进行操作
def gain_post_json(text_id, text, labels):
    text_tmp = pd.DataFrame({'index':range(len(text)),'word':list(text)})
    labels_tmp = pd.DataFrame({'index':range(len(labels)),'word':list(labels)})
    res_tmp = pd.merge(text_tmp,labels_tmp,on='index')
    res_tmp2 = res_tmp.loc[res_tmp['word_y'] != 'O']
    res_tmp2['type'] = res_tmp2['word_y'].apply(lambda x:x.split('-')[1])    # B-嫌疑人 切开后取后者
    res_tmp2['re_index'] = range(len(res_tmp2))
    res_tmp2['diff_index'] = res_tmp2['index'] - res_tmp2['re_index']
    res_tmp3 = res_tmp2.groupby('diff_index').apply(final_process)
    res_tmp4 = res_tmp3.reset_index()
    post_json = {
        'text_id': str(text_id),
        'attributes': []
    }
    for i in range(len(res_tmp4)):
        post_json['attributes'].append({'type':res_tmp4['type'][i],'entity':res_tmp4['entity'][i],'start':int(res_tmp4['start'][i]),'end':int(res_tmp4['end'][i])})  # 在存json格式是报错不支持int64，因此在这些数字前加了int()转型
    
    return post_json



if __name__ == '__main__':
    pd.set_option('mode.chained_assignment', None)
    pred_path = './ckpt/ccks/role/test_pred.json'
    row_path = './data/ccks/pre_submit/test_row.csv'
    handle_path = './data/ccks/pre_submit/test_handle.csv'
    submit_path = './submit/result.txt'
    # 读取经过基于ERNIE预训练模型序列标注任务得到的预测结果json文件
    with open(pred_path,encoding='utf-8') as f:
        c = f.readlines()
        
    print("============start submitted data process==========")    
    # 保留事件文本内容和对应BIO标签，从text中拿entity,start,end，从labels中拿type
    t = pd.DataFrame(columns=['text_id','text','labels'])
    for data in c:
        a = eval(data)
        labels = ''
        tmp = a['pred']['labels'] # 返回BIO的标注'labels'
        for i,l in enumerate(tmp):
            if i<len(tmp)-1:
                labels = labels + l + '\t'
            else:
                labels = labels + l
        t.loc[len(t)] = {'text_id':a['id'],'text':a['text'],'labels':labels}

    t.to_csv(row_path,index=None)

    res = t
    # res = t.groupby('text_id').apply(merge) # 金融数据集使用
    res.reset_index(inplace=True)
    # 在使用groupby和apply函数进行归并时，多出一个'level_1'的列，这里简单进行了删除操作
    # res.drop(['level_1'], axis=1,inplace=True)  # 金融数据集使用
    res.to_csv(handle_path,index=None)
    print("============cleaning step is completed==========")


    with open(submit_path,'w',encoding='utf-8') as f:
        for i in range(len(res)):
            post_json = gain_post_json(res['text_id'][i], res['text'][i],res['labels'][i].split('\t'))
            json.dump(post_json, f , ensure_ascii=False)    # ensure_ascii=False可以解决中文乱码
            f.write('\n')
    print("============the submitted data has been generated: {}==========".format(submit_path))









