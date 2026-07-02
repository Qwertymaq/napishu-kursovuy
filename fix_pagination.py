#!/usr/bin/env python3
import re

articles_file = "/tmp/opencode/articles/index.html"
articles_html = open(articles_file, "r", encoding="utf-8").read()

cards = re.findall(
    r'<article class="article-card"><h2><a href="([^"]+)">([^<]+)</a></h2><p>([^<]+)</p></article>',
    articles_html
)

print(f"Total articles: {len(cards)}")

PER_PAGE = 8

pages = []
for i in range(0, len(cards), PER_PAGE):
    pages.append(cards[i:i+PER_PAGE])

print(f"Pages needed: {len(pages)}")
for idx, pg in enumerate(pages):
    print(f"  Page {idx+1}: {len(pg)} articles")

def article_card(href, title, desc, reading_time="15 мин чтения"):
    return f'''<article class="article-card">
<h2><a href="articles/{href}">{title}</a></h2>
<p>{desc}</p>
<div class="meta">{reading_time}</div>
</article>'''

def pagination_html(current, total_pages):
    parts = []
    if current > 1:
        prev_page = "index.html" if current == 2 else f"page{current-1}.html"
        parts.append(f'<a href="{prev_page}" class="page-link">←</a>')
    
    for p in range(1, total_pages + 1):
        if p == current:
            parts.append(f'<span class="page-link current">{p}</span>')
        elif p == 1:
            parts.append(f'<a href="index.html" class="page-link">1</a>')
        else:
            parts.append(f'<a href="page{p}.html" class="page-link">{p}</a>')
    
    if current < total_pages:
        next_page = "index.html" if current == 0 else f"page{current+1}.html"
        next_page = f"page{current+1}.html"
        parts.append(f'<a href="{next_page}" class="page-link">→</a>')
    
    return "".join(parts)

total = len(pages)

for page_idx, pg in enumerate(pages):
    page_num = page_idx + 1
    
    if page_num == 1:
        filename = "/tmp/opencode/index.html"
        h1_text = "Полезные статьи"
        title = "Напишу курсовую"
        desc = "Полезные статьи о том как написать курсовую работу. Страница 1."
        canonical = "index.html"
        hero_title = "Как написать курсовую работу?"
        section_title = "Полезные статьи"
    elif page_num <= 6:
        filename = f"/tmp/opencode/page{page_num}.html"
        h1_text = f"Полезные статьи — страница {page_num}"
        title = f"Страница {page_num} — Напишу курсовую"
        desc = f"Полезные статьи о том как написать курсовую работу. Страница {page_num}."
        canonical = f"page{page_num}.html"
        hero_title = h1_text
        section_title = "Полезные статьи"
    else:
        filename = f"/tmp/opencode/page{page_num}.html"
        h1_text = f"Курсовые по предметам — страница {page_num}"
        title = f"Страница {page_num} — Напишу курсовую"
        desc = f"Полезные статьи о том как написать курсовую работу. Страница {page_num} — курсовые по предметам."
        canonical = f"page{page_num}.html"
        hero_title = h1_text
        section_title = "Курсовые по предметам"
    
    cards_html = "\n".join(article_card(h, t, d) for h, t, d in pg)
    pag_html = pagination_html(page_num, total)
    
    page_html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://napishu-kursovuy.ru/{canonical}">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<header><div class="container"><a href="./" class="logo">напишу<span>курсовую</span>.ру</a><nav><a href="./">Главная</a><a href="articles/">Статьи</a></nav></div></header>
<section class="hero"><div class="container"><h1>{hero_title}</h1><p>Полезные статьи, инструкции и советы для студентов. А если нет времени — закажите курсовую у профессионалов.</p><a class="btn" href="https://ref.studwork.ru/?p=1049093" target="_blank" rel="noopener noreferrer">Заказать курсовую</a></div></section>
<div class="page"><div class="container"><h2 class="section-title">{section_title}</h2><div class="articles-grid">{cards_html}</div><div class="pagination">{pag_html}</div></div></div>
<footer><div class="container"><div><strong>напишукурсовую.ру</strong> — полезные статьи для студентов</div><div><a href="https://ref.studwork.ru/?p=1049093" target="_blank">Биржа студенческих работ</a></div><div><a href="sitemap.xml">Карта сайта</a></div></div></footer>
</body>
</html>'''
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"Written {filename} ({len(pg)} articles)")

print("\nDone! All pages rebalanced.")
