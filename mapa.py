import os
import re
import json
import base64
import math
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Inicializa o geolocalizador e o rate limiter (para evitar exceder o limite de requisições)
geolocator = Nominatim(user_agent="agro_app")
geocode_rate_limited = RateLimiter(geolocator.geocode, min_delay_seconds=1)
geocode_cache = {}  # Cache para evitar consultas repetidas

def parse_coordinate(coord_str, is_latitude=True):
    """
    Converte uma string representando uma coordenada em DMS ou decimal para float.
    """
    if not isinstance(coord_str, str):
        try:
            return float(coord_str)
        except:
            return None

    c = coord_str.strip().replace(',', '.').upper()

    hemisphere = None
    if "NORTE" in c:
        hemisphere = "N"
        c = c.replace("NORTE", "")
    elif "SUL" in c:
        hemisphere = "S"
        c = c.replace("SUL", "")
    elif "LESTE" in c:
        hemisphere = "E"
        c = c.replace("LESTE", "")
    elif "OESTE" in c:
        hemisphere = "W"
        c = c.replace("OESTE", "")
    else:
        match = re.search(r'\b[NSWE]\b', c)
        if match:
            hemisphere = match.group(0)
            c = re.sub(r'\b[NSWE]\b', '', c)

    c = c.strip()

    dms_pattern = re.compile(r'^-?\d+(?:\.\d+)?[°:\s]+\d+(?:\.\d+)?[\'′\s]+\d+(?:\.\d+)?["″]?$')
    if dms_pattern.match(c):
        pattern = r'^(-?\d+(?:\.\d+)?)[°:\s]+(\d+(?:\.\d+)?)[\'′\s]+(\d+(?:\.\d+)?)(?:["″])?$'
        m = re.match(pattern, c)
        if not m:
            return None
        deg = float(m.group(1))
        mn = float(m.group(2))
        sc = float(m.group(3))
        dec = abs(deg) + mn / 60 + sc / 3600
        dec = dec if deg >= 0 else -dec
    else:
        try:
            dec = float(c)
        except ValueError:
            return None

    if hemisphere == 'S' or hemisphere == 'W':
        dec = -abs(dec)
    elif hemisphere == 'N' or hemisphere == 'E':
        dec = abs(dec)
    else:
        # se não houver indicação e for latitude positiva, assume sul (negativo)
        # **Este comportamento preserva o que já havia no seu script**
        if dec > 0:
            dec = -dec

    if is_latitude and not (-90 <= dec <= 90):
        return None
    if not is_latitude and not (-180 <= dec <= 180):
        return None

    return dec

def geocode_municipio(municipio, uf, extra_try=False):
    """
    Tenta obter as coordenadas (latitude, longitude) com base no nome do município e UF.
    Retorna uma tupla (lat, lon) ou (None, None) se não encontrar.
    Se extra_try=True faz uma query alternativa (string levemente diferente).
    """
    municipio = str(municipio).strip() if municipio is not None else ""
    uf = str(uf).strip() if uf is not None else ""

    if not municipio or not uf:
        return None, None

    key = f"{municipio.lower()}, {uf.upper()}"
    if key in geocode_cache:
        return geocode_cache[key]

    # principal query
    query = f"{municipio}, {uf}, Brasil" if not extra_try else f"{municipio} - {uf}, Brasil"
    try:
        location = geocode_rate_limited(query)
    except Exception:
        location = None

    if location:
        lat, lon = location.latitude, location.longitude
    else:
        lat, lon = None, None

    geocode_cache[key] = (lat, lon)
    return lat, lon

# --- funções geojson / ponto-em-polígono (sem dependências externas) ---

