import ollama

def check_local_models():
    try:
        # 呼叫本地端的 Ollama 服務取得模型清單
        response = ollama.list()
        
        print("🟢 目前本地端已下載的 Ollama 模型清單：")
        models = response.get('models', [])
        
        if not models:
            print("目前沒有任何模型。請在終端機輸入例如：`ollama run llama3` 來下載模型。")
            return

        for m in models:
            # 印出模型名稱與大小
            size_gb = m.get('size', 0) / (1024 ** 3)
            print(f"- {m['name']} (大小: {size_gb:.1f} GB)")
            
    except Exception as e:
        print("🔴 無法連線到 Ollama。")
        print("請確認：")
        print("1. Ollama 軟體是否已經啟動？")
        print("2. 是否已經安裝套件：pip install ollama")
        print(f"錯誤詳細資訊: {e}")

if __name__ == "__main__":
    check_local_models()