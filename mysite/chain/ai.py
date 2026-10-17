from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

search_router = APIRouter(prefix="/med-chat", tags=["MedCare AI Chat"])


class QuestionSchema(BaseModel):
    question: str



BASE_DIR = Path(__file__).resolve().parent
kb_path = BASE_DIR / "medcare.txt"

if kb_path.exists():
    loader = TextLoader(kb_path, encoding="utf-8")
    document = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(document)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
else:
    vector_store = None



def check_question(data):
    question = data["question"].lower()
    forbidden_words = ["бомба", "оружие", "наркотик", "убить", "взломать", "вирус", "террорист"]

    for word in forbidden_words:
        if word in question:
            data["allowed"] = False
            return data

    data["allowed"] = True
    return data



prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Сиз MedCare AI клиникасынын расмий жана кесипкөй ассистентисиз.\n"
        "Сиздин жалгыз милдетиңиз төмөндө берилген База знанийдеги маалыматка гана таянып жооп берүү.\n\n"
        "ПРОМПТ ЖАНА ЖООП БЕРҮҮ ЭРЕЖЕЛЕРИ:\n"
        "1. ЖООПТУН УЗУНДУГУ: Жообуңуз максимум 2 же 3 сүйлөмдөн гана турушу керек. Длинный же ашыкча текст жазбаңыз.\n"
        "2. АШЫКЧА СИМВОЛДОРГО ТЫЮУ: Жоопто эч кандай кошумча символдорду же маркдаун белгилерин колдонбоңуз. Жылдызча, торчо, дефис, кашаа, кош чекит же тырмакча сыяктуу белгилерди таптакыр кошпоңуз. Текст гана болушу керек.\n"
        "3. ОСНОВНОЙ МЕНИН БАЗАМ: Өзүңүздөн бааларды, дарыгерлерди, адистиктерди же графиктерди ойлоп таппаңыз же божомолдобоңуз.\n"
        "4. МААЛЫМАТ ЖОК БОЛСО: Эгерде суроого жооп База знанийде жок болсо, так ушул сүйлөмдү гана кайтарыңыз: Кечиресиз, бул тууралуу маалымат базабызда жок.\n"
        "5. ТИЛ ЖАНА ТОН: Текстти сылык, так жана бир гана кыргыз тилинде жазыңыз.\n"
        "6. МЕДИЦИНАЛЫК КЕҢЕШ: Эч качан диагноз койбоңуз жана дары-дармек жазып бербеңиз.\n\n"
        "База знаний маалыматы:\n{base_data}"
    ),
    (
        "human",
        "{question}"
    )
])


model = ChatOllama(model="llama3.2:latest",temperature=0.0)



def search_documents(data):
    if vector_store:
        documents = vector_store.similarity_search(data["question"], k=4)
        data["base_data"] = "\n".join(doc.page_content for doc in documents)
    else:
        data["base_data"] = "База знаний табылган жок."
    return data



chain = (RunnableLambda(check_question)| RunnableLambda(search_documents)| prompt| model| StrOutputParser())



@search_router.post("/ask")
async def ask_med_ai(question: QuestionSchema):
    data = {"question": question.question}

    checked_data = check_question(data)
    if not checked_data["allowed"]:
        raise HTTPException(
            status_code=400,
            detail="Суроо тыюу салынган сөздөрдү камтыйт.")

    answer = chain.invoke(data)

    return {
        "status": "success",
        "answer": answer}