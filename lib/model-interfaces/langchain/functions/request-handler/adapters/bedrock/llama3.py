import genai_core.clients

# from langchain.llms import Bedrock (pending https://github.com/langchain-ai/langchain/issues/13316)
from .base import Bedrock

from langchain.prompts.prompt import PromptTemplate

from ..shared.meta.llama3_instruct import Llama3ConversationBufferMemory

from ..base import ModelAdapter
from genai_core.registry import registry

BEGIN_OF_TEXT = "<|begin_of_text|>"
SYSTEM_HEADER = "<|start_header_id|>system<|end_header_id|>"
USER_HEADER = "<|start_header_id|>user<|end_header_id|>"
ASSISTANT_HEADER = "<|start_header_id|>assistant<|end_header_id|>"
EOD = "<|eot_id|>"


class BedrockMetaLLama3InstructAdapter(ModelAdapter):
    def __init__(self, model_id, *args, **kwargs):
        self.model_id = model_id

        super().__init__(*args, **kwargs)

    def get_memory(self, output_key=None, return_messages=False):
        return Llama3ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=self.chat_history,
            return_messages=return_messages,
            output_key=output_key,
        )

    def get_llm(self, model_kwargs={}):
        bedrock = genai_core.clients.get_bedrock_client()

        params = {}
        if "temperature" in model_kwargs:
            params["temperature"] = model_kwargs["temperature"]
        if "topP" in model_kwargs:
            params["top_p"] = model_kwargs["topP"]
        if "maxTokens" in model_kwargs:
            params["max_gen_len"] = model_kwargs["maxTokens"]

        return Bedrock(
            client=bedrock,
            model_id=self.model_id,
            model_kwargs=params,
            streaming=model_kwargs.get("streaming", False),
            callbacks=[self.callback_handler],
        )

    def get_prompt(self):
        Llama3Prompt = f"""{BEGIN_OF_TEXT}{SYSTEM_HEADER}
{self.inject_prompt}
You are an helpful assistant that provides concise answers to user questions with as little sentences as possible and at maximum 3 sentences. You do not repeat yourself. You avoid bulleted list or emojis.{EOD}{{chat_history}}{USER_HEADER}

{{input}}{EOD}{ASSISTANT_HEADER}"""
        
        Llama3PromptTemplate = PromptTemplate.from_template(Llama3Prompt)
        return Llama3PromptTemplate

    def get_qa_prompt(self):
        Llama3QAPrompt = f"""{BEGIN_OF_TEXT}{SYSTEM_HEADER}
{self.inject_prompt}
Use the following conversation history and pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. You do not repeat yourself. You avoid bulleted list or emojis.{EOD}{{chat_history}}{USER_HEADER}

Context: {{context}}

{{question}}{EOD}{ASSISTANT_HEADER}"""
        
        Llama3QAPromptTemplate = PromptTemplate.from_template(Llama3QAPrompt)
        return Llama3QAPromptTemplate

    def get_condense_question_prompt(self):
        Llama3CondensedQAPrompt = f"""{BEGIN_OF_TEXT}{SYSTEM_HEADER}
{self.inject_prompt}
Given the following conversation and the question at the end, rephrase the follow up input to be a standalone question, in the same language as the follow up input. You do not repeat yourself. You avoid bulleted list or emojis.{EOD}{{chat_history}}{USER_HEADER}

{{question}}{EOD}{ASSISTANT_HEADER}"""
        
        Llama3CondensedQAPromptTemplate = PromptTemplate.from_template(Llama3CondensedQAPrompt)
        return Llama3CondensedQAPromptTemplate


# Register the adapter
registry.register(

    r"^bedrock.meta.llama3-.*-instruct.*",
    BedrockMetaLLama3InstructAdapter,
)
