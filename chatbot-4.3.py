# -*- coding: utf-8 -*-


#comando necessário para inicialização da comunicação: vertexai.init(project=project_id, location=location)

# Resumo geral de modificações: implementação de nova biblioteca para o funcionamento da "nova" api que também funciona com a Gemini 1.5, o que mudou? É a Vertex API
# ela é mais rápida para geração de respostas, é possível definir a localização do servidor e limitar o acesso a ela pelo ID de projeto, também é possível 
# monitoramento de tráfego de rede, além de abrir possibilidade para acesso simultâneo o que não era possível pela API padrão que usávamos, é necessário consumo de crédito
# porém o ganho potencial pelas melhorias de serviço, fazem com que valha a pena.

import os
import subprocess
import sys
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from flask import Flask, request, Response, jsonify

# NOVO: Importações necessárias para a Vertex AI
import vertexai
from vertexai.generative_models import GenerativeModel

# =================================================================
# SEÇÃO 1: CONFIGURAÇÃO E INICIALIZAÇÃO
# =================================================================

def instalar_dependencias():
    """Tenta instalar as dependências listadas no arquivo requirements.txt."""
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", caminho])
        print("Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        print("Erro ao instalar dependências:", e)
        sys.exit(1)
    except FileNotFoundError:
        print("AVISO: Arquivo requirements.txt não encontrado. Pulando a instalação de dependências.")

# Descomente a linha abaixo se precisar instalar as dependências automaticamente
# instalar_dependencias()

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# MODIFICADO: Carrega as variáveis para Vertex AI e Twilio
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Validação das variáveis de ambiente
if not all([project_id, location, account_sid, auth_token]):
    print("ERRO: Verifique se as variáveis GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, TWILIO_ACCOUNT_SID e TWILIO_AUTH_TOKEN estão no arquivo .env")
    sys.exit(1)

# Configura as APIs e o modelo de IA
try:
    # NOVO: Inicializa a Vertex AI com seu projeto e localização
    vertexai.init(project=project_id, location=location)
    
    cliente = Client(account_sid, auth_token)
except Exception as e:
    print(f"Erro ao configurar as APIs: {e}")
    sys.exit(1)

# Informações de contato e Twilio
numero_twilio = 'whatsapp:+14155238886'
meu_numero = 'whatsapp:+5514999060870' # Substitua pelo seu número para testes, se necessário

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Contexto do assistente virtual para a DPNet (permanece o mesmo)
contexto = """
Você é um assistente virtual da empresa **DPO.net**, especializado em proteção de dados pessoais,
conformidade com a LGPD (Lei Geral de Proteção de Dados), consultoria em segurança da informação
e assessoria jurídica voltada à privacidade.

Seu papel é fornecer respostas **claras, objetivas e profissionais**, sempre em tom cordial,
institucional e confiável. Sempre que possível, destaque os diferenciais da DPO.net.

- Se a pergunta for sobre temas fora do escopo da DPO.net, responda educadamente:
  "Posso responder apenas sobre os serviços e especializações da DPO.net."

- Se a pergunta for ofensiva, inadequada ou não relacionada, responda:
  "Por favor, mantenha o respeito. Estou aqui para ajudar com informações sobre a DPO.net."

- Informações básicas a manter:
  • E-mail de contato: contato@dpnet.com.br
  • Suporte: suporte@dpnet.com.br
  • Horário de atendimento: segunda a sexta-feira, das 9h às 18h
  • Site oficial: www.dpnet.com.br

- Áreas de atuação da DPO.net:
  • Consultoria em LGPD e privacidade
  • Assessoria jurídica especializada em proteção de dados
  • Implementação de programas de governança em privacidade
  • Treinamentos e capacitação sobre LGPD
  • Suporte contínuo para adequação regulatória

Use sempre uma linguagem **profissional, didática e resumida**,
evitando respostas muito longas ou excessivamente técnicas.
"""

# MODIFICADO: A inicialização do modelo agora usa a classe da Vertex AI
# A estrutura é a mesma, o que facilita a migração.
modelo = GenerativeModel(
    "gemini-1.5-pro",
    system_instruction=contexto
)

# MARCAÇÃO DE VERSÃO API ↑




# =================================================================
# SEÇÃO 2: LÓGICA DO CHATBOT
# =================================================================

# Frases que, se presentes na resposta da IA, indicam que ela não soube responder
# e que devemos tentar usar uma macro como alternativa.
GATILHOS_FALLBACK = [
    "posso responder apenas sobre",
    "fora do escopo da dpo.net",
    "não tenho informações sobre esse assunto"
]

def verificar_macros(pergunta):
    """Verifica se a pergunta corresponde a uma palavra-chave para respostas prontas."""
    macros = {
        "contato": "Para entrar em contato conosco, envie um e-mail para contato@dpnet.com.br.",
        "suporte": "Nosso suporte pode ser acessado pelo e-mail suporte@dpnet.com.br.",
        "horário": "Nosso horário de atendimento é de segunda a sexta-feira, das 9h às 18h.",
        "site": "Você pode acessar nosso site em www.dpnet.com.br para mais informações.",
    }
    pergunta_lower = pergunta.lower()
    for chave, resposta in macros.items():
        if chave in pergunta_lower:
            return resposta
    return None

def obter_resposta_com_vertexai(pergunta): # MODIFICADO: Nome da função para clareza
    """
    Gera uma resposta usando o modelo de IA da Vertex AI.
    A chamada foi simplificada, pois o contexto já está no modelo.
    """
    try:
        # A chamada e o objeto de resposta são idênticos, tornando a migração simples.
        resposta = modelo.generate_content(pergunta)
        
        # Acessa corretamente o texto retornado pela API
        if resposta and resposta.candidates and resposta.candidates[0].content.parts:
            return resposta.candidates[0].content.parts[0].text
            
        return "Não foi possível gerar uma resposta no momento. Por favor, tente novamente."
    except Exception as e:
        # MODIFICADO: Mensagem de erro para refletir a nova API
        print(f"ERRO NA API Vertex AI: {str(e)}")
        return f"Ocorreu um erro ao comunicar com a IA. Detalhe: {str(e)}"

def obter_resposta(pergunta):
    """
    Função principal com a NOVA LÓGICA: IA primeiro, macros como último caso.
    """
    # 1. Tenta obter a resposta da IA primeiro
    resposta_ia = obter_resposta_com_vertexai(pergunta) # MODIFICADO: Chama a nova função
    
    # 2. Verifica se a resposta da IA é uma recusa (usando os gatilhos)
    resposta_ia_lower = resposta_ia.lower()
    usar_fallback = any(gatilho in resposta_ia_lower for gatilho in GATILHOS_FALLBACK)
    
    if usar_fallback:
        # 3. Se a IA recusou, tenta encontrar uma macro como alternativa
        resposta_macro = verificar_macros(pergunta)
        if resposta_macro:
            # Se encontrou uma macro correspondente, retorna a resposta da macro
            return resposta_macro
            
    # 4. Se a IA deu uma resposta válida ou se não encontrou macro no fallback,
    #    retorna a resposta original da IA.
    return resposta_ia

# =================================================================
# SEÇÃO 3: SERVIDOR WEB E ROTAS (NENHUMA ALTERAÇÃO NECESSÁRIA AQUI)
# =================================================================

@app.route("/whatsapp", methods=["POST"])
def resposta_whatsapp():
    """Rota para receber e responder mensagens do WhatsApp via Twilio."""
    mensagem_usuario = request.values.get("Body", "").strip()
    remetente = request.values.get("From", "")
    print(f"Mensagem de {remetente}: '{mensagem_usuario}'", flush=True)
    
    if not mensagem_usuario:
        return Response(status=204)

    resposta_texto = obter_resposta(mensagem_usuario)
    print(f"Resposta gerada: '{resposta_texto}'", flush=True)
    
    twilio_response = MessagingResponse()
    twilio_response.message(resposta_texto)
    
    return Response(str(twilio_response), mimetype="application/xml")

@app.route("/chat", methods=["POST"])
def chat():
    """Rota genérica para testes de chat via JSON."""
    dados = request.get_json()
    if not dados or "pergunta" not in dados:
        return jsonify({"erro": "A chave 'pergunta' é obrigatória."}), 400
        
    pergunta = dados["pergunta"]
    if not pergunta:
        return jsonify({"erro": "O valor de 'pergunta' não pode ser vazio."}), 400
        
    resposta = obter_resposta(pergunta)
    return jsonify({"resposta": resposta})

# =================================================================
# SEÇÃO 4: EXECUÇÃO DO APLICATIVO (NENHUMA ALTERAÇÃO NECESSÁRIA AQUI)
# =================================================================

if __name__ == "__main__":
    print("Iniciando o servidor Flask para o chatbot da DPNet com Vertex AI...")
    # O uso de debug=True é recomendado apenas para desenvolvimento
    app.run(host="0.0.0.0", port=5000, debug=True)