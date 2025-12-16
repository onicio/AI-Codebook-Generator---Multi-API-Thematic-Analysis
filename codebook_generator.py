"""
AI Codebook Generator - Multi-API Thematic Analysis
=====================================================
Script for comparing thematic analysis outputs across multiple AI platforms.
Designed for research on AI-assisted qualitative analysis of focus group data.

Usage: python ai_codebook_generator.py --iterations 20 --prompt contextual
"""

import os
import csv
import time
import argparse
from datetime import datetime
from pathlib import Path
import json

# API clients - install with:
# pip install openai anthropic google-generativeai requests

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

import requests


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """API configuration - set your keys here or via environment variables"""
    
    # API Keys (set via environment variables for security)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    XAI_API_KEY = os.getenv("XAI_API_KEY", "")  # Grok
    
    # Model identifiers
    OPENAI_MODEL = "gpt-5.1"  
    ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
    GOOGLE_MODEL = "gemini-1.5-pro"
    PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"
    GROK_MODEL = "grok-2-latest"
    
    # Rate limiting (seconds between requests)
    REQUEST_DELAY = 2
    
    # Output directory
    OUTPUT_DIR = Path("./output")


# ============================================================================
# PROMPTS
# ============================================================================

PROMPT_CONTEXTUAL = """For context, I would like your help conducting an inductive thematic qualitative analysis of focus group discussions which were held in Puerto Rico that included participants from the local community, to evaluate the utility and ease of use of the Kidenga mobile app design as well as the usefulness of the information provided to community members. Based only on the focus group discussions data I provide you with, please produce a codebook in a table format that has a column for the themes you identify, a column with the description of the theme, and a column that provides an example of that theme from the data provided.

FOCUS GROUP DATA:
{focus_group_data}"""

PROMPT_MINIMAL = """Based on the focus group discussions data I provide you with, please conduct an inductive thematic analysis and produce a codebook in a table format that has a column for the themes you identify, a column with the description of the theme, and a column that provides an example of that theme from the data provided.

FOCUS GROUP DATA:
{focus_group_data}"""


# ============================================================================
# API HANDLERS
# ============================================================================

class APIHandler:
    """Base class for API interactions"""
    
    def __init__(self, name):
        self.name = name
        self.enabled = False
    
    def query(self, prompt: str) -> dict:
        """Send prompt and return response with metadata"""
        raise NotImplementedError
    
    def _format_response(self, content: str, success: bool, error: str = None, 
                         tokens_in: int = 0, tokens_out: int = 0) -> dict:
        return {
            "model": self.name,
            "content": content,
            "success": success,
            "error": error,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "timestamp": datetime.now().isoformat()
        }


class OpenAIHandler(APIHandler):
    """Handler for OpenAI GPT models"""
    
    def __init__(self):
        super().__init__("OpenAI-GPT")
        if OpenAI and Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.enabled = True
        else:
            self.client = None
    
    def query(self, prompt: str) -> dict:
        if not self.enabled:
            return self._format_response("", False, "OpenAI API not configured")
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return self._format_response(
                content=response.choices[0].message.content,
                success=True,
                tokens_in=response.usage.prompt_tokens,
                tokens_out=response.usage.completion_tokens
            )
        except Exception as e:
            return self._format_response("", False, str(e))


class AnthropicHandler(APIHandler):
    """Handler for Anthropic Claude models"""
    
    def __init__(self):
        super().__init__("Anthropic-Claude")
        if anthropic and Config.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.enabled = True
        else:
            self.client = None
    
    def query(self, prompt: str) -> dict:
        if not self.enabled:
            return self._format_response("", False, "Anthropic API not configured")
        
        try:
            response = self.client.messages.create(
                model=Config.ANTHROPIC_MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._format_response(
                content=response.content[0].text,
                success=True,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens
            )
        except Exception as e:
            return self._format_response("", False, str(e))


class GeminiHandler(APIHandler):
    """Handler for Google Gemini models"""
    
    def __init__(self):
        super().__init__("Google-Gemini")
        if genai and Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.GOOGLE_MODEL)
            self.enabled = True
        else:
            self.model = None
    
    def query(self, prompt: str) -> dict:
        if not self.enabled:
            return self._format_response("", False, "Google API not configured")
        
        try:
            response = self.model.generate_content(prompt)
            # Gemini doesn't always return token counts in the same way
            tokens_in = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            tokens_out = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            
            return self._format_response(
                content=response.text,
                success=True,
                tokens_in=tokens_in,
                tokens_out=tokens_out
            )
        except Exception as e:
            return self._format_response("", False, str(e))


