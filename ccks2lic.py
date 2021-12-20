import json

# 按标点切句子，只是为了对齐lic2021中的title，思路是将text中的第一句话作为title
def cut_sentences(content):
    # 结束符号，包含中文和英文的
    end_flag = ['。', ';', '；','?','.','？','.']

    content_len = len(content)
    sentences = ''
    tmp_char = ''
    for idx, char in enumerate(content):
        # 拼接字符
        tmp_char += char

        # 判断是否已经到了最后一位
        if (idx + 1) == content_len:
            sentences += (tmp_char)
            break

        # 判断此字符是否为结束符号
        if char in end_flag:
            # 再判断下一个字符是否为结束符号，如果不是结束符号，则切分句子
            next_idx = idx + 1
            if not content[next_idx] in end_flag:
                sentences += tmp_char + '\n'
                tmp_char = ''

    return sentences

# ccks2021额外提供了三个level1，这里简单的让level1填充lic2021中的trigger槽位，level2填充event_type，只是为了保证lic2021的data_prepare代码正常运行，后续也没用用到trigger和event_type。重心在于属性中的论元角色列表，对应了ccks2021篇章级事件主体的类型和实体名
def train_ccks2lic(s):
    t = {'text': '',
     'event_list': [{'trigger': '',
       'event_type': '',
       'arguments': []}],
     'id': '',
     'title': ''}
    t['id'] = s['text_id']
    t['text'] = cut_sentences(s['text'])
    t['title'] = cut_sentences(s['text']).split('\n')[0]
    t['event_list'][0]['trigger'] = s['level1']
    t['event_list'][0]['event_type'] = s['level2']
    for i in s['attributes']:
        t['event_list'][0]['arguments'].append({'role': i['type'], 'argument': i['entity']})
    return t

    


def test_ccks2lic(s):
    t = {'text':'','id':'','title':''}
    text = cut_sentences(s['text'])
    t['text'] = text
    t['id'] = s['text_id']
    t['title'] = text.split('\n')[0]
    return t

def gain_train_dev(raw_path, train_save_path, dev_save_path):
    with open(raw_path, 'r', encoding='utf-8') as f:
        data = f.readlines()
    num = int(len(data) * 0.8)
    ccks_train, ccks_dev = data[:num], data[num:]
    with open(train_save_path, 'w',encoding='utf-8') as f:
        for i,data in enumerate(ccks_train):
            new_data = train_ccks2lic(eval(data))
            json.dump(new_data,f,ensure_ascii=False)
            f.write('\n')
    with open(dev_save_path, 'w',encoding='utf-8') as f:
        for i,data in enumerate(ccks_dev):
            new_data = train_ccks2lic(eval(data))
            json.dump(new_data,f,ensure_ascii=False)
            f.write('\n')            


def gain_test(raw_path, save_path):
    with open(raw_path, 'r', encoding='utf-8') as f:
        ccks_test = f.readlines()
    with open(save_path,'w', encoding='utf-8') as f:
        for i,data in enumerate(ccks_test):
            new_data = test_ccks2lic(eval(data))
            json.dump(new_data,f,ensure_ascii=False)
            f.write('\n')


if __name__ == '__main__':
    train_raw_data_path = 'data/ccks/raw/ccks_task1_train.txt'
    test_raw_data_path = 'data/ccks/raw/ccks_task1_eval_data.txt'

    train_lic_data_save_path = 'data/ccks/train.json'
    dev_lic_data_save_path = 'data/ccks/dev.json'
    test_lic_data_save_path = 'data/ccks/test.json'

    print("\n=================start generate train and dev data process==============")
    gain_train_dev(train_raw_data_path, train_lic_data_save_path, dev_lic_data_save_path)
    print("\n=================end generate train and dev data process==============")

    print("\n=================start generate test data process==============")
    gain_test(test_raw_data_path, test_lic_data_save_path)
    print("\n=================end generate test data process==============")    