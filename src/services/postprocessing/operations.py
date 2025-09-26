from ..postprocessing.base import BasePostProcessor

class SimplifyProcessor(BasePostProcessor):
    def process(self, text: str) -> str:
        prompt = self.prompt_manager.get("simplify").format(text=text)
        return self.run(prompt)


class ShortenProcessor(BasePostProcessor):
    def process(self, text: str) -> str:
        prompt = self.prompt_manager.get("shorten").format(text=text)
        return self.run(prompt)


class RephraseProcessor(BasePostProcessor):
    def process(self, text: str) -> str:
        prompt = self.prompt_manager.get("rephrase").format(text=text)
        return self.run(prompt)


class ExpandProcessor(BasePostProcessor):
    def process(self, text: str) -> str:
        prompt = self.prompt_manager.get("expand").format(text=text)
        return self.run(prompt)
