# "https://docs.chaicode.com/"

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vector_cloud_db import add_data


# loader = WebBaseLoader("https://docs.chaicode.com/")

loader_multiple_pages = WebBaseLoader(
    ["https://docs.chaicode.com/","https://docs.chaicode.com/youtube/getting-started/","https://docs.chaicode.com/youtube/chai-aur-html/welcome/","https://docs.chaicode.com/youtube/chai-aur-html/introduction/","https://docs.chaicode.com/youtube/chai-aur-html/emmit-crash-course/","https://docs.chaicode.com/youtube/chai-aur-html/html-tags/","https://docs.chaicode.com/youtube/chai-aur-git/welcome/","https://docs.chaicode.com/youtube/chai-aur-git/introduction/","https://docs.chaicode.com/youtube/chai-aur-git/terminology/","https://docs.chaicode.com/youtube/chai-aur-git/behind-the-scenes/","https://docs.chaicode.com/youtube/chai-aur-git/branches/","https://docs.chaicode.com/youtube/chai-aur-git/diff-stash-tags/","https://docs.chaicode.com/youtube/chai-aur-git/managing-history/","https://docs.chaicode.com/youtube/chai-aur-git/github/","https://docs.chaicode.com/youtube/chai-aur-c/welcome/","https://docs.chaicode.com/youtube/chai-aur-c/introduction/","https://docs.chaicode.com/youtube/chai-aur-c/hello-world/","https://docs.chaicode.com/youtube/chai-aur-c/variables-and-constants/","https://docs.chaicode.com/youtube/chai-aur-c/data-types/"]
)

docs = loader_multiple_pages.load()


# print(docs[8])
# print(docs[8].metadata.get('description'))



for data in docs:
    print(data.metadata.get('description'))
    collection_name = data.metadata.get('description')
    text_splitters = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    chunks = text_splitters.split_documents([data])

    print(f"--------Inject--Completed--for---{collection_name}---------",'\n\n',"---------------work-in-progress------------",'\n\n')

    add_data(collection_name,chunks)


print("--------------INJECTION-----COMPLETED--------------------")