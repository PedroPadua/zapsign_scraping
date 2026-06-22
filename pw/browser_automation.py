from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class BrowserAutomation(ABC):
    def __init__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
    
    @abstractmethod
    def login(self, user, password):
        pass


    
    def navigate(self, url):
        self.page.goto(url)
        self.page.wait_for_timeout(500)

    def cleanup(self):
        self.page.close()
        self.browser.close()
        self.pw.stop()

class ZapsignScrap(BrowserAutomation):


    def login(self):
        self.navigate('https://app.zapsign.com.br/')
        self.page.fill('input[inputmode = "email"]', os.getenv('email'))
        self.page.wait_for_selector('input[type="password"]', state="visible")
        self.page.fill('input[type="password"]', os.getenv('senha'))
        self.page.click('button:has-text("Entrar")')
        self.page.wait_for_url('https://app.zapsign.com.br/conta/documentos')
        # Seu login aqui
    
    def find_unfineshed_contract(self):
        self.page.wait_for_selector('text=Bison Agência')
        self.page.locator('text=Contratos').first.click()
        self.page.wait_for_selector('mat-select#mat-select-6')
        self.page.click('mat-select#mat-select-6')
        self.page.wait_for_selector('mat-option', state="visible")
        self.page.locator('mat-option:has-text("1-500")').click()
        self.page.wait_for_load_state("load")
        for _ in range(5):
            try:
                sucesso = self.page.evaluate("""
                    (selector) => {
                        const element = document.querySelector(selector);
                        if (element) {
                            element.click();
                            console.log('Clicado com sucesso');
                            return true;
                        }
                        console.log('Elemento não encontrado');
                        return false;
                    }
                """, ".filter-status > div:nth-child(2)")
                if sucesso:
                    print('clicou em Curso')
                    break
            except Exception as e: 
                print(f'Erro na tentantiva {_+1}\nTentando novamente!')
            self.page.wait_for_timeout(2000)
            
        self.page.wait_for_timeout(2000)

    def count_contracts(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(3000)  
        self.locators = self.page.locator('a.doc_item_container').all()
        self.qnt_contracts = len(self.locators)
        print(self.qnt_contracts)
    
    def get_links(self):
        relat_contratos = []
        self.login()
        self.find_unfineshed_contract()
        self.count_contracts()
        
        for idx in range(self.qnt_contracts):
            try:
                print(f"\n📍 Contrato {idx+1}/{self.qnt_contracts}")
                
                # ✅ CLICAR COM PLAYWRIGHT (não com evaluate)
                elemento = self.page.locator('a.doc_item_container').nth(idx)
                
                # ✅ Verificar se o elemento existe
                if elemento.count() == 0:
                    print(f"❌ Elemento {idx} não encontrado")
                    continue
                
                # ✅ Scroll para o elemento ficar visível
                elemento.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                
                # ✅ Clicar
                elemento.click()
                print(f"✅ Clicado com sucesso")
                
                # ✅ Aguardar navegação
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                self.page.wait_for_timeout(2000)
                
                print(f"✅ Contrato {idx+1} aberto - URL: {self.page.url}")
                
                # ✅ Extrair signatários
                signatarios = self.page.locator('div.container').all()
                
                if len(signatarios) < 2:
                    print(f'❌ Erro, não entrou no contrato (apenas {len(signatarios)} containers)')
                    self.page.go_back()
                    self.page.wait_for_timeout(2000)
                    continue
                
                # ✅ Loop pelos signatários
                for i, sig in enumerate(signatarios[1:], start=1):
                    list = sig.inner_text().split('\n')
                    list = [x for x in list if x.strip()]
                    print(f"   Signatário {i}: {list}")
                    
                    try:
                        if i == 1:
                            nm_contrato = list[0]
                            contrato_id = list[2]
                            qnt_assinados = list[-1]
                            nm_assinados = int(qnt_assinados[0])
                            total_assinaturas = int(qnt_assinados[2])
                            porc_assinados = (nm_assinados / total_assinaturas) * 100
                        else:
                            if len(list) > 3 and list[3] == 'Assinou o documento':
                                pass
                            else:
                                infos_assinatura = {
                                    'id': contrato_id,
                                    'contrato': nm_contrato,
                                    'porcentagem': porc_assinados,
                                    'nm_assinar': list[0],
                                    'link': list[2]
                                }
                                relat_contratos.append(infos_assinatura)
                    
                    except Exception as e:
                        print(f'❌ Erro na tentativa {idx+1} na leitura do documento: {e}')
                
                # ✅ Voltar
                try:
                    self.page.go_back()
                    self.page.wait_for_timeout(2000)
                except Exception as e:
                    print(f'⚠️ Erro ao voltar: {e}')
                
                print(f'✅ TOTAL DE CONTRATOS ANALISADOS: {idx+1}')
            
            except Exception as e:
                print(f'❌ Erro geral no contrato {idx+1}: {e}')
                import traceback
                traceback.print_exc()
                try:
                    self.page.go_back()
                except:
                    pass
        
        # ✅ Salvar uma única vez no final
        df_log = pd.DataFrame(relat_contratos)
        df_log.to_excel('relatório.xlsx', index=False)
        print(f'\n✅ Relatório salvo com {len(relat_contratos)} registros')



zap = ZapsignScrap()
zap.get_links()


