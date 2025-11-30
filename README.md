# Alpha-Telnet - Usenet Simulator

**Alpha-Telnet** é um simulador de Usenet em Python, com arquitetura cliente-servidor, 
que permite testar operações de leitura e postagem de artigos em grupos de notícias via terminal. 
É ideal para estudos de redes, protocolos de mensagens e aplicações assíncronas em Python.

---

## Funcionalidades

- Servidor Telnet simulando a Usenet
- Cliente interativo em terminal (asyncio)
- Comandos suportados:
  - `list` → Lista grupos de notícias
  - `group <nome>` → Seleciona um grupo
  - `article <id>` → Lê um artigo específico
  - `post` → Cria um novo artigo
  - `quit` → Encerra o cliente
- Persistência de dados (JSON)
- Suporte a múltiplos clientes simultâneos
- Interface limpa e mensagens de erro amigáveis

---

## Estrutura do Projeto
Alpha-Telnet/
├── client.py # Cliente Telnet assíncrono
├── server.py # Servidor Telnet Usenet
├── storage.py # Persistência de artigos
├── storage_backup.json # Backup de dados
└── pycache/ # Cache Python


---

## Requisitos

- Python 3.8+
- Bibliotecas padrão (`asyncio`, `argparse`)

---

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/tel36214287-star/Alpha-Telnet.git
cd Alpha-Telnet
python server.py
200 Usenet-simulator ready
Comandos: list, group <name>, article <id>, post, quit
>
> list
> group comp.example
> post
Newsgroups: comp.example
Subject: Meu Primeiro Artigo
From: usuario@teste.com
[Escreva o corpo e finalize com um ponto em linha separada]
.
> quit
Contribuições

Contribuições são bem-vindas! Algumas ideias:

Autenticação de usuários

Logs de artigos e histórico

Interface web ou gráfica

Melhor suporte a múltiplos clientes simultâneos

Licença

MIT License — você pode usar, modificar e redistribuir livremente.

Autor

tel36214287-star – Criador do Alpha-Telnet, simulador de Usenet em Python.
Renato, e... Nicole,se gato come peixe o G... come o D...? 

