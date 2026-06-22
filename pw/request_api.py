from dotenv import load_dotenv
import requests
import os
import pandas as pd
import ast
load_dotenv()
def get_docs():
    token = os.getenv('senha_api')

    headers = {
        'Authorization' : f'Bearer {token}'
    }

    params = {
        'include_signers':'true',
        'status':'pending',
        'deleted': 'false',
        'folder_path': '/Contratos'
    }
    url =  'https://api.zapsign.com.br/api/v1/docs/'
    page = 1
    relatorio = []
    #while True:
    while True:
        params['page'] = page
        response = requests.get(url, params = params, headers = headers, timeout = 30)
        if response.status_code == 200:
            dados = response.json()
            documentos = dados.get('results', [])
                
            if not documentos:
                print("Fim da paginação!")
                break
            
            print(f"Página {page}: {len(documentos)} documentos")

            relatorio.extend(documentos)
            
            page += 1
        else:
            print(f"Erro: {response.status_code}")
            break
    
    return relatorio


def analizer(dados):
    dados['signers'] = dados['signers'].astype(str)
    dados['signers'] = dados['signers'].apply(ast.literal_eval)
    signers = dados.explode('signers').reset_index(drop = True)

    relat = signers.loc[
        signers['signers'].apply(
            lambda x: isinstance(x, dict) and x['status'] in ['nao_abriu', 'abriu']
        )
    ]

    nomes_desejados = {
        'LUCAS GUILHERME PEIXOTO': 'lucas',
        'DAVID DE CASTRO GOMES': 'david',
        'GABRIELLA RIBEIRO AUGUSTO DA SILVA': 'gabi',
        'JULIANA GUERRA ASNAL': 'ju'
    }

    for nome_completo, apelido in nomes_desejados.items():
        df_temp = relat.loc[relat['signers'].apply(
            lambda x: isinstance(x, dict) and x['nome'] == nome_completo
        )].copy()
        df_temp['status'] = df_temp['signers'].apply(lambda x: x['status'])
        df_temp['link'] = df_temp['signers'].apply(lambda x: x['link_para_assinar'])
        
        # 2º: AGORA selecionar as colunas desejadas
        df_temp = df_temp[['name', 'open_id', 'status', 'link']].copy()
        
        # Renomear
        df_temp = df_temp.rename(columns={
            'name': 'Nome do Contrato',
            'open_id': 'ID do contrato',
            'status': 'Status',
            'link': 'Link p/ Assinatura'
        })
        



        df_temp.to_excel(f'{apelido}_pendentes.xlsx', index=False)
        print(f"{apelido}: {len(df_temp)} pendentes salvos")

    outros = relat.loc[~relat['signers'].apply(
        lambda x: isinstance(x, dict) and x['nome'] in nomes_desejados
        
    )]
    outros.to_excel('outros_sig_pendentes.xlsx')
    print(f"Outros signatários: {len(df_temp)} pendentes salvos")

    signers.to_excel('signers.xlsx')
    relat.to_excel('relat.xlsx')



relatorio = get_docs()
analizer(relatorio)

    