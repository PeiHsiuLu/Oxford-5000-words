import json
import os
import requests
import ollama
import re

# ==========================================
# 1. 核心功能函式
# ==========================================
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
        return "翻譯失敗"
    return "翻譯失敗"

def generate_example_sentence(word, word_type, level, max_retries=3):
    """呼叫本地端 Ollama 生成例句，並強制輸出 JSON 格式防呆"""
    
    prompt = f"""
    Create a practical English example sentence for the word "{word}".
    Requirements:
    1. The difficulty must strictly match CEFR level {level}.
    2. The word MUST be used as a {word_type} (part of speech).
    3. Output ONLY a valid JSON object in the following format, no extra text:
    {{"example": "Your sentence goes here."}}
    """
    
    for attempt in range(max_retries):
        try:
            response = ollama.generate(
                model='llama3.2', 
                prompt=prompt
            )
            raw_output = response['response'].strip()
            
            # 使用正則表達式，精準挖出 JSON，無視 AI 前後的多餘廢話
            json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result_dict = json.loads(json_str)
                example_sentence = result_dict.get('example', '')
                
                # 簡單檢查：如果句子裡有包含目標單字，才算成功
                if word.lower() in example_sentence.lower():
                    return example_sentence
                
        except Exception as e:
            print(f"\n  ⚠️ 格式解析失敗 ({word})，重試中 (第 {attempt+1}/{max_retries} 次)...")
                
    return ""

# ==========================================
# 2. 主處理邏輯
# ==========================================
def process_dictionary(input_file, output_file, limit=100):
    if not os.path.exists(input_file):
        print(f"找不到檔案: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            cleaned_data = json.load(f)
    else:
        cleaned_data = []

    processed_ids = {item['id'] for item in cleaned_data}
    total_count = len(raw_data)
    
    # 紀錄這次執行處理了幾個
    processed_this_run = 0

    print(f"🚀 開始批次處理！設定單次上限: {limit} 個。")
    print(f"總單字數: {total_count}。過去已處理: {len(processed_ids)} 個。")

    try:
        for item in raw_data:
            orig_id = item.get('id')
            
            # 如果這個 ID 已經處理過，就跳過
            if orig_id in processed_ids:
                continue

            val = item.get('value', {})
            word = val.get('word')
            
            if not word:
                continue
                
            word_type = val.get('type', 'unknown')
            level = val.get('level', '').strip()
            final_level = level if level else "Unclassified"

            # 步驟 A：取得翻譯
            definition = translate_word(word)
            
            # 步驟 B：取得 AI 例句
            example = generate_example_sentence(word, word_type, final_level)
            
            # 步驟 C：組裝符合目標結構的 JSON 格式
            new_entry = {
                "id": orig_id,
                "word": word,
                "type": word_type,
                "level": final_level,
                "example": example,
                "definition": definition
            }
            
            cleaned_data.append(new_entry)
            processed_this_run += 1
            
            print(f"[{len(cleaned_data)}/{total_count}] (本批次 {processed_this_run}/{limit}) {word} -> {example}")
            
            # 每 10 個單字存檔一次
            if len(cleaned_data) % 10 == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
                    
            # 檢查是否達到本次處理上限
            if processed_this_run >= limit:
                print(f"\n✅ 已經完成本批次的 {limit} 個單字處理，自動暫停。")
                break

    except KeyboardInterrupt:
        print("\n\n使用者中斷，進度已儲存。")
    except Exception as e:
        print(f"\n\n發生未預期錯誤: {e}")
    finally:
        # 確保最後一定會存檔
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        print(f"\n執行結束，當前結果已儲存至: {output_file}")

# ==========================================
# 3. 啟動腳本 (設定 limit=100)
# ==========================================
process_dictionary('full-word.json', 'final-dictionary.json', limit=500)