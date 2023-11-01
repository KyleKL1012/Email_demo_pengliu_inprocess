import json
import os
# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


openai.api_type = "azure"
openai.api_base = config_details["OPENAI_API_BASE"]
openai.api_version = "2022-12-01"
os.environ["OPENAI_API_KEY"] = config_details["API_KEY"]
openai.api_key = config_details["API_KEY"]

import pandas as pd
from llama_index.indices.service_context import ServiceContext
from langchain.llms import AzureOpenAI
from langchain.embeddings import OpenAIEmbeddings
from llama_index import LangchainEmbedding
from llama_index import (
    StringIterableReader,
    GPTSimpleVectorIndex,
    SimpleDirectoryReader, 
    LLMPredictor,
    PromptHelper,
    ServiceContext
)

deployment_name="text-davinci-003"
llm = AzureOpenAI(deployment_name="text-davinci-003", model_kwargs={
    "api_key": openai.api_key,
    "api_base": openai.api_base,
    "api_type": openai.api_type,
    "api_version": openai.api_version,
})
llm_predictor = LLMPredictor(llm=llm)
embedding_llm = LangchainEmbedding(OpenAIEmbeddings(
    document_model_name="text-embedding-ada-002",
    query_model_name="text-davinci-003"
))
# max LLM token input size
max_input_size = 500
# set number of output tokens
num_output = 50
# set maximum chunk overlap
max_chunk_overlap = 20

from llama_index.indices.query.query_transform.base import StepDecomposeQueryTransform
step_decompose_transform = StepDecomposeQueryTransform(
    llm_predictor, verbose=True
)
prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
service_context = ServiceContext.from_defaults(
    llm_predictor=llm_predictor,
    embed_model=embedding_llm,
    prompt_helper=prompt_helper,
    chunk_size_limit=320
)

def trim_text(text):
    text=text.replace('，',' ')
    text=text.replace('。',' ')
    text=text.replace(';',' ')
    text=text.replace('；',' ')
    text=text.replace('：','： ')
    text=text.replace('》','》 ')
    text=text.replace('[',' [')
    return text

def chunks_process(input_path,output_path):
    """
    input_path: folder path contains document
    output_path: output json, stores index of chunks
    """

    with open(input_path,'r',encoding='utf-8') as f:
        lines=[trim_text(line) for line in f.readlines()]
        lines=[line[:128] for line in lines]
        #lines=f.read().strip()
        #lines=lines.split('\n\n')
        #lines=[trim_text(line) for line in lines]

    documents = StringIterableReader().load_data(texts=lines)    
    
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
    
    index.save_to_disk(output_path)
def preprocess():
    texts=[]
    df=pd.read_excel('数据-ESG三级框架指标和正负描述.xlsx',header=None)
    df[1]=df[1].str.replace('\n',' ')
    for i in range(3,len(df)):
        if df.iloc[i][1]==df.iloc[i][1]:
            class_1=df.iloc[i][1]
        if df.iloc[i][2]==df.iloc[i][2]:
            class_2=df.iloc[i][2]
        
        text=f"一级类别：{class_1}，二级类别：{class_2}，三级类别：{df.iloc[i][3]}，类别描述：{df.iloc[i][4]}"
        texts.append(text)
        print(len(text))

    with open('ESG.txt','w',encoding='utf-8')as f:
        f.write('\n'.join(texts))
    print('done')

def utf8():

    with open('ESG/ESG_index.json','r',encoding='utf-8')as f:
            js=json.load(f)
    with open('ESG/ESG_index_utf8.json','w',encoding='utf-8')as f:
        json.dump(js,f,ensure_ascii=False)

def get_embedding(index):
    doc_dict=index.index_struct.to_dict()['__data__']['doc_id_dict']
    #import pdb;pdb.set_trace()
    embeddings=[]
    nodes_id=[]
    for doc_id in doc_dict:
        nodes=index.docstore.get_nodes(doc_dict[doc_id])
        _embeddings=[]
        for node_id in doc_dict[doc_id]:

            embedding=index._vector_store.get(node_id)
            _embeddings.append(embedding)            
            texts=[node.text for node in nodes]
        embeddings.append(_embeddings)
        nodes_id.append(nodes)
    return embeddings,nodes_id

f=open('result.csv','w',encoding='utf-8')
fw=open('print.txt','w',encoding='utf-8')

from openai.embeddings_utils import  cosine_similarity
import numpy as np
def query(index_file):
    index=GPTSimpleVectorIndex.load_from_disk('ESG/ESG_index.json', service_context=service_context)  
    index.index_struct.summary='Used to classify ESG report into 3 level categories.'  

    pdf_index=GPTSimpleVectorIndex.load_from_disk(index_file, service_context=service_context)  
    
    pdf_embeddings,pdf_nodes=get_embedding(pdf_index)
    esg_embeddings,esg_nodes=get_embedding(index)
    esg_embeddings=[e[0] for e in esg_embeddings]

    pdf_nodes_unpack=[]
    for nodes in pdf_nodes:
        for node in nodes:
            pdf_nodes_unpack.append(node)
    
    for i in range(len(esg_embeddings)): 
        #print(esg_nodes[i][0].text)
        #print('___________________________')
        similarity=[]
        for j in range(len(pdf_embeddings)):
            similarity.append(cosine_similarity(pdf_embeddings[j],esg_embeddings[i]))
        similarity=np.concatenate(similarity,axis=0)
        #import pdb;pdb.set_trace()
        info=[]
        for j in np.argsort(similarity)[-1:-10:-1]:
            
            info.append(pdf_nodes_unpack[j].text)
        concat_info=" ".join(info)
        print('**************************')
        fw.write('**************************\n')
        prompt=f'''
从A,B,C三个选项中回答问题，并给出理由。
以下是从{os.path.basename(index_file).split('.')[0]}公司发布的ESG报告中抽出的关键信息，这些是否符合“{esg_nodes[i][0].text.split('三级类别')[1]}”的评价？
A. 非常符合   B. 符合   C. 不符合
信息：
{concat_info}
回答：
        '''

        completion = openai.Completion.create(prompt=prompt,temperature=0,max_tokens=100,engine=deployment_name)
        # print the completion
        print(prompt)
        fw.write(f'{prompt}\n')
        answer=completion.choices[0].text.strip(" \n")
        print(answer)
        fw.write(f'{answer}\n')
        if 'A' in answer:
            rate='非常符合'
        elif 'B' in answer:
            rate='符合'
        else:
            rate='不符合'
        f.write(f"{os.path.basename(index_file).split('.')[0]},{esg_nodes[i][0].text.split('类别：')[1].split('，')[0]},{esg_nodes[i][0].text.split('类别：')[2].split('，')[0]},{esg_nodes[i][0].text.split('类别：')[3][:-2]},{rate}\n")


if __name__=='__main__0':
    # to make embedding and chunks
    for root,dirs,files in os.walk('dataset'):
        for file in files:
            if file.endswith('txt'):
                path=os.path.join(root,file)
                chunks_process(path, os.path.join(root,file.split('.')[0]+'.index'))

if __name__=='__main__':
    for root,dirs,files in os.walk('dataset'):
        for file in files:
            if file.endswith('index'):
                path=os.path.join(root,file)
                query(path)