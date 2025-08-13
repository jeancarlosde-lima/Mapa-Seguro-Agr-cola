# 🗺️ Mapa Interativo de Culturas Agrícolas no Brasil

![Licença](https://img.shields.io/badge/license-GPL--3.0-blue)
![Status](https://img.shields.io/badge/status-funcional-green)
![Python](https://img.shields.io/badge/python-3.9%2B-informational)

> **⚠️ Aviso de Privacidade e LGPD:** Este repositório utiliza um conjunto de **dados 100% fictícios** para fins de demonstração. Nenhuma informação real de clientes, apólices ou segurados está presente, em total conformidade com as melhores práticas de segurança e a Lei Geral de Proteção de Dados (LGPD).

---

### 🚀 O que é este projeto?

Este pipeline em Python transforma dados agrícolas de planilhas em um **mapa interativo e dinâmico**, mostrando a localização de apólices, culturas e áreas garantidas. O diferencial do projeto é sua capacidade de **validar e corrigir dados geograficamente**, utilizando os limites oficiais dos estados brasileiros (via GeoJSON) como fonte da verdade.

A ferramenta foi projetada para resolver o problema de dados de localização imprecisos, automatizando a limpeza e garantindo que as análises de risco sejam baseadas em informações confiáveis.

---

### 🖼️ Demonstração

![Demo do Mapa Interativo](https://drive.google.com/file/d/1VtOTlKN6HJd1cYS1t8CW-pGJgwWZoJKU/view?usp=sharing)

---

### ✨ Funcionalidades Principais

* **Validação Geográfica Precisa:** Utiliza um algoritmo "ponto-em-polígono" para verificar se cada coordenada está dentro da UF correta.
* **Correção Automática de Coordenadas:**
    * 📡 Geocodificação via **OpenStreetMap (Nominatim)** para endereços sem coordenadas.
    * 🎯 Atribuição do **centróide do estado** como fallback para garantir que nenhum dado seja perdido.
* **Engenharia de Dados:**
    * 📂 Leitura e manipulação de dados em lote com **Pandas**.
    * 📍 Parser de múltiplos formatos de coordenadas (DMS ↔ Decimal) com RegEx.
* **Visualização Rica:**
    * 🗺️ Geração de um arquivo `.html` interativo com **Folium**.
    * 🎨 Marcadores coloridos por tipo de cultura.
    * 📊 Cabeçalho customizado com logo e estatísticas dinâmicas.
    * 🔖 Legenda e pop-ups detalhados para cada ponto no mapa.

---

### 🛠️ Tecnologias Utilizadas

| Ferramenta | Propósito |
| :--- | :--- |
| **Python 3.x** | Linguagem principal |
| **Pandas** | Manipulação e estruturação dos dados |
| **Folium** | Geração dos mapas interativos |
| **Geopy** | Geocodificação (consultas a APIs de mapas) |
| **Openpyxl**| Leitura de arquivos Excel |

---

### 📦 Como Instalar e Rodar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jeancarlosde-lima/Mapa-Seguro-Agr-cola.git](https://github.com/jeancarlosde-lima/Mapa-Seguro-Agr-cola.git)
    cd Mapa-Seguro-Agr-cola
    ```
2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Nota: Se o arquivo `requirements.txt` não existir, crie-o com `pip freeze > requirements.txt`)*

3.  **Estrutura de Arquivos:** Garanta que seu diretório tenha a seguinte estrutura, com os nomes de arquivos correspondendo ao que está no script:
    ```
    /Mapa Seguradora_agro
    ├── script.py
    ├── dados_ficticios.xlsx
    ├── br.json
    └── logo_projeto.png
    ```

4.  **Execute o script:**
    ```bash
    python seu_script.py
    ```
    Um arquivo `mapa_final.html` (ou similar) será gerado. Abra-o em qualquer navegador.

---

### 💡 Criado por

**Jean Lima**
* [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jeancarlosodelima/)
* [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jeancarlosde-lima)



### ⚖️ Direitos Autorais e Uso

Copyright © 2025 Jean Lima. Todos os Direitos Reservados.

Este projeto é um trabalho proprietário e seu código-fonte é disponibilizado neste repositório do GitHub estritamente para fins de **demonstração e avaliação de portfólio**.

Nenhuma permissão é concedida para copiar, modificar, distribuir, usar em outros projetos (sejam eles pessoais, acadêmicos ou comerciais) ou criar trabalhos derivados a partir deste código sem o consentimento prévio e por escrito do autor.