def is_point_in_ring(point_lon, point_lat, ring):
    """
    Ray casting algorithm para verificar se ponto está dentro de um anel linear (ring).
    ring: lista de [lon, lat]
    """
    inside = False
    n = len(ring)
    if n == 0:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        intersect = ((yi > point_lat) != (yj > point_lat)) and \
                    (point_lon < (xj - xi) * (point_lat - yi) / (yj - yi + 1e-16) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside

def point_in_polygon(point_lon, point_lat, polygon_coords):
    """
    polygon_coords: lista de linear rings: [ [ [lon,lat], ... ], [hole], ... ]
    Retorna True se ponto estiver dentro do anel externo e fora de todos os holes.
    """
    if not polygon_coords:
        return False
    outer = polygon_coords[0]
    if not is_point_in_ring(point_lon, point_lat, outer):
        return False
    # se estiver no anel externo, verificar holes
    for hole in polygon_coords[1:]:
        if is_point_in_ring(point_lon, point_lat, hole):
            return False
    return True

def point_in_feature(point_lon, point_lat, feature):
    """
    Verifica ponto para geometria do feature (Polygon / MultiPolygon).
    """
    geom = feature.get("geometry", {})
    gtype = geom.get("type")
    coords = geom.get("coordinates", [])
    if gtype == "Polygon":
        return point_in_polygon(point_lon, point_lat, coords)
    elif gtype == "MultiPolygon":
        # coords: [ [ polygon1_coords ], [ polygon2_coords ], ... ]
        for poly_coords in coords:
            if point_in_polygon(point_lon, point_lat, poly_coords):
                return True
        return False
    else:
        return False

def compute_feature_centroid(feature):
    """
    Centróide simples: média dos pontos do anel externo da primeira polygon disponível.
    (não é um centróide geodésico perfeito, mas serve como fallback).
    """
    geom = feature.get("geometry", {})
    gtype = geom.get("type")
    coords = geom.get("coordinates", [])
    if gtype == "Polygon" and coords:
        ring = coords[0]
    elif gtype == "MultiPolygon" and coords and len(coords) > 0:
        ring = coords[0][0]
    else:
        return None, None
    lons = [pt[0] for pt in ring if len(pt) >= 2]
    lats = [pt[1] for pt in ring if len(pt) >= 2]
    if not lons or not lats:
        return None, None
    return (sum(lats) / len(lats), sum(lons) / len(lons))  # retorna (lat, lon)

# --- carregar dados (agora recebe geojson para validação por UF) ---

def carregar_dados(file_path, sheet_name, geojson_data):
    """
    Lê as colunas do Excel e converte as coordenadas.
    Força que as coordenadas fiquem dentro da UF informada (corrige com geocoding e depois com centróide da UF).
    """
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=0,
        usecols=[
            "APÓLICE", "NUMERO_PI", "Municipio",
            "UF","LATITUDE", "LONGITUDE", "CULTURA", "STATUS", "CULTURA","STATUS", "NOME","ÁREA GARANTIDA (ha)"
        ]
    )

    original_count = len(df)

    df["CULTURA"] = df["CULTURA"].astype(str).str.strip().str.capitalize()
    df["UF"] = df["UF"].astype(str).str.strip().str.upper()

    df["LATITUDE"] = df["LATITUDE"].apply(lambda x: parse_coordinate(str(x), True))
    df["LONGITUDE"] = df["LONGITUDE"].apply(lambda x: parse_coordinate(str(x), False))

    # criar um mapeamento de id_estado -> feature para busca rápida
    features_map = {}
    for feature in geojson_data.get("features", []):
        props = feature.get("properties", {})
        estado_id = props.get("id") or props.get("ID") or props.get("code") or props.get("uf") or None
        # alguns geojson usam 'id' tipo 'BRRS' - assumimos formato BR + UF
        if estado_id:
            features_map[str(estado_id).upper()] = feature

    # criar centróides para fallback
    centroids = {}
    for key, feature in features_map.items():
        latc, lonc = compute_feature_centroid(feature)
        if latc is not None:
            centroids[key] = (latc, lonc)

    # colunas de auditoria
    df["INSIDE_UF"] = False
    df["COORD_CORRECTION"] = ""  # original | geocoded | centroid | none

    for idx, row in df.iterrows():
        lat = row["LATITUDE"]
        lon = row["LONGITUDE"]
        uf = str(row["UF"]).strip().upper()
        estado_key = "BR" + uf  # formato usado em features_map no seu script
        feature = features_map.get(estado_key)

        # se sem coords válidas, tenta geocoding simples
        if pd.isna(lat) or pd.isna(lon):
            novo_lat, novo_lon = geocode_municipio(row["Municipio"], uf)
            if novo_lat is not None and novo_lon is not None:
                df.at[idx, "LATITUDE"] = novo_lat
                df.at[idx, "LONGITUDE"] = novo_lon
                df.at[idx, "COORD_CORRECTION"] = "geocoded"
                lat, lon = novo_lat, novo_lon

        # se ainda sem coords, já foi geocoded/mas None -> deixará para filtro posterior
        if pd.isna(lat) or pd.isna(lon):
            continue

        # verificar se ponto está dentro da UF declarada
        inside = False
        if feature is not None:
            try:
                inside = point_in_feature(lon, lat, feature)
            except Exception:
                inside = False

        if inside:
            df.at[idx, "INSIDE_UF"] = True
            if df.at[idx, "COORD_CORRECTION"] == "":
                df.at[idx, "COORD_CORRECTION"] = "original"
        else:
            # se não estiver dentro da UF, tenta uma segunda geocoding mais explícita
            novo_lat2, novo_lon2 = geocode_municipio(row["Municipio"], uf, extra_try=True)
            if novo_lat2 is not None and novo_lon2 is not None:
                # checar se essa nova está dentro
                if feature is not None and point_in_feature(novo_lon2, novo_lat2, feature):
                    df.at[idx, "LATITUDE"] = novo_lat2
                    df.at[idx, "LONGITUDE"] = novo_lon2
                    df.at[idx, "INSIDE_UF"] = True
                    df.at[idx, "COORD_CORRECTION"] = "geocoded_second_try"
                    continue
            # se ainda não está dentro, usar centróide da UF (se existir)
            if feature is not None and estado_key in centroids:
                latc, lonc = centroids[estado_key]
                df.at[idx, "LATITUDE"] = latc
                df.at[idx, "LONGITUDE"] = lonc
                df.at[idx, "INSIDE_UF"] = True
                df.at[idx, "COORD_CORRECTION"] = "centroid_assigned"
            else:
                # não conseguimos localizar feature/centróide -> marcar como inválido (será removido pelo filtro abaixo)
                df.at[idx, "INSIDE_UF"] = False
                if df.at[idx, "COORD_CORRECTION"] == "":
                    df.at[idx, "COORD_CORRECTION"] = "none"

    df_before_filter = df.copy()

    # aplicar filtros de faixa Brasil (mantive os limites que você tinha)
    df = df[df["LATITUDE"].notna() & df["LONGITUDE"].notna()]
    df = df[
        (df["LATITUDE"] >= -34) & (df["LATITUDE"] <= 5) &
        (df["LONGITUDE"] >= -74) & (df["LONGITUDE"] <= -34)
    ]

    # além do filtro de faixa, remover quaisquer pontos que ainda não estejam INSIDE_UF = True
    invalid_by_uf = df[~df["INSIDE_UF"]]
    if len(invalid_by_uf) > 0:
        print("Atenção: os seguintes pontos foram removidos por estarem fora da UF declarada ou inválidos:")
        print(invalid_by_uf[["APÓLICE", "NUMERO_PI", "Municipio", "UF", "LATITUDE", "LONGITUDE", "COORD_CORRECTION"]].to_string(index=False))

    df = df[df["INSIDE_UF"] == True]

    final_count = len(df)
    if final_count < original_count:
        print(f"Linhas iniciais: {original_count}")
        print(f"Linhas finais:  {final_count}")
        print("Foram aplicadas correções para garantir que pontos fiquem dentro da UF (ver COORD_CORRECTION).")

    # correções manuais caso precise
    correcoes = {
    }
    for pi, (lat, lon) in correcoes.items():
        df.loc[df["NUMERO_PI"] == pi, ["LATITUDE", "LONGITUDE"]] = (lat, lon)
        df.loc[df["NUMERO_PI"] == pi, "COORD_CORRECTION"] = "manual_override"

    df["Estado"] = "BR" + df["UF"]

    return df

