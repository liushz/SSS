# ATLAS: A High-Difficulty, Multidisciplinary Benchmark for Frontier Scientific Reasoning

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dataset License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Dataset%20License-CC%20BY--NC--SA%204.0-blue.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Paper](https://img.shields.io/badge/Paper-arXiv-red.svg)](https://arxiv.org/abs/XXXX.XXXXX)
[![Website](https://img.shields.io/badge/Website-ATLAS-green.svg)](https://liushz.github.io/SSS/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-orange)](https://huggingface.co/datasets/opencompass/ATLAS)

</div>

---

## 📊 Overview

**ATLAS (AGI-Oriented Testbed for Logical Application in Science)** is a high-difficulty, multidisciplinary benchmark designed to evaluate frontier scientific reasoning capabilities of Large Language Models (LLMs). As existing benchmarks show saturated performance, ATLAS provides a reliable measuring stick for progress towards Artificial General Intelligence.

### 🌟 Key Features

- **🎯 800+ Original High-Quality Questions**: All questions are newly created or significantly adapted to prevent data contamination
- **🔬 7 Core Scientific Domains**: Mathematics, Physics, Chemistry, Biology, Computer Science, Earth Science, and Materials Science
- **🏛️ 25+ Leading Institutions**: Contributed by PhD-level experts from top universities and research institutions
- **💎 High-Fidelity Answers**: Complex, open-ended answers involving multi-step reasoning and LaTeX expressions
- **🛡️ Contamination-Resistant**: Rigorous quality control with multi-round expert peer review and adversarial testing

### 📈 Leaderboard Highlights

Latest results evaluated with **OpenAI-o4-mini** as judge (Public Validation Set):

| Rank | Model | Organization | Accuracy (Avg) |
|------|-------|--------------|----------------|
| 1 | OpenAI GPT-5-High | OpenAI | 42.9% |
| 2 | Gemini-2.5-Pro | Google | 35.3% |
| 3 | Grok-4 | xAI | 34.1% |
| 4 | OpenAI o3-High | OpenAI | 33.8% |
| 5 | DeepSeek-R1-0528 | DeepSeek AI | 26.4% |

> 📝 **Note**: Results show that even the most advanced models struggle with ATLAS, demonstrating its effectiveness as a frontier benchmark.

For complete leaderboard and submission: [https://liushz.github.io/SSS/](https://liushz.github.io/SSS/)

---

## 🚀 Quick Start

### Installation

```bash
pip install opencompass
```

### Load Dataset

```python
from datasets import load_dataset

# Load ATLAS dataset
dataset = load_dataset("opencompass/ATLAS")

# Access validation split
val_data = dataset['val']
print(f"Validation samples: {len(val_data)}")

# Access test split (for inference only)
test_data = dataset['test']
```

### Basic Evaluation Setup

```python
from mmengine.config import read_base

with read_base():
    from opencompass.configs.datasets.atlas.atlas_gen import atlas_datasets

# Update your judge model information
atlas_datasets[0]["eval_cfg"]["evaluator"]["judge_cfg"]["judgers"][0].update(dict(
    abbr="YOUR_MODEL_ABBR",
    openai_api_base="YOUR_API_URL",
    path="YOUR_MODEL_PATH",
    key="YOUR_API_KEY",
    # tokenizer_path="o3",  # Optional: update if using a different model
))
```

### Evaluate on Test Split

```python
from mmengine.config import read_base

with read_base():
    from opencompass.configs.datasets.atlas.atlas_gen import atlas_datasets

# Configure for test split
atlas_datasets[0]["abbr"] = "atlas-test" 
atlas_datasets[0]["split"] = "test"
atlas_datasets[0]["eval_cfg"]["evaluator"]["dataset_cfg"]["abbr"] = "atlas-test"
atlas_datasets[0]["eval_cfg"]["evaluator"]["dataset_cfg"]["split"] = "test"
```

> ⚠️ **Important**: The test split is only supported for inference mode. Use `-m infer` flag when running OpenCompass.

### Run Evaluation

```bash
# Evaluate on validation set
python run.py configs/eval_atlas.py

# Evaluate on test set (inference only)
python run.py configs/eval_atlas.py -m infer
```

---

## 📚 Dataset Structure

### Data Fields

- `name_en`: Subject name in English (e.g., "Biology", "Physics")
- `question`: The scientific question/problem statement
- `answer_ideas`: Reasoning ideas and approaches for solving the problem
- `refined_standard_answer`: List of standard answers (may contain multiple sub-answers)
- `sub_subject_name`: Specific sub-discipline (e.g., "Molecular Biology", "Quantum Mechanics")

### Data Splits

| Split | Count | Purpose |
|-------|-------|---------|
| **Validation** | 300+ | Public evaluation, reproducible results |
| **Test** | 500+ | Hidden evaluation, contamination-resistant |

### Example Data Point

```json
{
  "name_en": "Biology",
  "question": "Explain how CRISPR-Cas9 gene editing works at the molecular level...",
  "answer_ideas": "[\"Cas9 protein binds to guide RNA...\"]",
  "refined_standard_answer": [
    "1. Guide RNA (gRNA) directs Cas9 to target DNA sequence...",
    "2. Cas9 creates double-strand break...",
    "3. Cell repairs through NHEJ or HDR pathways..."
  ],
  "sub_subject_name": "Molecular Biology and Biotechnology"
}
```

---

## 🎯 Evaluation Protocol

ATLAS uses an **LLM-as-Judge** evaluation framework with the following characteristics:

### Judge Model

- Default: **OpenAI-o4-mini** (for leaderboard consistency)
- Customizable: You can use your own judge model

### Evaluation Process

1. **Model Inference**: Generate answers in structured JSON format
2. **Answer Extraction**: Parse final answers from model outputs
3. **LLM Judging**: Compare candidate answers with standard answers
4. **Scoring**: Calculate accuracy and pass@k metrics

### Answer Format

Models should output answers in the following JSON format:

```json
{
  "answers": [
    "answer to sub-question 1",
    "answer to sub-question 2",
    ...
  ]
}
```

### Evaluation Metrics

- **Accuracy (Avg)**: Average correctness across all questions
- **mG-Pass@2**: Majority voting accuracy with 2 samples
- **mG-Pass@4**: Majority voting accuracy with 4 samples

---

## 📜 Citation

If you use ATLAS in your research, please cite:

```bibtex
@inproceedings{atlas2025,
    title={ATLAS: A High-Difficulty, Multidisciplinary Benchmark for Frontier Scientific Reasoning},
    author={ATLAS Team},
    booktitle={Proceedings of XXX},
    year={2025}
}
```



