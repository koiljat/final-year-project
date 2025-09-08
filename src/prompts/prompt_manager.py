import yaml
from langchain.prompts import PromptTemplate

import os
class PromptManager:
    def __init__(self, filepath: str=None):
        if filepath is None:
            base_dir = os.path.dirname(__file__)
            filepath = os.path.join(base_dir, "prompts.yaml")
        with open(filepath, "r") as f:
            self.prompts = yaml.safe_load(f)


    def get(self, key: str) -> PromptTemplate:
        if key not in self.prompts:
            raise ValueError(f"Prompt '{key}' not found in prompts.yaml")
        return PromptTemplate(
            input_variables=["text"],
            template=self.prompts[key]
        )

if __name__ == "__main__":
    pm = PromptManager()
    prompt = pm.get("default").format(text="This is a test")
    print(prompt)