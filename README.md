Pipeline de Validação Geográfica e Visualização para Seguro Agrícola
Status: Concluído ✔️

📄 Sobre o Projeto
Este projeto consiste em um pipeline de dados desenvolvido em Python para automatizar o processo de limpeza, validação, enriquecimento e visualização de dados geoespaciais de apólices de seguro agrícola.

O principal desafio abordado é a inconsistência e a falta de precisão nos dados de localização provenientes de planilhas, que representam um risco para a análise e subscrição. A solução garante a integridade e a conformidade territorial de cada apólice, transformando dados brutos em um mapa interativo e acionável.

✨ Funcionalidades Principais
Ingestão de Dados: Leitura e processamento de dados de apólices a partir de arquivos Excel.

Tratamento de Coordenadas: Análise e padronização de múltiplos formatos de coordenadas (DMS, Decimal).

Validação Geoespacial: Implementação de um algoritmo "ponto-em-polígono" que utiliza um arquivo GeoJSON para verificar se a coordenada de uma apólice está, de fato, dentro dos limites geográficos do estado (UF) declarado.

Correção e Enriquecimento Automático: Em caso de dados inválidos ou ausentes, o pipeline utiliza a biblioteca Geopy para fazer a geocodificação do município ou, como último recurso, atribui o centróide da UF, garantindo que nenhum dado válido seja perdido.

Visualização Interativa: Geração de um mapa HTML interativo com Folium, onde cada apólice é um ponto clicável, com cores customizadas por tipo de cultura, legendas e um dashboard com estatísticas gerais.

演示 Demonstração
(Dica: Tire um print screen do seu mapa gerado e adicione a imagem na pasta do seu projeto. Depois, substitua o link abaixo para que a imagem apareça aqui.)

🛠️ Tecnologias Utilizadas
Linguagem: Python

Bibliotecas Principais:

Pandas: Manipulação e estruturação de dados.

Folium: Criação de mapas interativos.

Geopy: Geocodificação de endereços (consultas via API ao Nominatim).

RE (Expressões Regulares): Para o parsing de formatos complexos de coordenadas.

🚀 Como Executar
Clone o repositório:

Bash

git clone https://github.com/seu-usuario/nome-do-repositorio.git
Crie e ative um ambiente virtual:

Bash

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
Instale as dependências:

Bash

pip install -r requirements.txt
Certifique-se de que os seguintes arquivos estão na pasta raiz do projeto:

dados_ficticios.xlsx (com os dados de exemplo)

br.json (o arquivo GeoJSON com os limites dos estados)

layout_set_logo (1).png (ou o logo que você utiliza)

Execute o script principal:

Bash

python nome_do_seu_script.py
Abra o arquivo mapa_proposta_julho.html gerado no seu navegador.

👤 Autor
Jean Lima

LinkedIn: https://www.linkedin.com/in/seu-perfil

GitHub: https://github.com/seu-usuario

