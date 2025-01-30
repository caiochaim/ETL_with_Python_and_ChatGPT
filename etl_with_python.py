!pip install chardet
!pip install openai

import chardet as cd
import pandas as pd
from openai import OpenAI

client = OpenAI(
  api_key="YOUR_OpenAI_API_KEY"
)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

with open("base_dados_msg_promocional_copy.csv", "rb") as f:
    result = cd.detect(f.read())

data_frame = pd.read_csv("base_dados_msg_promocional.csv", encoding=result['encoding'], sep=';')

data_frame.columns = data_frame.columns.str.strip()

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

dados = data_frame[data_frame.columns.values.tolist()]
aprovados = []

for d in list(dados.index):
  nota_final = dados.loc[d]['TOTAL_NOTA'] / dados.loc[d]['QTDE_DISCIPLINA']
  dados.loc[d, 'NOTA_FINAL'] = round(nota_final, 1)

aprovados = dados[dados['NOTA_FINAL'] >= 7.0]
aprovados['SITUACAO'] = 'APROVADO'

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

def generate_msg (nome_usuario, endereco, curso, nota_final, situacao, e_mail):
  msg_chat = f"crie uma msg de até 100 caracteres, para uma pessoa chamada {nome_usuario}, informando que ele obteve uma das melhores notas do curso de {curso}, e obtendo uma boa classificação na faculdade com a nota {nota_final}. Sendo assim, caso a nota dele for maior que 8.5, ganhará uma viagem para a Escócia de 5 dias com tudo pago, e as passagens serão enviadas no e-mail {e_mail} e também para o endereço dele, que é na {endereco}, caso não for maior que 8.5, somente parabenizará o aluno."
  
  try:
    response = gpt.chat.completions.create(
      model="gpt-4o-mini",
      store=True,
      messages=[
        {
            "role": "user",
            "content": msg_chat
        }
      ]
    )

    return response.choices[0].message.content.strip()
  except Exception as e:
    return "Ops, não conseguimos gerar a mensagem!"

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

for a in list(aprovados.index):
  endereco_completo = f"{aprovados.loc[a, 'ENDERECO']}, número {aprovados.loc[a, 'NUMERO']} ({aprovados.loc[a, 'COMPLEMENTO']}) - {aprovados.loc[a, 'CIDADE']} - {aprovados.loc[a, 'ESTADO']}"
  msg = generate_msg(aprovados.loc[a, 'NOME'], endereco_completo, aprovados.loc[a, 'CURSO'], aprovados.loc[a, 'NOTA_FINAL'], aprovados.loc[a, 'SITUACAO'], aprovados.loc[a, 'E_MAIL'])
  
  aprovados.loc[a, 'MENSAGEM'] = msg

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

pd.DataFrame(aprovados).to_excel('aprovados.xlsx', index = False)