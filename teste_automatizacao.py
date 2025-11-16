#!/usr/bin/env python3
"""
Script de teste para validar a automação no Infinite Pay
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def teste_basico():
    """Teste básico para verificar se consegue acessar o site"""
    
    print("🧪 TESTE DE AUTOMAÇÃO - INFINITE PAY")
    print("=" * 50)
    
    # Configurar Chrome
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    
    try:
        print("🚀 Iniciando navegador...")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        
        # Executar script para remover detecção de automação
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Acessando Infinite Pay...")
        driver.get("https://app.infinitepay.io")
        
        print("⏳ Aguardando 10 segundos...")
        time.sleep(10)
        
        print("📄 Tentando acessar página de faturas...")
        driver.get("https://app.infinitepay.io/invoices")
        time.sleep(5)
        
        # Verificar se consegue encontrar o botão "Nova cobrança"
        try:
            nova_cobranca_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Nova cobrança') or contains(., 'Nova cobrança')]"))
            )
            print("✅ Botão 'Nova cobrança' encontrado!")
            
            # Verificar se está logado
            if nova_cobranca_btn.is_displayed():
                print("✅ Usuário parece estar logado")
            else:
                print("⚠️ Botão encontrado mas não visível - pode precisar fazer login")
                
        except:
            print("❌ Botão 'Nova cobrança' não encontrado - usuário provavelmente não está logado")
            print("📝 Verifique se você está logado no Infinite Pay antes de executar o script")
        
        print("\n⏰ Mantendo navegador aberto por 30 segundos para inspeção...")
        print("💡 Use este tempo para verificar se está logado e navegar manualmente")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        
    finally:
        if driver:
            print("🔒 Fechando navegador...")
            driver.quit()
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Certifique-se de estar logado no Infinite Pay")
        print("2. Execute o script principal: python automatizar_cobrancas.py")
        print("3. Monitore os logs em: cobrancas_automatizadas.log")

if __name__ == "__main__":
    teste_basico() 