# --- funções auxiliares de mapa (mantive as suas) ---

def get_logo_base64(path_logo):
    with open(path_logo, 'rb') as image_file:
        logo_data = image_file.read()
    return base64.b64encode(logo_data).decode('utf-8')

def get_marker_color(row_or_str):
    if isinstance(row_or_str, dict):
        cultura = str(row_or_str["CULTURA"]).strip().lower()
    else:
        cultura = str(row_or_str).strip().lower()

    if "soja" in cultura:
        return "#FF8247"
    elif "milho" in cultura:
        return "#C0FF3E"
    elif "milho safrinha" in cultura:
        return "#228B22"
    elif "trigo" in cultura:
        return "#9F79EE"
    elif "arroz" in cultura:
        return "#F5F5DC"
    elif "batata" in cultura:
        return "#FFFF00"
    elif "sorgo" in cultura:
        return "#8B7B8B"
    elif "maçã" in cultura:
        return "#8B2500"
    elif "cebola" in cultura:
        return "#8B7765"
    elif "tomate de mesa" in cultura:
        return "#FA8072"
    else:
        return "magenta"

def adicionar_legenda(mapa, df):
    culturas = sorted(df["CULTURA"].unique())
    legend_lines = ""
    for cultura in culturas:
        cor = get_marker_color(cultura)
        legend_lines += (
            f'<p><span style="background-color: {cor}; display: inline-block; '
            f'width: 15px; height: 15px; margin-right: 5px; border-radius: 50%;"></span> {cultura}</p>'
        )
    legenda_html = f'''
    <div style="
        position: fixed;
        bottom: 20px;
        left: 10px;
        z-index: 9999;
        font-size: 12px;
        background-color: white;
        padding: 10px;
        border: 2px solid black;
        border-radius: 5px;
    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Legenda</h4>
        {legend_lines}
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(legenda_html))

def adicionar_cabecalho(mapa, df, logo_path="#logo da empresa"):  #LOGO
    total_points = len(df)
    logo_base64 = get_logo_base64(logo_path)
    logo_img = f'<img src="data:image/png;base64,{logo_base64}" alt="#logo da empresa" style="width:120px; height:auto; margin-bottom:10px;" />'

    culture_counts = df["CULTURA"].value_counts()
    culture_lines = ""
    for cultura, count in culture_counts.items():
        culture_lines += f"<p style='margin: 2px 0;'>{cultura}: {count}</p>"

    cabecalho_html = f'''
    <div style="
        position: fixed;
        top: 20px;
        right: 10px;
        z-index: 9999;
        font-size: 14px;
        background-color: white;
        padding: 10px;
        border: 2px solid black;
        border-radius: 5px;
        font-family: 'Poppins', sans-serif;
        min-width: 220px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        text-align: center;
    ">
        {logo_img}
        <h4 style="margin: 0 0 5px 0; font-weight: 600;"> Agro - MAPA </h4>
        <p style="margin: 2px 0;">DADOS FICTÍCIOS - MERAMENTE ILUSTRATITO</p>
        <p style="margin: 2px 0;"><b>Total: {total_points}</b></p>
        {culture_lines}
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(cabecalho_html))