class PerplexityHandler(APIHandler):
    """Handler for Perplexity AI"""
    
    def __init__(self):
        super().__init__("Perplexity")
        self.api_key = Config.PERPLEXITY_API_KEY
        self.enabled = bool(self.api_key)
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def query(self, prompt: str) -> dict:
        if not self.enabled:
            return self._format_response("", False, "Perplexity API not configured")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": Config.PERPLEXITY_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            return self._format_response(
                content=data["choices"][0]["message"]["content"],
                success=True,
                tokens_in=data.get("usage", {}).get("prompt_tokens", 0),
                tokens_out=data.get("usage", {}).get("completion_tokens", 0)
            )
        except Exception as e:
            return self._format_response("", False, str(e))


class GrokHandler(APIHandler):
    """Handler for xAI Grok models"""
    
    def __init__(self):
        super().__init__("xAI-Grok")
        self.api_key = Config.XAI_API_KEY
        self.enabled = bool(self.api_key)
        self.base_url = "https://api.x.ai/v1/chat/completions"
    
    def query(self, prompt: str) -> dict:
        if not self.enabled:
            return self._format_response("", False, "xAI API not configured")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": Config.GROK_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            return self._format_response(
                content=data["choices"][0]["message"]["content"],
                success=True,
                tokens_in=data.get("usage", {}).get("prompt_tokens", 0),
                tokens_out=data.get("usage", {}).get("completion_tokens", 0)
            )
        except Exception as e:
            return self._format_response("", False, str(e))


# ============================================================================
# MAIN RUNNER
# ============================================================================

