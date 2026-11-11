# 130NET

Aplicativo de mensagens privadas em Streamlit com autenticação, contatos, solicitações de amizade, conversas privadas e perfil.

## Requisitos

- Python 3.10+
- MySQL 8+
- pip

## Instalação

1. Crie um ambiente virtual:
   python -m venv .venv
   .\.venv\Scripts\activate

2. Instale as dependências:
   pip install -r requirements.txt

3. Configure as credenciais do banco MySQL:
   - copie o arquivo `.env.example` para `.env`
   - ajuste os valores do banco conforme sua instalação
   - crie o banco configurado no MySQL antes de iniciar (por exemplo: `CREATE DATABASE 130net CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`)

4. As tabelas são criadas automaticamente na primeira execução. Também é possível criá-las manualmente:
   python database/init_db.py

5. Execute a aplicação:
   streamlit run app.py

## Estrutura resumida

- `app.py`: ponto de entrada
- `config.py`: carregamento e configuração da aplicação
- `database/__init__.py`: engine SQLAlchemy, sessão e inicialização de tabelas
- `models/`: modelos do sistema
- `services/`: regras de negócio
- `pages/`: telas do app
- `components/`: blocos reutilizáveis

## Observações

- As senhas são armazenadas com hash seguro via `werkzeug.security`.
- O sistema usa SQLAlchemy e MySQL como banco principal.
- O Streamlit não oferece WebSocket nativo, por isso a atualização em tempo real é simulada com polling leve do banco e rerun periódico.

## Publicação no Streamlit Community Cloud

- Defina as variáveis de ambiente no painel de segredos do Streamlit.
- Use `DATABASE_URL` ou `MYSQL_*` com os valores do seu banco.
- A aplicação espera um MySQL acessível a partir do ambiente em nuvem.
