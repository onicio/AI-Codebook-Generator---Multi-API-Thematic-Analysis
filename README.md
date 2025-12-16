# AI Codebook Generator

A Python tool for comparing thematic analysis outputs across multiple AI platforms. Designed for research on AI-assisted qualitative analysis of focus group data.

## Overview

This script sends the same prompt to multiple AI APIs (OpenAI, Anthropic Claude, Google Gemini, Perplexity, and xAI Grok) across multiple iterations, collecting codebook outputs for comparative analysis. Useful for evaluating consistency and variation in AI-generated qualitative coding.

## Features

- Multi-API support (5 providers)
- Configurable iteration counts (20x, 30x, 50x)
- Two prompt variants (contextual vs. minimal)
- CSV output with iteration tagging
- Progress tracking and error handling

## Requirements

- Python 3.8+
- API keys for desired providers

## Installation

```bash
# Clone the repository
git clone https://github.com/onicio/AI-Codebook-Generator---Multi-API-Thematic-Analysis.git
cd ai-codebook-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### API Keys

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
export GOOGLE_API_KEY="your-google-key"
export PERPLEXITY_API_KEY="pplx-your-key"
export XAI_API_KEY="your-xai-key"
```

> **Note:** You don't need all five APIs configured. The script will use whichever ones are available.

### Focus Group Data

Set your transcription file path in `ai_codebook_generator.py` (line ~62):

```python
FOCUS_GROUP_FILE = "./data/your_transcription.txt"
```

Or pass it via command line with `--data`.

## Usage

```bash
# Basic run (20 iterations, both prompt types)
python ai_codebook_generator.py --data ./transcription.txt --iterations 20

# Full experiment
python ai_codebook_generator.py --data ./transcription.txt --iterations 20 30 50

# Single prompt type
python ai_codebook_generator.py --data ./transcription.txt --iterations 20 --prompt contextual
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--data` | `-d` | Path to focus group transcription file |
| `--iterations` | `-i` | Number of iterations (accepts multiple values) |
| `--prompt` | `-p` | Prompt type: `contextual`, `minimal`, or `both` |
| `--output` | `-o` | Output directory (default: `./output`) |
| `--setup-env` | | Generate `.env` template file |

## Output

Results are saved to `./output/` as CSV files with the following columns:

| Column | Description |
|--------|-------------|
| `iteration` | Current iteration number |
| `iteration_batch` | Batch identifier (20x, 30x, 50x) |
| `prompt_type` | contextual or minimal |
| `model` | API/model name |
| `success` | Request success status |
| `content` | Generated codebook |
| `timestamp` | ISO timestamp |

## Project Structure

```
ai-codebook-generator/
├── ai_codebook_generator.py   # Main script
├── requirements.txt           # Dependencies
├── README.md
├── data/
│   └── your_transcription.txt # Your focus group data
└── output/
    └── *.csv                  # Generated results
```

## Prompt Variants

**Contextual** — includes research context:
> "For context, I would like your help conducting an inductive thematic qualitative analysis of focus group discussions which were held in Puerto Rico that included participants from the local community, to evaluate the utility and ease of use of the Kidenga mobile app design..."

**Minimal** — stripped of context:
> "Based on the focus group discussions data I provide you with, please conduct an inductive thematic analysis and produce a codebook in a table format..."

## Cost Estimation

| Data Size | Est. Cost (full experiment) |
|-----------|----------------------------|
| ~2,000 words | $15–50 |
| ~5,000 words | $40–100 |
| ~10,000 words | $80–180 |

## Troubleshooting

**Module not found**
```bash
pip install -r requirements.txt
```

**API not configured**
```bash
# Verify your keys are set
echo $OPENAI_API_KEY
```

**File not found**
```bash
# Use absolute path
python ai_codebook_generator.py --data /full/path/to/file.txt
```

## License

MIT

## Citation

If you use this tool in your research, please cite accordingly.
