import os
import platform
from collections import Counter

def limpar_tela():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def obter_opcao_numerada(pergunta, opcoes):
    print(pergunta)
    
    opcoes_com_outro = list(opcoes)
    if "Risco" not in pergunta and "Status" not in pergunta:
        opcoes_com_outro.append("Outro (descrever)")

    for i, opcao in enumerate(opcoes_com_outro, 1):
        print(f"  [{i}] {opcao}")
    
    while True:
        try:
            escolha = int(input("\nSua opção: "))
            if 1 <= escolha <= len(opcoes_com_outro):
                return opcoes_com_outro[escolha - 1]
            else:
                print(f"Erro: Por favor, insira um número entre 1 e {len(opcoes_com_outro)}.")
        except ValueError:
            print("Erro: Por favor, insira um número válido.")

def criar_processo():
    limpar_tela()
    processo = {} # Cria um dicionário local para este processo

    print("=========================================")
    print("     SISTEMA DE CADASTRO DE PROCESSOS    ")
    print("=========================================\n")
    print("Preencha os campos de informações gerais do tratamento de dados.\n")

    #Coleta de dados
    departamentos_disponiveis = ["Comercial","Desenvolvimento","Financeiro","Recursos Humanos","Suprimentos"]
    processo['departamento'] = obter_opcao_numerada("Selecione o departamento:", departamentos_disponiveis)
    print("-" * 20)

    processo['codigo'] = input("Identificador único do registro: ")
    processo['versao'] = input("Versão do processamento (padrão: 0): ") or "0"
    print("-" * 20)
    
    processo['nome_processo'] = input("Nome do processo que vamos mapear: ")
    print("-" * 20)
    
    origens_conhecidas = [
        "O próprio titular fornece os dados",
        "Outro departamento compartilha os dados",
    ]
    origem_escolhida = obter_opcao_numerada("De onde vêm os dados (origem):", origens_conhecidas)
    
    if origem_escolhida == "Outro (descrever)":
        processo['origem_dados'] = input("Por favor, descreva a nova origem dos dados: ")
    else:
        processo['origem_dados'] = origem_escolhida
    print("-" * 20)

    print("--- Por que o dado é tratado? (Finalidade) ---")
    processo['finalidade'] = input("> ")
    print("-" * 20)

    opcoes_armazenamento = ["Definido", "Indefinido", "Permanente"]
    processo['tempo_armazenamento'] = obter_opcao_numerada("Tempo de armazenamento:", opcoes_armazenamento)
    print("-" * 20)

    #Dashboard
    
    print("--- Informações para o Dashboard ---")
    
    # Campo 1: Risco
    niveis_risco = ["Risco baixo", "Risco médio", "Risco alto", "Risco severo"]
    processo['risco'] = obter_opcao_numerada("Qual o nível de risco desse processo?", niveis_risco)
    
    # Campo 2: Status
    status_disponiveis = ["Aprovados", "Revisão LIA", "Pendente", "Em Revisão", "Reprovados", "Inativos"]
    processo['status'] = obter_opcao_numerada("Qual o status atual desse processo?", status_disponiveis)
    
    print("-" * 20)

    #Resumo
    limpar_tela()
    print("=========================================")
    print("      PROCESSO CADASTRADO COM SUCESSO!     ")
    print("=========================================\n")
    
    print(f"Departamento: {processo.get('departamento', 'N/A')}")
    print(f"Código: {processo.get('codigo', 'N/A')}")
    print(f"Nome do Processo: {processo.get('nome_processo', 'N/A')}")
    print(f"Origem dos Dados: {processo.get('origem_dados', 'N/A')}")
    print(f"Finalidade: {processo.get('finalidade', 'N/A')}")
    print(f"Tempo de Armazenamento: {processo.get('tempo_armazenamento', 'N/A')}")
    print(f"Nível de Risco: {processo.get('risco', 'N/A')}")
    print(f"Status: {processo.get('status', 'N/A')}")
    
    print("\n=========================================")
    
    # Retorna o dicionário preenchido
    return processo

