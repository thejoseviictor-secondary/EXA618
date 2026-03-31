# Crawler para coletar dados dos conteúdos adicionais (conhecidos como expansões ou DLCs (Downloadable Content))
# dos jogos "American Truck Simulator" e "Euro Truck Simulator 2". Que são simuladores de caminhão.

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date
import urllib.request
import json
import csv

# Coletando a data atual (ISO 8601):
todays_date = date.today().isoformat()

# Modelo de tabela para arquivo ".csv":
output_data_template = [
    [
        "Nome do Jogo", "Nome da Expansão", "Tipo de Expansão", "Imagem de Capa",
        "Data de Lançamento", "Preço Atual", "Qtd. de Avaliações", "Qualidade de Avaliações",
        "Data de Coleta dos Dados"
    ]
]

# Modelo para arquivo ".html":
html_content_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparador de DLCs para ATS e ETS2</title>
    <style>
        body { font-family: Arial; }
        div { border: 1px solid #ccc; padding: 10px; margin: 10px; }
    </style>
</head>
<body>
"""

# Caminhos dos arquivos:
csv_file_path = "output.csv"
html_file_path = "index.html"

# Nomes dos jogos:
ats_name = "American Truck Simulator"
ets2_name = "Euro Truck Simulator 2"

# Sites onde os dados serão coletados:
# American Truck Simulator:
ats_map_expansions_seed = "https://store.steampowered.com/dlc/270880/American_Truck_Simulator/list/43348/"
ats_cargo_packs_seed = "https://store.steampowered.com/dlc/270880/American_Truck_Simulator/list/43349/"
ats_tuning_packs_seed = "https://store.steampowered.com/dlc/270880/American_Truck_Simulator/list/43350/"
ats_paint_themes_seed = "https://store.steampowered.com/dlc/270880/American_Truck_Simulator/list/43351/"
# Euro Truck Simulator 2:
ets2_map_expansions_seed = "https://store.steampowered.com/dlc/227300/Euro_Truck_Simulator_2/list/43330/"
ets2_cargo_packs_seed = "https://store.steampowered.com/dlc/227300/Euro_Truck_Simulator_2/list/43331/"
ets2_tuning_and_cabin_accesories_seed = "https://store.steampowered.com/dlc/227300/Euro_Truck_Simulator_2/list/43342/"
ets2_trailer_packs_seed = "https://store.steampowered.com/dlc/227300/Euro_Truck_Simulator_2/list/43341/"
ets2_paint_themes_seed = "https://store.steampowered.com/dlc/227300/Euro_Truck_Simulator_2/list/43333/"

# Site raiz da "Steam" para acessar mais detalhes do conteúdo:
steam_content_root_url = "https://store.steampowered.com/app/"

# Função de "parser" para coletar dados na "Steam":
def collectSteamData(seed):
    page = urllib.request.urlopen(seed)
    html = str(page.read().decode("utf-8"))

    soup = BeautifulSoup(html, "html.parser")
    
    div = soup.find("div", {"id": "application_config"})

    if div:
        data_applinkinfo = div.attrs.get("data-applinkinfo")
        if data_applinkinfo:
            return json.loads(data_applinkinfo)
    
    return None # Não encontrou dados.

# Função para formatar os dados para salvamento no ".csv" e ".html":
def setOutputData(map_expansions_steam_data, game_name, type):
    csv_output_data = []
    html_content = ""

    for steam_data in map_expansions_steam_data:
        release_date = steam_data["release"] # Data de lançamento.

        # Desconsiderando expansões que não foram lançadas ainda.
        if release_date != "To be announced":
            raw_title = steam_data["title"]
            title = raw_title.rsplit(" - ", 1)[-1].strip() # Título.

            steam_url = steam_content_root_url + str(steam_data["appid"]) # URL na "Steam".
            header = steam_data["capsule"] # Arte de capa.
            current_price = steam_data["price"] # Preço atual (na moeda local).
            num_reviews = steam_data["reviews_filtered"]["num_reviews"] # Quantidade de avaliações.
            label_reviews = steam_data["reviews_filtered"]["label"] # Qualidade das avaliações.

            html_content += f"""
    <div>
        <h1>Nome do jogo: {game_name}</h1>
        <h2>Nome do mapa: {title}</h2>
        <a href={steam_url} target="_blank">
            <img src={header} style="width: 30%; height: auto;" alt="Clique para acessar">
        </a>
        <p>Tipo de expansão: {type}</p>
        <p>Data de lançamento: {release_date}</p>
        <p>Preço atual: {current_price}</p>
        <p>Quantidade de avaliações: {num_reviews}</p>
        <p>Qualidade das avaliações: {label_reviews}</p>
        <p>Data da coleta dos dados: {todays_date}</p>
    </div>
    <br>
"""

            steam_data_output = [game_name, title, type, header, release_date, current_price, num_reviews, label_reviews, todays_date]
            csv_output_data.append(steam_data_output)
    
    return csv_output_data, html_content

# Função para salvar os dados no arquivo ".csv":
def writeDataToCSVFile(output_data):
    with open(csv_file_path, mode="w", newline="", encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(output_data)

# Função para salvar os dados no arquivo ".html":
def writeDataToHTMLFile(html_output):
    html_output += """
</body>
</html>
"""

    with open(html_file_path, mode="w", encoding="utf-8") as file:
        file.write(html_output)

if __name__ == "__main__":
    # Coletando os dados na "Steam":
    # American Truck Simulator:
    ats_map_expansions_steam_data = collectSteamData(ats_map_expansions_seed)
    ats_cargo_packs_steam_data = collectSteamData(ats_cargo_packs_seed)
    ats_tuning_packs_steam_data = collectSteamData(ats_tuning_packs_seed)
    ats_paint_themes_steam_data = collectSteamData(ats_paint_themes_seed)
    # Euro Truck Simulator 2:
    ets2_map_expansions_steam_data = collectSteamData(ets2_map_expansions_seed)
    ets2_cargo_packs_steam_data = collectSteamData(ets2_cargo_packs_seed)
    ets2_tuning_and_cabin_accesories_steam_data = collectSteamData(ets2_tuning_and_cabin_accesories_seed)
    ets2_trailer_packs_steam_data = collectSteamData(ets2_trailer_packs_seed)
    ets2_paint_themes_steam_data = collectSteamData(ets2_paint_themes_seed)
    
    # Inicializando o ".csv" e ".html" de saída:
    output_csv = output_data_template
    output_html = html_content_template

    # Organizando os dados de saída:
    # American Truck Simulator:
    ats_map_expansions_csv_output, ats_map_expansions_html_output = setOutputData(ats_map_expansions_steam_data, ats_name, "Expansão de Mapa")
    ats_cargo_packs_csv_output, ats_cargo_packs_html_output = setOutputData(ats_cargo_packs_steam_data, ats_name, "Pack de Cargas")
    ats_tuning_packs_csv_output, ats_tuning_packs_html_output = setOutputData(ats_tuning_packs_steam_data, ats_name, "Pack de Tunagem")
    ats_paint_themes_csv_output, ats_paint_themes_html_output = setOutputData(ats_paint_themes_steam_data, ats_name, "Temas de Pintura")
    # Euro Truck Simulator 2:
    ets2_map_expansions_csv_output, ets2_map_expansions_html_output = setOutputData(ets2_map_expansions_steam_data, ets2_name, "Expansão de Mapa")
    ets2_cargo_packs_csv_output, ets2_cargo_packs_html_output = setOutputData(ets2_cargo_packs_steam_data, ets2_name, "Pack de Cargas")
    ets2_tuning_and_cabin_accesories_csv_output, ets2_tuning_and_cabin_accesories_html_output = setOutputData(ets2_tuning_and_cabin_accesories_steam_data, ets2_name, "Tunagem e Acessórios de Cabine")
    ets2_trailer_packs_csv_output, ets2_trailer_packs_html_output = setOutputData(ets2_trailer_packs_steam_data, ets2_name, "Pack de Trailers")
    ets2_paint_themes_csv_output, ets2_paint_themes_html_output = setOutputData(ets2_paint_themes_steam_data, ets2_name, "Temas de Pintura")

    # Somando as saídas para o ".csv" e ".html":
    # CSV ------------------------------------------------------
    # American Truck Simulator:
    output_csv += ats_map_expansions_csv_output
    output_csv += ats_cargo_packs_csv_output
    output_csv += ats_tuning_packs_csv_output
    output_csv += ats_paint_themes_csv_output
    # Euro Truck Simulator 2:
    output_csv += ets2_map_expansions_csv_output
    output_csv += ets2_cargo_packs_csv_output
    output_csv += ets2_tuning_and_cabin_accesories_csv_output
    output_csv += ets2_trailer_packs_csv_output
    output_csv += ets2_paint_themes_csv_output
    # HTML -----------------------------------------------------
    # American Truck Simulator:
    output_html += ats_map_expansions_html_output
    output_html += ats_cargo_packs_html_output
    output_html += ats_tuning_packs_html_output
    output_html += ats_paint_themes_html_output
    # Euro Truck Simulator 2:
    output_html += ets2_map_expansions_html_output
    output_html += ets2_cargo_packs_html_output
    output_html += ets2_tuning_and_cabin_accesories_html_output
    output_html += ets2_trailer_packs_html_output
    output_html += ets2_paint_themes_html_output

    # Escrevendo os dados nos arquivos ".csv" e ".html":
    writeDataToCSVFile(output_csv)
    writeDataToHTMLFile(output_html)
