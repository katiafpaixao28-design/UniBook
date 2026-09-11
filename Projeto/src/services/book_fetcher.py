import urllib.request
import urllib.parse
import json

# Sugestões de obras pré-configuradas com capas para cadastro rápido em 1 clique
SUGESTOES_RAPIDAS = [
    {
        "titulo": "Memórias Póstumas de Brás Cubas",
        "autor": "Machado de Assis",
        "tema": "Comédia",
        "ano": 1881,
        "quantidade": 4,
        "capa_url": "https://covers.openlibrary.org/b/id/10515152-M.jpg",
        "sinopse": "Narrativa irreverente e irônica contada por um 'defunto autor' sobre a sociedade brasileira."
    },
    {
        "titulo": "O Cortiço",
        "autor": "Aluísio Azevedo",
        "tema": "Drama",
        "ano": 1890,
        "quantidade": 3,
        "capa_url": "https://covers.openlibrary.org/b/id/8315183-M.jpg",
        "sinopse": "Retrato naturalista marcante da vida e dos conflitos em uma habitação coletiva no Rio de Janeiro."
    },
    {
        "titulo": "O Morro dos Ventos Uivantes",
        "autor": "Emily Brontë",
        "tema": "Romance",
        "ano": 1847,
        "quantidade": 5,
        "capa_url": "https://covers.openlibrary.org/b/id/12644265-M.jpg",
        "sinopse": "A intensa e tempestuosa história de amor e vingança entre Catherine Earnshaw e Heathcliff."
    },
    {
        "titulo": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "tema": "Ficção Científica",
        "ano": 1953,
        "quantidade": 4,
        "capa_url": "https://covers.openlibrary.org/b/id/12711674-M.jpg",
        "sinopse": "Num futuro distópico, os bombeiros têm a missão de queimar livros para censurar o pensamento livre."
    },
    {
        "titulo": "Drácula",
        "autor": "Bram Stoker",
        "tema": "Suspense/Terror",
        "ano": 1897,
        "quantidade": 3,
        "capa_url": "https://covers.openlibrary.org/b/id/10524458-M.jpg",
        "sinopse": "O clássico do horror gótico narrando a jornada sombria do Conde Drácula da Transilvânia à Inglaterra."
    },
    {
        "titulo": "O Programador Pragmático",
        "autor": "Andrew Hunt e David Thomas",
        "tema": "Acadêmico/Técnico",
        "ano": 1999,
        "quantidade": 5,
        "capa_url": "https://covers.openlibrary.org/b/id/8575024-M.jpg",
        "sinopse": "Dicas essenciais e sabedoria prática para a carreira e evolução de engenheiros de software."
    },
    {
        "titulo": "O Hobbit",
        "autor": "J.R.R. Tolkien",
        "tema": "Fantasia",
        "ano": 1937,
        "quantidade": 4,
        "capa_url": "https://covers.openlibrary.org/b/id/12845686-M.jpg",
        "sinopse": "A inesquecível aventura de Bilbo Bolseiro junto aos anões para recuperar o tesouro de Erebor."
    }
]

def buscar_metadados_online(termo_busca):
    """
    Consulta metadados e imagem de capa na base pública da Open Library.
    Permite cadastro rápido por título ou ISBN sem digitação manual.
    """
    termo = termo_busca.strip()
    if not termo:
        return []

    url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(termo)}&limit=5"
    req = urllib.request.Request(url, headers={"User-Agent": "UniBook-UniEnsino/2.0"})

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            docs = data.get("docs", [])
            resultados = []

            for item in docs:
                title = item.get("title", "")
                authors = item.get("author_name", ["Autor Desconhecido"])
                first_author = authors[0] if authors else "Autor Desconhecido"
                year = item.get("first_publish_year")
                cover_i = item.get("cover_i")

                # URL da imagem oficial da capa
                capa_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else None

                # Tentar deduzir tema a partir dos assuntos (subjects) ou título
                subjects = [s.lower() for s in item.get("subject", [])[:10]]
                tema_sugerido = "Acadêmico/Técnico"

                subjects_str = " ".join(subjects) + " " + title.lower()
                if any(k in subjects_str for k in ["humor", "comedy", "comedia", "comédia", "satire"]):
                    tema_sugerido = "Comédia"
                elif any(k in subjects_str for k in ["romance", "love", "amor"]):
                    tema_sugerido = "Romance"
                elif any(k in subjects_str for k in ["science fiction", "ficcao", "ficção", "space", "alien", "dune"]):
                    tema_sugerido = "Ficção Científica"
                elif any(k in subjects_str for k in ["horror", "terror", "thriller", "suspense", "mystery"]):
                    tema_sugerido = "Suspense/Terror"
                elif any(k in subjects_str for k in ["fantasy", "fantasia", "magic", "dragon"]):
                    tema_sugerido = "Fantasia"
                elif any(k in subjects_str for k in ["adventure", "aventura"]):
                    tema_sugerido = "Aventura"

                resultados.append({
                    "titulo": title,
                    "autor": first_author,
                    "ano": year,
                    "tema": tema_sugerido,
                    "capa_url": capa_url,
                    "sinopse": f"Obra localizada na biblioteca aberta internacional. Edição de {year or 'ano não catalogado'}."
                })

            return resultados
    except Exception as e:
        print(f"Erro na busca online: {e}")
        return []
