import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer

# ==========================================
# 1. 載入模型與量化設定 (BitsAndBytes)
# ==========================================
model_id = "meta-llama/Llama-3.2-3B-Instruct"

print("🚀 正在載入 Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

print("🚀 正在以 4-bit 量化載入 Llama 3.2 3B 模型...")
# 設定 4-bit 量化，讓 8GB VRAM 的 RTX 3050 能夠順利載入
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto" # 自動將模型分配到你的顯示卡上
)

# 準備進行低位元訓練
model = prepare_model_for_kbit_training(model)

# ==========================================
# 2. 設定 LoRA 參數 (PEFT)
# ==========================================
print("🧠 注入 LoRA 微調適配器...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# ==========================================
# 3. 讀取與處理訓練資料
# ==========================================
print("📂 讀取 dataset.json...")
dataset = load_dataset("json", data_files="dataset.json", split="train")

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def formatting_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input, output) + tokenizer.eos_token
        texts.append(text)
    return { "text" : texts }

dataset = dataset.map(formatting_func, batched = True)

# ==========================================
# 4. 開始訓練
# ==========================================
print("🔥 開始啟動標準 Hugging Face 訓練...")
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 512,
    args = TrainingArguments(
        per_device_train_batch_size = 1, # 保守起見先設 1，以防 VRAM 爆掉
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 30, # 10筆資料的 PoC 測試
        learning_rate = 2e-4,
        fp16 = True,
        logging_steps = 5,
        optim = "paged_adamw_8bit",
        output_dir = "hf_outputs",
    ),
)

# 節省 VRAM 的關鍵機制
model.config.use_cache = False 
trainer.train()

# ==========================================
# 5. 儲存 LoRA 權重
# ==========================================
print("✅ 訓練完成！正在儲存 LoRA 權重檔...")
trainer.model.save_pretrained("my_lora_adapter")
tokenizer.save_pretrained("my_lora_adapter")
print("🎉 儲存成功！權重檔位於 my_lora_adapter 目錄中。")