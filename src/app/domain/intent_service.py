import re
import json
from app.infra.logger_adapter import logger
from typing import Dict, Any, List
from app.infra.llm_adapter import query_llm
from app.domain.state_repository import get_user_state, update_user_state

SYSTEM_PROMPT = """
Você é um assistente financeiro conversando com o usuário.

Sua tarefa é analisar a conversa anterior e a mensagem mais recente do usuário, e retornar um JSON com:
- intent: a intenção da ação - "transfer", "get_balance", "get_transactions", "get_help" ou "unknown"
- entities: as entidades extraídas
- missing_entities: entidades ainda não identificadas
- next_question: a próxima pergunta necessária para solicitar alguma entidade faltante

Possíveis intenções são EXCLUSIVAMENTE:

- "transfer": quando o usuário quer enviar dinheiro
- "get_balance": quando o usuário quer saber o saldo da conta
- "get_transactions": quando o usuário quer ver o histórico ou extrato
- "get_help": quando o usuário pede ajuda ou quer saber os serviços, comandos ou operações que você oferece
- "unknown": quando você não consegue identificar nenhuma das intenções acima

Identifique sempre a intenção mais apropriada para a mensagem atual. Se não conseguir identificar nenhuma das intenções específicas, use "unknown".

Atenção:
- A conversa pode ter múltiplas mensagens. Use o histórico para entender o contexto.
- Se a mensagem do usuário responde a uma pergunta anterior, atualize as entidades com essa resposta.
- Algumas solicitações não terão entidades e portanto também não terão entidades faltantes: consultar saldo por exemplo.
- Sua resposta deve ser APENAS um JSON válido, sem explicações ou comentários.
- Nunca pergunte pelo número da conta do usuário. Ele já é conhecido e fornecido como `account_number`.
- Responda sempre em português.

O número da conta do usuário (account_number) é {user_account_number}.

Formato esperado:
{{
  "intent": "transfer",
  "entities": {{
    "amount": 100,
    "recipient": "Maria"
  }},
  "missing_entities": [],
  "next_question": ""
}}

Histórico da conversa:
{history}

Mensagem atual do usuário:
{user_input}
"""

class IntentService:
    def __init__(self, user_account_number: int = 987654321):
        self.user_account_number = user_account_number

    def process_message(self, user_id: str, history: List[str], user_input: str) -> Dict[str, Any]:
        """Process a user message and return the intent and entities."""
        prompt = SYSTEM_PROMPT.format(
            history="\n".join(history),
            user_input=user_input,
            user_account_number=self.user_account_number
        )

        response = query_llm(prompt)

        logger.debug("Prompt:\n", prompt)
        logger.debug("RAW LLM RESPONSE:\n", response)

        # Tenta encontrar JSON dentro da resposta (mesmo que mal formatado)
        start = response.find("{")
        end = response.rfind("}") + 1

        if start == -1 or end == -1:
            return {"error": "No JSON block found in response."}

        json_like = response[start:end]

        # Correção tosca: adiciona aspas nas chaves
        json_fixed = re.sub(r'(\s*)(\w+):', r'\1"\2":', json_like)

        try:
            data = json.loads(json_fixed)
            # Ensure intent is always present and valid
            if "intent" not in data or data["intent"] not in ["transfer", "get_balance", "get_transactions", "get_help", "unknown"]:
                data["intent"] = "unknown"
            
            update_user_state(user_id, {
                "intent": data.get("intent"),
                "entities": data.get("entities", {}),
                "missing_entities": data.get("missing_entities", []),
                "next_question": data.get("next_question")
            })
            return data
        except json.JSONDecodeError as e:
            logger.debug("JSON error:", e)
            return {"error": "LLM returned an unexpected format."}