class CodebookGenerator:
    """Main class to orchestrate multi-API codebook generation"""
    
    def __init__(self, focus_group_data: str, output_dir: Path = None):
        self.focus_group_data = focus_group_data
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all API handlers
        self.handlers = [
            OpenAIHandler(),
            AnthropicHandler(),
            GeminiHandler(),
            PerplexityHandler(),
            GrokHandler()
        ]
        
        # Report which APIs are configured
        self._report_api_status()
    
    def _report_api_status(self):
        """Print status of API configurations"""
        print("\n" + "=" * 60)
        print("API STATUS")
        print("=" * 60)
        for handler in self.handlers:
            status = "✓ ENABLED" if handler.enabled else "✗ NOT CONFIGURED"
            print(f"  {handler.name}: {status}")
        print("=" * 60 + "\n")
    
    def run_iterations(self, iterations: int, prompt_type: str = "contextual") -> list:
        """
        Run specified number of iterations across all enabled APIs
        
        Args:
            iterations: Number of times to run each prompt (e.g., 20, 30, 50)
            prompt_type: 'contextual' or 'minimal'
        
        Returns:
            List of all results
        """
        # Select prompt template
        template = PROMPT_CONTEXTUAL if prompt_type == "contextual" else PROMPT_MINIMAL
        full_prompt = template.format(focus_group_data=self.focus_group_data)
        
        results = []
        enabled_handlers = [h for h in self.handlers if h.enabled]
        
        if not enabled_handlers:
            print("ERROR: No APIs are configured. Please set API keys.")
            return results
        
        total_requests = iterations * len(enabled_handlers)
        current_request = 0
        
        print(f"Starting {iterations} iterations across {len(enabled_handlers)} APIs")
        print(f"Prompt type: {prompt_type}")
        print(f"Total requests: {total_requests}")
        print("-" * 60)
        
        for iteration in range(1, iterations + 1):
            for handler in enabled_handlers:
                current_request += 1
                print(f"[{current_request}/{total_requests}] {handler.name} - Iteration {iteration}...", end=" ")
                
                response = handler.query(full_prompt)
                
                # Add metadata
                response["iteration"] = iteration
                response["total_iterations"] = iterations
                response["prompt_type"] = prompt_type
                response["iteration_batch"] = f"{iterations}x"
                
                results.append(response)
                
                status = "OK" if response["success"] else f"FAIL: {response['error'][:50]}"
                print(status)
                
                # Rate limiting
                time.sleep(Config.REQUEST_DELAY)
        
        return results
    
    def save_results(self, results: list, filename: str = None) -> Path:
        """Save results to CSV file"""
        if not results:
            print("No results to save.")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"codebook_results_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        fieldnames = [
            "iteration",
            "iteration_batch",
            "total_iterations",
            "prompt_type",
            "model",
            "success",
            "error",
            "tokens_input",
            "tokens_output",
            "timestamp",
            "content"
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nResults saved to: {filepath}")
        return filepath
    
    def run_full_experiment(self, iteration_counts: list = None, prompt_types: list = None) -> Path:
        """
        Run full experiment with multiple iteration counts and prompt types
        
        Args:
            iteration_counts: List of iteration counts, e.g., [20, 30, 50]
            prompt_types: List of prompt types, e.g., ['contextual', 'minimal']
        """
        if iteration_counts is None:
            iteration_counts = [20, 30, 50]
        if prompt_types is None:
            prompt_types = ["contextual", "minimal"]
        
        all_results = []
        
        for prompt_type in prompt_types:
            for count in iteration_counts:
                print(f"\n{'=' * 60}")
                print(f"RUNNING: {count} iterations with {prompt_type} prompt")
                print(f"{'=' * 60}")
                
                results = self.run_iterations(count, prompt_type)
                all_results.extend(results)
        
        # Save combined results
        return self.save_results(all_results, "full_experiment_results.csv")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_focus_group_data(filepath: str) -> str:
    """Load focus group data from file"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Focus group data file not found: {filepath}")
    
    return path.read_text(encoding="utf-8")


def setup_env_file():
    """Create a template .env file for API keys"""
    env_template = """# API Keys for AI Codebook Generator
# Copy this file to .env and fill in your keys

OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
XAI_API_KEY=your_xai_grok_key_here
"""
    
    env_path = Path(".env.template")
    env_path.write_text(env_template)
    print(f"Created {env_path} - copy to .env and add your API keys")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate codebooks using multiple AI APIs for qualitative analysis research"
    )
    parser.add_argument(
        "--data", "-d",
        type=str,
        required=True,
        help="Path to focus group data file"
    )
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        nargs="+",
        default=[20],
        help="Number of iterations (can specify multiple: -i 20 30 50)"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        choices=["contextual", "minimal", "both"],
        default="both",
        help="Prompt type to use"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./output",
        help="Output directory for results"
    )
    parser.add_argument(
        "--setup-env",
        action="store_true",
        help="Create template .env file for API keys"
    )
    
    args = parser.parse_args()
    
    if args.setup_env:
        setup_env_file()
        return
    
    # Load focus group data
    try:
        focus_group_data = load_focus_group_data(args.data)
        print(f"Loaded focus group data: {len(focus_group_data)} characters")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Initialize generator
    generator = CodebookGenerator(
        focus_group_data=focus_group_data,
        output_dir=Path(args.output)
    )
    
    # Determine prompt types
    if args.prompt == "both":
        prompt_types = ["contextual", "minimal"]
    else:
        prompt_types = [args.prompt]
    
    # Run experiment
    generator.run_full_experiment(
        iteration_counts=args.iterations,
        prompt_types=prompt_types
    )


if __name__ == "__main__":
    main()
