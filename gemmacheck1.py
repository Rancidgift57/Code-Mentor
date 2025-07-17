from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import os

# Ensure you are logged in to Hugging Face if accessing private models
# login(token=os.environ.get("HF_TOKEN")) # Uncomment and set HF_TOKEN environment variable if needed

model_id = "google/gemma-1.1-2b-it"  # or use 3b if your system supports it

# STEP 3: Load tokenizer and model
print(f"Loading tokenizer and model: {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
print("Model loaded successfully.")

# STEP 4: Create pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# STEP 5: Prompt and generate
# Define the code snippet to be analyzed
code_to_analyze = """
def add_numbers(a, b):
    result = a + b
    return result

print(add_numbers(5))
"""

# Construct the prompt for the model
# We explicitly ask for three hints before the solution
prompt = f"""You are a Python code assistant. Review the following code and point out any errors or bugs it may contain.
Before revealing the solution, provide exactly three distinct hints to help solve the error.
After the hints, provide the corrected code.

Code to review:
```python
{code_to_analyze}
```
"""

print("\nSending prompt to the model for analysis...")
output = pipe(prompt, max_new_tokens=200, do_sample=True, temperature=0.7, top_p=0.95)

# STEP 6: Show result
# The generated text will contain the analysis, hints, and solution
generated_text = output[0]["generated_text"]

# Extract only the model's response, removing the initial prompt repetition
# The model might repeat the prompt, so we find where its actual response starts.
response_start_index = generated_text.find("```python\n")
if response_start_index != -1:
    # Find the end of the input code block in the generated text
    end_of_input_code = generated_text.find("```\n", response_start_index)
    if end_of_input_code != -1:
        # The actual response should start after the input code block
        # Add 3 for '```\n'
        actual_response = generated_text[end_of_input_code + 4:].strip()
    else:
        actual_response = generated_text # Fallback if marker not found
else:
    actual_response = generated_text # Fallback if marker not found

print("\n--- Model's Analysis ---")
print(actual_response)
print("------------------------")

