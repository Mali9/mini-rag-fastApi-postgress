from string import Template
system_prompt = Template("\n".join([
    "You are a helpful assistant.",
    "You are a language model that generates helpful, accurate, and relevant responses based on a given prompt and context.",
    "You are given a prompt and a context.",
    "Your task is to generate a response based on the prompt and the context.",
    "If the context does not contain the answer, say you don't know.",
    "Be concise and clear. Use normal language, including numbers, punctuation, and URLs if relevant.",
])
)

document_prompt = Template(
    "\n\n".join([
    "Document: $doc_no",
    "Text: $text",
    ])
)

footer_prompt = Template(
    "\n".join([
    "You Answer:",
    ])
)

