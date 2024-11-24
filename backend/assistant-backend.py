from openai import OpenAI
client = OpenAI()
assistant_id = "asst_IDASp9o2BX2zy7hzMTeJGCz6"
assistant = client.beta.assistants.retrieve(assistant_id = assistant_id)
#print(assistant)


def destroyThread(thread_id: str) -> bool:
    thread = client.beta.threads.retrieve(thread_id = thread_id)
    store_response = client.beta.vector_stores.delete(thread.tool_resources.file_search.vector_store_ids[0])
    response = client.beta.threads.delete(thread_id = thread_id)
    if response.deleted and store_response.deleted:
        return True
    else:
        return False

def analyzeFile(file, instructions:str, id_thread = "", message:str = "test") -> (str, str):
    uploaded = client.files.create(file = file, purpose="assistants")
    #global assistant
    if not id_thread:
        thread = client.beta.threads.create(messages=[
            {
                "role" : "user",
                "content" : "Ignore this message, just analyze the provided file using the instructions.",
                "attachments" : [
                    {"file_id" : uploaded.id, "tools" : [{"type" : "file_search"}]}
                ]

            }
        ])
        id_thread = thread.id
        #print(id_thread)
        #print(thread.tool_resources.file_search.vector_store_ids)
    else:
        thread = client.beta.threads.retrieve(id_thread)
        vector_store_files = client.beta.vector_stores.files.list(thread.tool_resources.file_search.vector_store_ids[0])
        for file in vector_store_files:
            client.beta.vector_stores.files.delete(vector_store_id=thread.tool_resources.file_search.vector_store_ids[0], file_id=file.id)
        new_message = client.beta.threads.messages.create(
            id_thread,
            role="user",
            content=message,
            attachments=[{"file_id" : uploaded.id, "tools" : [{"type":"file_search"}]}]
            )
    run = client.beta.threads.runs.create_and_poll(thread_id = id_thread, assistant_id = assistant_id, additional_instructions=instructions)
    messages = client.beta.threads.messages.list(
        thread_id=id_thread,
    )
    #print(messages.data[0].content[0].text.value)
    return messages.data[0].content[0].text.value, id_thread

def chat(id_thread:str, message:str) -> str:
    thread = client.beta.threads.retrieve(id_thread)
    new_message = client.beta.threads.messages.create(
        id_thread,
        role="user",
        content=message
    )
    run = client.beta.threads.runs.create_and_poll(thread_id = id_thread, assistant_id = assistant_id)
    messages = client.beta.threads.messages.list(thread_id=id_thread)
    return messages.data[0].content[0].text.value

def getMessages(id_thread:str) -> list:
    return client.beta.threads.messages.list(id_thread)