def criar_mapa_com_camadas(df, geojson_data, output_file, logo_path="layout_set_logo (1).png"):
    total_points = len(df)
    if total_points == 0:
        print("Nenhum dado de pontos encontrado. Gerando mapa base sem marcadores.")

    breakdown_group = df.groupby(['Estado', 'CULTURA']).size().reset_index(name='Count')
    breakdown_dict = {}
    for state in breakdown_group['Estado'].unique():
        lines = []
        state_data = breakdown_group[breakdown_group['Estado'] == state]
        for _, r in state_data.iterrows():
            lines.append(f"{r['CULTURA']}: {r['Count']}")
        breakdown_dict[state] = lines

    state_names = {
        'BRAC': 'Acre', 'BRAL': 'Alagoas', 'BRAP': 'Amapá', 'BRAM': 'Amazonas',
        'BRBA': 'Bahia', 'BRCE': 'Ceará', 'BRDF': 'Distrito Federal', 'BRES': 'Espírito Santo',
        'BRGO': 'Goiás', 'BRMA': 'Maranhão', 'BRMT': 'Mato Grosso', 'BRMS': 'Mato Grosso do Sul',
        'BRMG': 'Minas Gerais', 'BRPA': 'Pará', 'BRPB': 'Paraíba', 'BRPR': 'Paraná',
        'BRPE': 'Pernambuco', 'BRPI': 'Piauí', 'BRRJ': 'Rio de Janeiro', 'BRRN': 'Rio Grande do Norte',
        'BRRS': 'Rio Grande do Sul', 'BRRO': 'Rondônia', 'BRRR': 'Roraima', 'BRSC': 'Santa Catarina',
        'BRSP': 'São Paulo', 'BRSE': 'Sergipe', 'BRTO': 'Tocantins'
    }
    for feature in geojson_data["features"]:
        estado_id = feature["properties"].get("id") or feature["properties"].get("ID") or ""
        nome_estado = state_names.get(estado_id, estado_id)
        if estado_id in breakdown_dict:
            total = sum(int(line.split(": ")[1]) for line in breakdown_dict[estado_id])
            lines = breakdown_dict[estado_id]
            table_html = (
                f"<table border='1' style='border-collapse: collapse; font-size:12px;'>"
                f"<tr><th>{nome_estado} - TOTAL: {total}</th></tr>"
            )
            for line in lines:
                table_html += f"<tr><td style='padding:2px 5px;'>{line}</td></tr>"
            table_html += "</table>"
            feature["properties"]["observacoes"] = table_html
        else:
            feature["properties"]["observacoes"] = (
                f"<table border='1' style='border-collapse: collapse; font-size:12px;'>"
                f"<tr><td>{nome_estado} - Sem dados</td></tr></table>"
            )

    mapa = folium.Map(location=[-15.8267, -47.9218], zoom_start=4.0, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='<a href="https://sompoagricola.com.br"> "Empresa" Agro</a> | Criado por Jean Lima', 
        name='Relatório - Agro '
    ).add_to(mapa)

    css = """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
    .leaflet-tooltip {
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
    }
    </style>
    """
    mapa.get_root().html.add_child(folium.Element(css))

    folium.GeoJson(
        geojson_data,
        name="Estados",
        style_function=lambda feature: {
            "fillColor": "lightblue",
            "color": "green",
            "weight": 2,
            "dashArray": "5, 5",
        },
        highlight_function=lambda feature: {
            "fillColor": "yellow",
            "color": "white",
            "weight": 3,
            "dashArray": "",
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["observacoes"],
            aliases=["Culturas"],
            labels=True,
            localize=True,
            sticky=False,
            parse_html=True
        )
    ).add_to(mapa)

    for _, row in df.iterrows():
        cor = get_marker_color(row)
        popup_content = (
            f"<b>APÓLICE:</b> {row['APÓLICE']}<br>"
            f"<b>NUMERO_PI:</b> {row['NUMERO_PI']}<br>"
            f"<b>Cultura:</b> {row['CULTURA']}<br>"
            f"<b>Município:</b> {row['Municipio']}<br>"
            f"<b>NOME:</b> {row['NOME']}<br>"
            f"<b>ÁREA GARANTIDA (ha):</b> {row['ÁREA GARANTIDA (ha)']}<br>"
            f"<b>UF:</b> {row['UF']}<br>"
            f"<b>COORD_CORRECTION:</b> {row.get('COORD_CORRECTION', '')}"
        )
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=3.5,
            color="black",
            weight=1,
            fill=True,
            fill_color=cor,
            fill_opacity=0.85,
            opacity=0.6,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(mapa)

    adicionar_cabecalho(mapa, df, logo_path)
    adicionar_legenda(mapa, df)
    mapa.save(output_file)
    print(f"Mapa salvo em: {output_file}")

if __name__ == "__main__":
    file_path = r"C:\Users" - #Seu caminho da planilha
    sheet_name = 'RANDOM' - #Nome da Aba da planilha

    if not os.path.exists(file_path):
        print("O arquivo não foi encontrado no caminho especificado.")
    else:
        diretorio = r"" #Seu caminho para salvar
        
        output_file = os.path.join(diretorio, "mapa_exemplo.html")
        geojson_path = os.path.join(diretorio, "br.json")
        logo_path = os.path.join(diretorio, "" #imagem da empresa)

        # CARREGA GEOJSON ANTES para que carregar_dados possa validar por UF
        with open(geojson_path, encoding="utf-8") as f:
            geojson_data = json.load(f)

        df = carregar_dados(file_path, sheet_name, geojson_data)

        criar_mapa_com_camadas(df, geojson_data, output_file, logo_path)
