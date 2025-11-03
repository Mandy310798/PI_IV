# 🌐 PI_IV - Projeto Integrador IV

Aplicação web desenvolvida como parte do Projeto Integrador IV dos cursos do Eixo de Computação. O projeto é uma aplicação back-end, construída com **Python** e o *framework* **Flask**, utilizando **HTML** para a apresentação das páginas que tem o objetivo de mostrar gráficos de desempenho de vendas de uma pequena loja varejista.

## 🛠️ Ferramentas e Tecnologias Utilizadas

| Ferramenta / Linguagem | Tipo | Uso no Projeto |
| :--- | :--- | :--- |
| **Python** | Linguagem de Programação | Linguagem principal para toda a lógica de back-end. |
| **Flask** | Framework Web (Python) | Utilizado para criar o servidor web, definir rotas (URLs) e gerenciar as requisições HTTP (arquivos `app_flask.py`). |
| **HTML** | Linguagem de Marcação | Usado para estruturar o conteúdo das páginas web (*frontend*), localizadas na pasta `templates`. |
| **Jinja2** | Motor de Templates | Usado pelo Flask para renderizar dinamicamente o HTML, injetando dados do back-end nas páginas. |
| **Git** | Sistema de Controle de Versão | Utilizado para gerenciar e rastrear alterações no código-fonte. |

---

## 💻 Configuração e Instalação

Para que você possa clonar, configurar e rodar a aplicação em seu computador local, siga os passos abaixo.

### Pré-requisitos

Certifique-se de que os seguintes programas estão instalados em sua máquina:

1.  **Python** (Versão 3.x recomendada)
2.  **Git** (Para clonar o repositório)

### 1. Clonar o Repositório

Abra o seu terminal ou prompt de comando e execute o seguinte comando para baixar os arquivos do projeto:

```bash
git clone [https://github.com/Mandy310798/PI_IV.git](https://github.com/Mandy310798/PI_IV.git)
cd PI_IV ```

### 2. Configurar Ambiente Virtual (Recomendado)

É uma boa prática isolar as dependências do projeto em um ambiente virtual.

1.  **Crie o ambiente virtual:**
    ```bash
    python -m venv venv
    ```

2.  **Ative o ambiente virtual:**
    * **No Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **No macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

### 3. Instalar Dependências

Com o ambiente virtual ativo, instale todas as bibliotecas Python necessárias.

> **Nota:** Se você possui um arquivo `requirements.txt`, use `pip install -r requirements.txt`. Caso contrário, instale o Flask diretamente:

```bash
# Opção A: Se houver um arquivo requirements.txt
pip install -r requirements.txt

# Opção B: Se NÃO houver requirements.txt (instalação manual do Flask)
# pip install Flask

### 4. Executar a Aplicação

Inicie o servidor local do Flask.

1.  **Defina a variável de ambiente (obrigatório para o Flask):**
    ```bash
    # No Windows (CMD)
    set FLASK_APP=app_flask.py
    
    # No Windows (PowerShell) ou macOS/Linux
    export FLASK_APP=app_flask.py
    ```

2.  **Rode o servidor:**
    ```bash
    flask run
    ```

### 5. Acessar o Projeto

A aplicação estará rodando no seu navegador através do endereço:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

Para interromper o servidor, pressione `Ctrl + C` no terminal.
