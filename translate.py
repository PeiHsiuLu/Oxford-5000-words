import json
import requests
import time
import os
import random

def translate_word(word):
    """呼叫 Google Translate 隱藏 API 取得中文翻譯"""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "zh-TW",
        "dt": "t",
        "q": word
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()[0][0][0]
    except Exception:
        return None
    return None

def process_dictionary(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"找不到檔案: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 讀取已處理的進度，避免中斷後重跑
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            cleaned_data = json.load(f)
    else:
        cleaned_data = []

    # 追蹤已處理的 ID
    processed_ids = {item['id'] for item in cleaned_data}
    total_count = len(raw_data)

    print(f"總單字數: {total_count}。目前進度: {len(processed_ids)}/{total_count}")

    try:
        for item in raw_data:
            orig_id = item.get('id')
            val = item.get('value', {})
            word = val.get('word')

            if orig_id in processed_ids or not word:
                continue

            # 1. 翻譯單字
            definition = translate_word(word)
            if definition is None:
                print("\n[警告] 觸發 API 限制，建議休息 5 分鐘或切換 IP...")
                break

            # 2. 隨機挑選「一句」例句
            original_examples = val.get('examples', [])
            # 若無例句則回傳空字串，若有則隨機選一
            selected_example = random.choice(original_examples) if original_examples else ""

            # 3. 處理 Level 缺失值 (如 ID 47)
            level = val.get('level', '').strip()
            final_level = level if level else "Unclassified"

            # 4. 組成新結構
            new_entry = {
                "id": orig_id,
                "word": word,
                "type": val.get('type'),
                "level": final_level,
                "example": selected_example, # 已改為單一字串
                "definition": definition
            }

            cleaned_data.append(new_entry)
            
            # 每 20 個存檔一次並回報進度
            if len(cleaned_data) % 20 == 0:
                percent = (len(cleaned_data) / total_count) * 100
                print(f"\r進度: {len(cleaned_data)}/{total_count} ({percent:.2f}%) | 當前: {word} -> {definition}", end="")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

            # 保護機制：延遲 1 秒避免封鎖
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n使用者中斷，進度已儲存。")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    print(f"\n\n處理完成！結果儲存至: {output_file}")

# 啟動任務
process_dictionary('full-word.json', 'clear-word.json')