"""
update_reviews.py — Equipa Diogo Dias
Vai buscar as reviews do Google Places API e actualiza a secção de
testemunhos no index.html. Corre manualmente sempre que quiseres actualizar.

Uso:
    python update_reviews.py

Requisitos:
    pip install requests python-dotenv
"""

import re
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACE_ID = os.getenv("GOOGLE_PLACE_ID")
INDEX_HTML = Path(__file__).parent / "index.html"

PLACES_URL = f"https://places.googleapis.com/v1/places/{PLACE_ID}"
PLACES_HEADERS = {
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "reviews",
}

# Só mostra reviews com 5 estrelas e texto com pelo menos 40 caracteres
MIN_RATING = 5
MIN_TEXT_LEN = 40
MAX_REVIEWS = 6


def estrelas(n):
    return "★" * n


def escapar_html(texto):
    return (
        texto.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
    )


def gerar_html_reviews(reviews):
    cards = []
    for r in reviews:
        rating = r.get("rating", 0)
        # nova Places API: text é um objecto {"text": "...", "languageCode": "..."}
        texto_obj = r.get("text", {})
        texto = (texto_obj.get("text", "") if isinstance(texto_obj, dict) else texto_obj).strip()
        autor = r.get("authorAttribution", {}).get("displayName", "Cliente EDD")

        if rating < MIN_RATING or len(texto) < MIN_TEXT_LEN:
            continue

        card = f"""        <div class="testimonial">
          <div class="testimonial-stars">{estrelas(rating)}</div>
          <p class="testimonial-text">"{escapar_html(texto)}"</p>
          <p class="testimonial-author">{escapar_html(autor)} · Google</p>
        </div>"""
        cards.append(card)

        if len(cards) >= MAX_REVIEWS:
            break

    return "\n".join(cards)


def actualizar_html(novo_html_cards):
    conteudo = INDEX_HTML.read_text(encoding="utf-8")

    # Substitui o conteúdo entre as tags da grelha de testemunhos
    padrao = r'(<div class="testimonials-grid">)(.*?)(</div>\s*</div>\s*</section>)'
    substituicao = (
        r'\1\n'
        + novo_html_cards
        + r'\n      \3'
    )

    novo_conteudo, n = re.subn(padrao, substituicao, conteudo, flags=re.DOTALL)

    if n == 0:
        print("ERRO: Não foi possível encontrar a secção 'testimonials-grid' no index.html.")
        sys.exit(1)

    INDEX_HTML.write_text(novo_conteudo, encoding="utf-8")
    print(f"index.html actualizado com {novo_html_cards.count('testimonial-stars')} reviews.")


def main():
    if not API_KEY or not PLACE_ID:
        print("ERRO: Variáveis GOOGLE_PLACES_API_KEY ou GOOGLE_PLACE_ID em falta no .env")
        sys.exit(1)

    print("A ir buscar reviews ao Google Places API...")
    resposta = requests.get(PLACES_URL, headers=PLACES_HEADERS, timeout=10)
    dados = resposta.json()

    if "error" in dados:
        erro = dados["error"]
        print(f"ERRO da API: {erro.get('status')} — {erro.get('message', '')}")
        sys.exit(1)

    reviews = dados.get("reviews", [])
    if not reviews:
        print("Nenhuma review encontrada.")
        sys.exit(0)

    print(f"{len(reviews)} reviews recebidas. A filtrar e gerar HTML...")
    html_cards = gerar_html_reviews(reviews)

    if not html_cards:
        print("Nenhuma review passou os filtros (mínimo 5 estrelas, 40 caracteres).")
        sys.exit(0)

    actualizar_html(html_cards)
    print("Concluído. Abre o index.html no browser para confirmar.")


if __name__ == "__main__":
    main()
