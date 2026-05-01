# Oxford Dictionary 5000 Word List (Modified Chinese Version)

This repository features a cleaned and localized version of the **Oxford 3000 & 5000** word lists. The original dataset has been specifically processed using Python to enhance readability and utility for developers building English learning applications, vocabulary trainers, or flashcard systems.

## 🔗 Dataset Access
The processed dataset is available here: **[wordlist (cleaned)](https://github.com/PeiHsiuLu/Oxford-5000-words/blob/main/clear-word.json)**

---

## 🌟 Key Features
- **Field Optimization**: Trimmed redundant metadata to keep the file lightweight and focused on core learning content.
- **Traditional Chinese Localization**: Added a `definition` field with Traditional Chinese translations powered by the Google Translate API.
- **Simplified Examples**: To prevent information overload, each entry contains exactly **one randomly selected example** from the original array of sentences.
- **Consistent Identification**: Included a unique `id` for each entry to facilitate database indexing and referencing.
- **CEFR Level Handling**: Retains the A1–C1 difficulty levels, with missing or empty values explicitly labeled as `"Unclassified"` (e.g., the entry for *accounting*).

---

## 📊 Data Structure
Each entry in `clear-word.json` follows this schema:
```json
    {
        "id": 0,
        "word": "a",
        "type": "indefinite article",
        "level": "A1",
        "example": "There's a visitor for you.",
        "definition": "一個"
    }
```

| Key | Description |
| :--- | :--- |
| **id** | Unique identifier for the word from the original dataset. |
| **word** | The English vocabulary word. |
| **type** | Part of speech (e.g., noun, verb, adjective). |
| **level** | CEFR difficulty level (A1, A2, B1, B2, C1) or "Unclassified" if missing in source. |
| **example** | A single representative sentence selected randomly from the original source examples. |
| **definition** | Traditional Chinese translation. |

---

## 🛠️ Cleaning Process (Python)
The dataset was transformed using a Python workflow consisting of:
1.  **Extraction**: Parsing the original nested JSON structure.
2.  **Filtering**: Retaining only essential keys: `word`, `type`, and `level`.
3.  **Randomization**: Applying `random.choice()` to the original `examples` array to pick one high-quality sentence for better readability.
4.  **Translation**: Iterating through the 5,948 entries to fetch definitions via the Google Translate hidden API.
5.  **Data Integrity**: Handling empty strings or whitespace in the source data (such as in the level field for specific entries like ID 47) to ensure every field has a valid value.

---

## 📖 Intended Use
This cleaned list is ideal for:
*   Building mobile or web vocabulary training systems.
*   Generating randomized English-to-Chinese quizzes.
*   Integrating structured word lists into AI-driven educational bots.

---

## ⚠️ Disclaimer
This project is intended for educational and research purposes. The original word lists and example sentences remain the property of **Oxford Learner's Dictionaries**.
