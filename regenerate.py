#!/usr/bin/env python3
import os, re, json, time, sys, html as html_mod
from pathlib import Path
from openai import OpenAI

ARTICLES_DIR = Path("/tmp/opencode/articles")
API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"
SKIP = {"index.html"}
PROGRESS_FILE = Path("/tmp/groq_progress.json")

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

def extract_h1(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    return html_mod.unescape(m.group(1).strip()) if m else ""

def extract_meta(html, name):
    m = re.search(fr'<meta\s+name="{name}"\s+content="(.*?)"\s*/?>', html)
    return m.group(1) if m else ""

def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html)
    return m.group(1) if m else ""

def build_prompt(topic):
    return f"""Напиши подробную экспертную статью на русском языке для студенческого сайта.

Тема: {topic}

ТРЕБОВАНИЯ:
- Объём: 2500-3500 слов
- Глубокое раскрытие темы, практическая ценность для студентов
- Грамотный литературный русский язык, без орфографических и стилистических ошибок
- Формат: HTML с тегами <h2>, <h3>, <p>, <ul>, <li>, <strong>
- Первый абзац — введение, затем разделы с <h2> (3-4 раздела), в конце — заключение
- НЕ используй <h1> — заголовок уже есть на странице
- НЕ используй markdown — только HTML-теги
- НЕ добавляй CTA-блок

Верни ТОЛЬКО HTML-код содержимого статьи (без <html>, <head>, <body>)."""

def generate(topic, retries=5):
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Ты — эксперт по написанию студенческих работ. Пишешь длинные, грамотные, подробные статьи на русском языке. Отвечаешь только HTML-кодом."},
                    {"role": "user", "content": build_prompt(topic)}
                ],
                temperature=0.7,
                max_tokens=8192
            )
            return r.choices[0].message.content
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower() or "limit" in err_str.lower():
                w = min(30 * (attempt + 1), 120)
                print(f"  ⏳ rate limit, wait {w}s...")
                time.sleep(w)
            else:
                print(f"  ❌ {err_str[:200]}")
                if attempt < retries - 1:
                    time.sleep(10)
    return None

def make_html(filename, topic, body, meta_desc, html_title):
    body = body.strip()
    if body.startswith("```html"):
        body = body[7:]
    if body.startswith("```"):
        body = body[3:]
    if body.endswith("```"):
        body = body[:-3]
    body = body.strip()

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_title}</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="https://napishu-kursovuy.ru/articles/{filename}">
<link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
<header>
<div class="container">
<a href="../" class="logo">напишу<span>курсовую</span>.ру</a>
<nav><a href="../">Главная</a><a href="./">Статьи</a></nav>
</div>
</header>
<div class="page"><div class="container"><article class="article-content">
<div class="breadcrumbs"><a href="../">Главная</a><span>›</span>{topic}</div>
<h1>{topic}</h1>
<div class="meta">Обновлено: июль 2026 • Время чтения: 15 минут</div>
{body}
<div class="cta-box">
<h3>Нужна помощь с курсовой?</h3>
<p>Закажите написание курсовой работы у профессионалов на проверенной бирже Studwork. Гарантия качества, бесплатные доработки, соблюдение сроков.</p>
<a class="btn" href="https://ref.studwork.ru/?p=1049093" target="_blank" rel="noopener noreferrer">Заказать курсовую</a>
</div>
</article></div></div>
<footer><div class="container">
<div><strong>напишукурсовую.ру</strong> — полезные статьи для студентов</div>
<div><a href="https://ref.studwork.ru/?p=1049093" target="_blank">Биржа студенческих работ</a></div>
</div></footer>
</body>
</html>"""

def load_progress():
    if PROGRESS_FILE.exists():
        return set(json.loads(PROGRESS_FILE.read_text()))
    return set()

def save_progress(done):
    PROGRESS_FILE.write_text(json.dumps(list(done)))

def main():
    files = sorted(f for f in ARTICLES_DIR.iterdir() if f.suffix == ".html" and f.name not in SKIP)
    done = load_progress()

    remaining = [f for f in files if f.name not in done]
    print(f"Total: {len(files)}, Already done: {len(done)}, Remaining: {len(remaining)}")

    for i, fp in enumerate(remaining):
        name = fp.name
        print(f"\n[{i+1}/{len(remaining)}] {name}")
        
        html = fp.read_text("utf-8")
        topic = extract_h1(html)
        if not topic:
            print("  ⚠️ no h1, skip")
            done.add(name)
            save_progress(done)
            continue

        meta_desc = extract_meta(html, "description")
        html_title = extract_title(html) or topic
        
        print(f"  📝 {topic[:70]}...")
        
        body = generate(topic)
        if not body:
            print("  ❌ failed after retries, skip")
            continue

        new_html = make_html(name, topic, body, meta_desc, html_title)
        fp.write_text(new_html, "utf-8")
        word_count = len(body.split())
        print(f"  ✅ saved (~{word_count} слов, {len(body)} chars)")

        done.add(name)
        save_progress(done)

        if i < len(remaining) - 1:
            time.sleep(3)

    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
