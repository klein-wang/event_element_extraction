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

echo -e "check and create directory"
dir_list=(./ckpt ${ckpt_dir} ./submit)
for item in ${dir_list[*]}
do
    if [ ! -d ${item} ]; then
        mkdir ${item}
        echo "create dir * ${item} *"
    else
        echo "dir ${item} exist"
    fi
done

process_name=${1}

run_sequence_labeling_model(){
    model=${1}
    is_train=${2} 
    pred_save_path=${ckpt_dir}/${model}/test_pred.json
    sh run_sequence_labeling.sh ${data_dir}/${model} ${conf_dir}/${model}_tag.dict ${ckpt_dir}/${model} ${pred_data} ${learning_rate} ${is_train} ${max_seq_len} ${batch_size} ${epoch} ${pred_save_path}
}

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