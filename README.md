[README.md](https://github.com/user-attachments/files/24199132/README.md)
# AI Codebook Generator

Multi-API tool for comparing thematic analysis outputs across AI platforms. Designed for research on AI-assisted qualitative analysis of focus group data from the Kidenga project.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Set environment variables for each API you want to use:

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
export PERPLEXITY_API_KEY="your-key"
export XAI_API_KEY="your-key"  # For Grok
```

Or create a `.env` file:

```bash
python ai_codebook_generator.py --setup-env
# Then edit .env.template and rename to .env
```

To load from .env, add this at the top of the script or use python-dotenv:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Usage

### Basic run (20 iterations, both prompts)

```bash
python ai_codebook_generator.py --data focus_group_notes.txt --iterations 20
```

### Multiple iteration counts

```bash
python ai_codebook_generator.py --data focus_group_notes.txt --iterations 20 30 50
```

### Single prompt type

```bash
# Contextual prompt only
python ai_codebook_generator.py --data focus_group_notes.txt --iterations 20 --prompt contextual

# Minimal prompt only
python ai_codebook_generator.py --data focus_group_notes.txt --iterations 20 --prompt minimal
```

### Custom output directory

```bash
python ai_codebook_generator.py --data focus_group_notes.txt -o ./results
```

## Output

Results are saved to CSV with the following columns:

| Column | Description |
|--------|-------------|
| iteration | Current iteration number (1, 2, 3...) |
| iteration_batch | Batch identifier (20x, 30x, 50x) |
| total_iterations | Total iterations in this batch |
| prompt_type | contextual or minimal |
| model | API/model name |
| success | Whether the request succeeded |
| error | Error message if failed |
| tokens_input | Input token count |
| tokens_output | Output token count |
| timestamp | ISO timestamp of the request |
| content | The generated codebook |

## Prompt Variations

**Contextual prompt** - includes context about Puerto Rico, Kidenga app, and research purpose:
> "For context, I would like your help conducting an inductive thematic qualitative analysis of focus group discussions which were held in Puerto Rico..."

**Minimal prompt** - stripped of contextual information:
> "Based on the focus group discussions data I provide you with, please conduct an inductive thematic analysis..."

## API Notes

- **OpenAI**: Currently set to gpt-4o. Update `Config.OPENAI_MODEL` when GPT-5.2 becomes available.
- **Perplexity**: Uses llama-3.1-sonar-large model via their API.
- **Grok**: Uses xAI's API endpoint.
- **Rate limiting**: 2-second delay between requests (configurable via `Config.REQUEST_DELAY`).

## Programmatic Usage

```python
from ai_codebook_generator import CodebookGenerator, load_focus_group_data

# Load your data
data = load_focus_group_data("focus_group_notes.txt")

# Initialize generator
generator = CodebookGenerator(focus_group_data=data)

# Run single batch
results = generator.run_iterations(iterations=20, prompt_type="contextual")
generator.save_results(results, "batch_20x_contextual.csv")

# Or run full experiment
generator.run_full_experiment(
    iteration_counts=[20, 30, 50],
    prompt_types=["contextual", "minimal"]
)
```

## Cost Estimation

Before running large batches, estimate costs:
- 20 iterations × 5 APIs = 100 API calls
- 50 iterations × 5 APIs × 2 prompts = 500 API calls

Check each provider's pricing for your expected token usage.