def mostrar_dashboard(banco_de_processos):
    """
    Lê a lista de todos os processos e exibe o dashboard agregado.
    """
    limpar_tela()
    
    # 1. Contar os dados
    total_processos = len(banco_de_processos)
    
    # Contadores para status e risco
    contagem_status = Counter(p.get('status', 'N/A') for p in banco_de_processos)
    contagem_risco = Counter(p.get('risco', 'N/A') for p in banco_de_processos)
    
    # Calcula Ativos vs Inativos
    inativos = contagem_status.get('Inativos', 0)
    ativos = total_processos - inativos
    
    # Calcula o total de processos que *têm* um risco definido
    total_com_risco = sum(contagem_risco[r] for r in ["Risco baixo", "Risco médio", "Risco alto", "Risco severo"])

    # 2. Exibir o Dashboard
    print("##################################################")
    print("#           DASHBOARD DE PROCESSOS (CLI)           #")
    print("##################################################")

    print("\n==================================================")
    print(" VISÃO GERAL")
    print("==================================================")
    print(f" PROCESSOS ATIVOS:   {ativos}")
    print(f" PROCESSOS INATIVOS:  {inativos}")

    print("\n==================================================")
    print(" PROCESSOS POR RISCO")
    print("==================================================")
    if total_com_risco > 0:
        print(f" (Contagem baseada em {total_com_risco} processos com risco definido)\n")
        
        # Define os rótulos e busca a contagem de cada um
        riscos = {
            "Risco baixo": contagem_risco.get("Risco baixo", 0),
            "Risco médio": contagem_risco.get("Risco médio", 0),
            "Risco alto": contagem_risco.get("Risco alto", 0),
            "Risco severo": contagem_risco.get("Risco severo", 0)
        }
        
        # Encontra o comprimento do rótulo mais longo para alinhar o gráfico
        max_label_len = max(len(r) for r in riscos)
        
        for risco, contagem in riscos.items():
            barra = "■" * contagem
            print(f"  {risco.ljust(max_label_len)}: {str(contagem).rjust(2)} | {barra}")
            
    else:
        print(" (Nenhum processo com risco cadastrado)")

    print("\n==================================================")
    print(" STATUS DOS PROCESSOS")
    print("==================================================")
    print(f" (Total geral: {total_processos} processos)\n")

    # Lista completa de status para exibir em ordem
    status_ordenados = [
        ("Aprovados", "[Verde]"),
        ("Revisão LIA", "[Azul C.]"),
        ("Pendente", "[Azul E.]"),
        ("Em Revisão", "[Amarelo]"),
        ("Reprovados", "[Vermelho]"),
        ("Inativos", "[Cinza]")
    ]

    print(" [Status]           [Contagem]   [Percentual]")
    print(" --------------------------------------------")
    
    if total_processos == 0:
        print("     Nenhum processo cadastrado.")
    else:
        for status_nome, status_cor in status_ordenados:
            contagem = contagem_status.get(status_nome, 0)
            percentual = (contagem / total_processos) * 100
            
            # Formata o rótulo para alinhamento
            rotulo_completo = f"{status_cor} {status_nome}"
            print(f" {rotulo_completo.ljust(17)}: {str(contagem).rjust(5)}       ({percentual:5.1f}%)")

    print("\n##################################################")

# --- Função Principal (Menu) ---

def main():
    """
    Menu principal que gerencia a lista de processos.
    """
    banco_de_processos = [] # Nosso "banco de dados" em memória

    while True:
        limpar_tela()
        print("=========================================")
        print("           MENU PRINCIPAL             ")
        print("=========================================\n")
        print(" [1] Criar novo processo")
        print(" [2] Ver Dashboard de processos")
        print(" [3] Sair")
        
        escolha = input("\nEscolha uma opção: ")
        
        if escolha == '1':
            # Chama a função de criar e armazena o resultado
            novo_processo = criar_processo()
            banco_de_processos.append(novo_processo)
            
            input("\nPressione Enter para voltar ao menu...")
            
        elif escolha == '2':
            # Passa o "banco de dados" para a função de dashboard
            mostrar_dashboard(banco_de_processos)
            input("\nPressione Enter para voltar ao menu...")
            
        elif escolha == '3':
            print("Saindo...")
            break
            
        else:
            print("Opção inválida!")
            input("\nPressione Enter para tentar novamente...")

if __name__ == "__main__":
    main()