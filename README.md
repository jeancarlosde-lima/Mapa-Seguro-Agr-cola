# 🗺️ Pipeline de Validação Geográfica para Seguro Agrícola

![Status](https://img.shields.io/badge/status-concluído-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> Um pipeline de engenharia de dados ponta-a-ponta para garantir a máxima qualidade e precisão em dados geoespaciais de risco agrícola.

---

### 🎯 O Desafio

No setor de seguros agrícolas, a precisão dos dados de localização é fundamental para uma subscrição de risco correta. Dados inconsistentes, com formatos variados ou erros de digitação, podem levar a análises falhas e decisões de negócio equivocadas. Este projeto foi criado para resolver esse problema de forma automatizada e escalável.

---

### ✨ Funcionalidades Principais

* **⚙️ Automação de Processos:** Ingestão de dados diretamente de planilhas (`.xlsx`) e processamento em lote.
* **🧹 Limpeza e Padronização:** Implementação de um parser robusto com Expressões Regulares (RegEx) para interpretar e converter múltiplos formatos de coordenadas (DMS, Decimal).
* **🌍 Validação Geoespacial:** Utilização de um algoritmo **"ponto-em-polígono"** com um shapefile GeoJSON para validar programaticamente se cada apólice pertence ao estado (UF) declarado, garantindo conformidade territorial.
* **🧠 Correção Inteligente:** Em caso de divergências, o pipeline enriquece os dados utilizando a API do Nominatim (via **Geopy**) para encontrar a localização correta. Como fallback, o centróide da UF é utilizado para evitar a perda de dados.
* **📊 Visualização Interativa:** Geração de um mapa `.html` dinâmico com **Folium**, apresentando cada apólice como um ponto de dados interativo, com dashboards, legendas e pop-ups detalhados para uma análise visual e intuitiva.

---

### 🚀 Demonstração em Vídeo (GIF)

*(Dica: Grave um GIF curto mostrando a interação com o mapa final. É muito mais impactante que uma imagem estática. Use ferramentas como LICEcap ou Giphy Capture para gravar sua tela. Depois, adicione o GIF na pasta do projeto e atualize o link abaixo.)*

![Demo do Mapa Interativo](caminho/para/seu/mapa-demo.gif)

---

### 🛠️ Tecnologias Utilizadas

| Ferramenta | Propósito |
| :--- | :--- |
| **Python** | Linguagem principal do projeto |
| **Pandas** | Manipulação, limpeza e estruturação dos dados |
| **Folium** | Geração dos mapas interativos em HTML/JS |
| **Geopy** | Geocodificação (consultas a APIs de mapas) |
| **JSON & RegEx** | Leitura de shapefiles e parsing de texto |

---

### ⚡ Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jeancarlosde-lima/Mapa-Seguro-Agr-cola.git](https://github.com/jeancarlosde-lima/Mapa-Seguro-Agr-cola.git)
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv && source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute o script:**
    ```bash
    python nome_do_seu_script.py
    ```
5.  Abra o arquivo `.html` gerado no seu navegador para ver o mapa.

---

### 👤 Autor

**Jean Lima**

* [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jeancarlosodelima/)
* [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jeancarlosde-lima)
