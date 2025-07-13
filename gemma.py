from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

model_id = "google/gemma-1.1-2b-it"  # or use 3b if your system supports it

# STEP 3: Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

# STEP 4: Create pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# STEP 5: Prompt and generate
prompt = """You are a Python code assistant. Review the following code and point out any errors or bugs it may contain:

```python
def add_numbers(a, b):
    result = a + b
    return result

print(add_numbers(5))
"""
output = pipe(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)

# STEP 6: Show result
print(output[0]["generated_text"])