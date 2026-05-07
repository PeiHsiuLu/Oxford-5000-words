import json

# 讀取你最新整理好的完美資料
input_file = 'filtered-word.json'
output_file = 'dataset.json'

# 【重點修改】系統提示詞：拿掉翻譯要求，只要它生出英文例句
instruction = "你是一個專業的英語教材編輯。請根據單字、級別、詞性與字義，提供一個符合該級別的英文例句。格式為「例句：[英文]」。"

training_data = []

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    for item in raw_data:
        word = item.get('word', '')
        level = item.get('level', '')
        word_type = item.get('type', '')
        definition = item.get('definition', '')
        example = item.get('example', '')
        
        # 建立訓練用的 Input 格式 (依然保留 definition 給 AI 參考語境)
        input_text = f"單字：{word}, 級別：{level}, 詞性：{word_type}, 字義：{definition}"
        
        # 建立訓練用的 Output 格式 (直接填入例句，乾淨俐落)
        output_text = f"例句：{example}"
        
        # 將整理好的單筆資料加入陣列
        training_data.append({
            "instruction": instruction,
            "input": input_text,
            "output": output_text
        })

    # 將結果輸出成 Llama 訓練需要的格式
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=4)

    print(f"成功轉換 {len(training_data)} 筆訓練資料！已儲存至 {output_file}")
    print("請直接執行 train.py 開始訓練！")

except FileNotFoundError:
    print(f"找不到檔案 {input_file}，請確認檔名與路徑是否正確。")