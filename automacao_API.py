import os
from dotenv import load_dotenv
import sys
import requests
import pandas as pd

# ✅ Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class ZapSignAPI:
    def __init__(self):
        self.token = os.getenv('senha_api')
        self.base_url = 'https://api.zapsign.com.br/api/v1'

        if not self.token:
            print("❌ Erro: a variável de ambiente 'senha_api' não está configurada.")
            sys.exit(1)

        # 🔑 Header correto para autenticação
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def listar_documentos(self, page=1, folder_id=None):
        try:
            url = f'{self.base_url}/docs/?status=pending&include_signers=true&page={page}'
            if folder_id:
                url += f'&folder_id={folder_id}'
            
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao listar documentos (página {page}): {e}")
            return None

    def executar(self, arquivo_saida='signatarios_nao_assinados.xlsx', folder_id=None):
        try:
            registros = []
            page = 1
            total_docs = 0
            total_pendentes = 0

            while True:
                print(f"\n📄 Carregando página {page}...")
                documentos = self.listar_documentos(page=page, folder_id=folder_id)
                if documentos is None:
                    break

                docs_list = documentos.get('results', [])
                if not docs_list:
                    break

                for documento in docs_list:
                    total_docs += 1
                    doc_id = documento.get('id')
                    doc_nome = documento.get('name', 'Sem nome')

                    if not doc_id:
                        continue

                    print(f"   📍 [{total_docs}] {doc_nome}")

                    signatarios = documento.get('signers', [])
                    for signatario in signatarios:
                        status = signatario.get('status', '').lower()
                        # ✅ Apenas quem ainda pode assinar
                        if status in ['nao_abriu', 'abriu']:
                            total_pendentes += 1
                            registros.append({
                                'documento_id': doc_id,
                                'documento_nome': doc_nome,
                                'signatario_nome': signatario.get('name'),
                                'signatario_email': signatario.get('email'),
                                'signatario_telefone': signatario.get('phone'),
                                'link_assinatura': signatario.get('signing_url'),
                                'status': status
                            })

                # ✅ Usa o campo 'next' para continuar paginação
                if documentos.get('next'):
                    page += 1
                else:
                    break

            print(f"\n📊 RESUMO:")
            print(f"   Total de documentos em curso: {total_docs}")
            print(f"   Total de signatários pendentes: {total_pendentes}")

            if not registros:
                print("\n✅ Nenhum signatário pendente encontrado.")
                return

            df = pd.DataFrame(registros)
            df.to_excel(arquivo_saida, index=False, engine='openpyxl')
            print(f"\n✅ Arquivo salvo: {arquivo_saida}")
            print(f"📈 Total de signatários pendentes: {len(registros)}")

        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

if __name__ == '__main__':
    # 👉 Se quiser filtrar por uma pasta específica, passe o folder_id aqui
    api = ZapSignAPI()
    api.executar(folder_id=None)  # exemplo: api.executar(folder_id="abc123")
