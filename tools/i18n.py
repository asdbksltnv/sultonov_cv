#!/usr/bin/env python3
"""Build the Uzbek (uz/) and Russian (ru/) pages from the English pages.

tools/pages.py builds the English pages (index.html, about.html, ...) from
src/, and this script translates each of them. Edit src/, then run from the
site folder:

    python3 tools/build.py

Every English string below must still be found in the source pages, and the
script stops with an error if one is missing, so a translation can never
silently drift out of date. New English text that is not in the table is
listed as a warning so you can add it.

Published paper and poster titles, journal names, institution names and
author names are kept in English on purpose.
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages  # noqa: E402

PAGES = [p["file"] for p in pages.PAGES]  # the blog has its own builder: tools/blog.py
LANGS = {"uz": "uz_UZ", "ru": "ru_RU"}
BASE = "https://asadbeksultonov.com/"

# Page names, used in the menu cards, previous/next links and breadcrumbs.
NAMES = [
    ("Home", "Bosh sahifa", "Главная"),
    ("About", "Men haqimda", "Обо мне"),
    ("Experience", "Tajriba", "Опыт"),
    ("Research", "Tadqiqotlar", "Исследования"),
    ("Achievements", "Yutuqlar", "Достижения"),
    ("Skills", "Koʻnikmalar", "Навыки"),
    ("Contact", "Aloqa", "Контакты"),
    ("Projects", "Loyihalar", "Проекты"),
    ("Blog", "Blog", "Блог"),
]

# (English, Uzbek, Russian). Longer, more specific strings come first.
T = [
    # ---------- page titles and descriptions ----------
    ("About Asadbek Sultonov · Orthopedic surgery resident in Tashkent",
     "Asadbek Sultonov haqida · Toshkentdagi ortopediya ordinatori",
     "Об Асадбеке Султонове · ординатор по ортопедии в Ташкенте"),
    ("Asadbek Sultonov, PGY2 orthopedic surgery resident at Akfa Medline University Hospital in Tashkent: trauma, arthroplasty, arthroscopy and clinical AI.",
     "Asadbek Sultonov – Toshkentdagi Akfa Medline University Hospital ortopediya ordinatori: travmatologiya, artroplastika, artroskopiya va klinik AI.",
     "Асадбек Султонов – ординатор по ортопедии в Akfa Medline University Hospital, Ташкент: травматология, артропластика, артроскопия и клинический ИИ."),
    ("Clinical experience · Asadbek Sultonov",
     "Klinik tajriba · Asadbek Sultonov",
     "Клинический опыт · Асадбек Султонов"),
    ("The clinical and professional path of Asadbek Sultonov: orthopedic surgery residency and research at Akfa Medline, teaching, and earlier clinical roles since 2019.",
     "Asadbek Sultonovning klinik va kasbiy yoʻli: Akfa Medlineda ortopediya ordinaturasi va ilmiy ish, oʻqituvchilik hamda 2019 yildan buyongi klinik lavozimlar.",
     "Клинический и профессиональный путь Асадбека Султонова: ординатура по ортопедии и исследования в Akfa Medline, преподавание и клиническая работа с 2019 года."),
    ("Research and publications · Asadbek Sultonov",
     "Tadqiqotlar va nashrlar · Asadbek Sultonov",
     "Исследования и публикации · Асадбек Султонов"),
    ("Publications, conference talks and applied AI research by Asadbek Sultonov, including a Q1 systematic review and an AAHKS 2026 ePoster.",
     "Asadbek Sultonovning nashrlari, maʼruzalari va amaliy AI tadqiqotlari, jumladan Q1 jurnaldagi tizimli sharh va AAHKS 2026 ePosteri.",
     "Публикации, доклады и прикладные исследования ИИ Асадбека Султонова, включая систематический обзор в журнале Q1 и ePoster на AAHKS 2026."),
    ("Awards and certifications · Asadbek Sultonov",
     "Mukofotlar va sertifikatlar · Asadbek Sultonov",
     "Награды и сертификаты · Асадбек Султонов"),
    ("Medical olympiad awards, the AKFA MEDINNOVA gold medal, USMLE Step 1, AHA ACLS and BLS certification and continuing medical education of Asadbek Sultonov.",
     "Asadbek Sultonovning tibbiyot olimpiadalaridagi mukofotlari, AKFA MEDINNOVA oltin medali, USMLE Step 1, AHA ACLS va BLS sertifikatlari hamda uzluksiz tibbiy taʼlimi.",
     "Награды медицинских олимпиад, золотая медаль AKFA MEDINNOVA, USMLE Step 1, сертификаты AHA ACLS и BLS и непрерывное медицинское образование Асадбека Султонова."),
    ("Skills · Asadbek Sultonov",
     "Koʻnikmalar · Asadbek Sultonov",
     "Навыки · Асадбек Султонов"),
    ("Clinical, research and technical skills of Asadbek Sultonov, from evidence based medicine and meta-analysis to data analysis in Python.",
     "Asadbek Sultonovning klinik, ilmiy va texnik koʻnikmalari: dalillarga asoslangan tibbiyot va meta-tahlildan Pythonda maʼlumotlar tahliligacha.",
     "Клинические, исследовательские и технические навыки Асадбека Султонова: от доказательной медицины и метаанализа до анализа данных на Python."),
    ("Contact · Asadbek Sultonov",
     "Aloqa · Asadbek Sultonov",
     "Контакты · Асадбек Султонов"),
    ("Contact Asadbek Sultonov, orthopedic surgery resident at Akfa Medline University Hospital in Tashkent, about research collaborations and clinical projects.",
     "Ilmiy hamkorlik va klinik loyihalar boʻyicha Toshkentdagi Akfa Medline University Hospital ortopediya ordinatori Asadbek Sultonov bilan bogʻlaning.",
     "Свяжитесь с Асадбеком Султоновым, ординатором по ортопедии в Akfa Medline University Hospital в Ташкенте, по вопросам научного сотрудничества и клинических проектов."),
    ("Projects · Asadbek Sultonov",
     "Loyihalar · Asadbek Sultonov",
     "Проекты · Асадбек Султонов"),
    ("Software by Asadbek Sultonov, including 3D Anatomiya Laboratoriyasi, a free interactive 3D anatomy atlas for Uzbek-speaking medical students.",
     "Asadbek Sultonov yaratgan dasturlar, jumladan 3D Anatomiya Laboratoriyasi – oʻzbek tilida oʻqiydigan tibbiyot talabalari uchun bepul interaktiv 3D anatomiya atlasi.",
     "Программы Асадбека Султонова, в том числе 3D Anatomiya Laboratoriyasi – бесплатный интерактивный 3D атлас анатомии для студентов медицинских вузов, обучающихся на узбекском языке."),

    # ---------- page headers, home page cards, previous/next ----------
    ("Who I am, where I trained and the languages I work in.",
     "Men kimman, qayerda taʼlim olganman va qaysi tillarda ishlayman.",
     "Кто я, где учился и на каких языках работаю."),
    ("<h1 class=\"heading-2 hero-title\">Get in touch</h1>",
     "<h1 class=\"heading-2 hero-title\">Bogʻlanish</h1>",
     "<h1 class=\"heading-2 hero-title\">Связаться со мной</h1>"),
    ("Email is the best way to reach me. I'm based at Akfa Medline University Hospital in Tashkent, Uzbekistan.",
     "Men bilan bogʻlanishning eng yaxshi yoʻli – elektron pochta. Toshkentdagi Akfa Medline University Hospitalda ishlayman.",
     "Лучше всего писать мне на электронную почту. Я работаю в Akfa Medline University Hospital в Ташкенте."),
    ("Explore my work", "Faoliyatim bilan tanishing", "Моя работа"),
    ("Clinical training, research, awards and skills, each on its own page.",
     "Klinik tayyorgarlik, tadqiqotlar, mukofotlar va koʻnikmalar – har biri alohida sahifada.",
     "Клиническая подготовка, исследования, награды и навыки – каждая тема на отдельной странице."),
    ("Background, education and the languages I work in.", "Tarjimai hol, taʼlim va ish tillarim.", "Биография, образование и языки, на которых я работаю."),
    ("Residency, research and teaching roles since 2019.", "2019 yildan buyon ordinatura, ilmiy ish va oʻqituvchilik.", "Ординатура, исследования и преподавание с 2019 года."),
    ("Publications, conference presentations and applied AI projects.", "Nashrlar, konferensiyalardagi maʼruzalar va amaliy AI loyihalari.", "Публикации, доклады на конференциях и прикладные проекты ИИ."),
    ("Olympiad awards, certificates and life support credentials.", "Olimpiada mukofotlari, sertifikatlar va hayotni qoʻllab-quvvatlash guvohnomalari.", "Награды олимпиад, сертификаты и удостоверения по реанимации."),
    ("Clinical, research and technical skills.", "Klinik, ilmiy va texnik koʻnikmalar.", "Клинические, исследовательские и технические навыки."),
    ("A free 3D anatomy atlas I built for medical students.", "Tibbiyot talabalari uchun yaratgan bepul 3D anatomiya atlasim.", "Бесплатный 3D атлас анатомии, который я создал для студентов медицинских вузов."),
    ("Conferences, clinical training and moments from my medical career.", "Konferensiyalar, klinik tayyorgarlik va tibbiy faoliyatimdagi lahzalar.", "Конференции, клиническая подготовка и моменты из моей медицинской карьеры."),
    ("<span>Contact details</span>", "<span>Aloqa maʼlumotlari</span>", "<span>Контакты</span>"),
    ('aria-label="More pages"', 'aria-label="Boshqa sahifalar"', 'aria-label="Другие страницы"'),
    ('</svg>Previous</span>', '</svg>Oldingi</span>', '</svg>Назад</span>'),
    ('>Next<svg', '>Keyingi<svg', '>Далее<svg'),
] + [
    (pat % n[0], pat % n[1], pat % n[2])
    for pat, names in (
        ('<span class="title-3">%s</span>', NAMES),                        # previous/next links
        ('<h3 class="title-1">%s</h3>', [n for n in NAMES if n[0] not in ("Home", "Contact")]),  # home page cards
        ('"name": "%s"', NAMES[:8]),                                         # breadcrumbs
    )
    for n in names
] + [
    # ---------- head ----------
    ("Orthopedic surgery resident and clinical AI researcher",
     "Ortopediya ordinatori va klinik sunʼiy intellekt tadqiqotchisi",
     "Ординатор по ортопедии и исследователь в области клинического ИИ"),
    ("Asadbek Sultonov, PGY2 orthopedic surgery resident at Akfa Medline University Hospital in Tashkent, researching bone regeneration and AI for knee osteoarthritis.",
     "Asadbek Sultonov – Toshkentdagi Akfa Medline University Hospital ortopediya ordinatori. Suyak regeneratsiyasi va tizza osteoartriti uchun AI boʻyicha tadqiqotlar.",
     "Асадбек Султонов – ординатор по ортопедии в Akfa Medline University Hospital в Ташкенте. Исследует регенерацию кости и ИИ для оценки остеоартрита колена."),
    ("PGY2 orthopedic surgery resident at Akfa Medline University Hospital. Clinical work, applied AI research, publications and awards.",
     "Akfa Medline University Hospital ortopediya ordinatori. Klinik ish, amaliy AI tadqiqotlari, nashrlar va mukofotlar.",
     "Ординатор по ортопедии в Akfa Medline University Hospital. Клиническая работа, прикладные исследования ИИ, публикации и награды."),
    ('content="Asadbek Sultonov logo: a letter A formed by a knee joint, with the words Orthopaedic surgeon"',
     'content="Asadbek Sultonov logotipi: tizza boʻgʻimidan hosil boʻlgan A harfi va Orthopaedic surgeon yozuvi"',
     'content="Логотип Асадбека Султонова: буква A, образованная коленным суставом, и надпись Orthopaedic surgeon"'),

    # ---------- navigation and shared UI ----------
    (">Skip to content<", ">Asosiy matnga oʻtish<", ">Перейти к содержанию<"),
    ('aria-label="Main"', 'aria-label="Asosiy menyu"', 'aria-label="Основное меню"'),
    ('aria-label="Asadbek Sultonov, home"', 'aria-label="Asadbek Sultonov, bosh sahifa"', 'aria-label="Asadbek Sultonov, главная"'),
    ('aria-label="Language"', 'aria-label="Til"', 'aria-label="Язык"'),
    ('aria-label="Open menu" data-label-open="Open menu" data-label-close="Close menu"',
     'aria-label="Menyuni ochish" data-label-open="Menyuni ochish" data-label-close="Menyuni yopish"',
     'aria-label="Открыть меню" data-label-open="Открыть меню" data-label-close="Закрыть меню"'),
    (">About</a>", ">Men haqimda</a>", ">Обо мне</a>"),
    (">Experience</a>", ">Tajriba</a>", ">Опыт</a>"),
    (">Research</a>", ">Tadqiqotlar</a>", ">Исследования</a>"),
    (">Achievements</a>", ">Yutuqlar</a>", ">Достижения</a>"),
    (">Skills</a>", ">Koʻnikmalar</a>", ">Навыки</a>"),
    (">Projects</a>", ">Loyihalar</a>", ">Проекты</a>"),
    (">Blog</a>", ">Blog</a>", ">Блог</a>"),
    (">Contact</a>", ">Aloqa</a>", ">Контакты</a>"),
    ("<span>Blog</span>", "<span>Blog</span>", "<span>Блог</span>"),
    ("<span>Back to top</span>", "<span>Yuqoriga</span>", "<span>Наверх</span>"),
    ('aria-label="Image viewer"', 'aria-label="Rasmni koʻrish"', 'aria-label="Просмотр изображения"'),
    ('aria-label="Close"', 'aria-label="Yopish"', 'aria-label="Закрыть"'),
    ("(opens in a new tab)", "(yangi oynada ochiladi)", "(откроется в новой вкладке)"),

    # ---------- hero ----------
    ("Orthopedic resident<br> at AMUH", "AMUH ortopediya<br> ordinatori", "Ординатор<br> по ортопедии в AMUH"),
    ("<strong>I'm Asadbek Sultonov,</strong> a PGY2 resident at Akfa Medline University Hospital in Tashkent, interested in arthroplasty, arthroscopy and AI in orthopedics.",
     "<strong>Men Asadbek Sultonov,</strong> Toshkentdagi Akfa Medline University Hospital ikkinchi yil ordinatoriman. Artroplastika, artroskopiya va ortopediyada sunʼiy intellektga qiziqaman.",
     "<strong>Я Асадбек Султонов,</strong> ординатор второго года в Akfa Medline University Hospital в Ташкенте. Интересуюсь артропластикой, артроскопией и применением ИИ в ортопедии."),
    ("<span>Email me</span>", "<span>Menga yozing</span>", "<span>Написать мне</span>"),
    ('aria-label="Highlights"', 'aria-label="Asosiy yutuqlar"', 'aria-label="Главное"'),
    ("AAHKS 2026 ePoster, under 15% acceptance", "AAHKS 2026 ePoster, qabul darajasi 15% dan past", "ePoster на AAHKS 2026, отбор менее 15%"),
    ("<li>Q1 systematic review, 2026</li>", "<li>Q1 jurnalda tizimli sharh, 2026</li>", "<li>Систематический обзор в журнале Q1, 2026</li>"),
    ("USMLE Step 1 passed", "USMLE Step 1 topshirilgan", "USMLE Step 1 сдан"),
    ('alt="Asadbek Sultonov in a suit, speaking at a podium"',
     'alt="Asadbek Sultonov kostyumda, minbarda nutq soʻzlamoqda"',
     'alt="Асадбек Султонов в костюме выступает за трибуной"'),
    ("Akfa Medline University Hospital, Tashkent", "Akfa Medline University Hospital, Toshkent", "Akfa Medline University Hospital, Ташкент"),
    (">MD overall GPA<", ">MD umumiy GPA<", ">Общий GPA (MD)<"),
    (">Published papers<", ">Chop etilgan maqolalar<", ">Опубликованные статьи<"),
    (">Competition awards<", ">Tanlov mukofotlari<", ">Награды конкурсов<"),
    (">Languages<", ">Tillar<", ">Языки<"),
    (">Pass</dd>", ">Topshirgan</dd>", ">Сдан</dd>"),

    # ---------- about ----------
    ("Clinical training, research and teaching", "Klinik tayyorgarlik, ilmiy tadqiqot va oʻqitish", "Клиническая подготовка, исследования и преподавание"),
    ("I'm a PGY2 orthopedic surgery resident at Akfa Medline University Hospital with a strong interest in trauma, orthopedics, evidence based medicine and clinical research. I prepare journal clubs, appraise the literature, and write educational material for patients and for the hospital website.",
     "Men Akfa Medline University Hospital klinikasida ikkinchi yil ortopediya ordinatoriman. Travmatologiya, ortopediya, dalillarga asoslangan tibbiyot va klinik tadqiqotlarga katta qiziqishim bor. Jurnal klublarini tayyorlayman, ilmiy adabiyotlarni tahlil qilaman, bemorlar va shifoxona sayti uchun oʻquv materiallari yozaman.",
     "Я ординатор второго года по ортопедии в Akfa Medline University Hospital. Меня особенно интересуют травматология, ортопедия, доказательная медицина и клинические исследования. Готовлю журнальные клубы, анализирую научную литературу и пишу образовательные материалы для пациентов и для сайта больницы."),
    ("I also have practical experience organizing conferences, handling research data and writing Python for research workflows. That work now extends into applied machine learning, including a calibrated deep learning model for automated knee osteoarthritis grading. My goal is an academic career that combines clinical practice, research and medical education.",
     "Konferensiyalar tashkil qilish, ilmiy maʼlumotlar bilan ishlash va tadqiqot uchun Python kodi yozish boʻyicha amaliy tajribam bor. Bu ish endi amaliy mashinaviy oʻrganishga kengaydi, jumladan tizza osteoartritini avtomatik baholovchi kalibrlangan chuqur oʻrganish modeliga. Maqsadim klinik amaliyot, ilmiy tadqiqot va tibbiy taʼlimni birlashtirgan akademik faoliyat.",
     "Также у меня есть практический опыт организации конференций, работы с исследовательскими данными и написания кода на Python для научных задач. Сейчас эта работа включает прикладное машинное обучение, в том числе калиброванную модель глубокого обучения для автоматической оценки остеоартрита коленного сустава. Моя цель – академическая карьера, которая объединяет клиническую практику, исследования и медицинское образование."),
    ('aria-label="Interests"', 'aria-label="Qiziqishlar"', 'aria-label="Интересы"'),
    (">Trauma and orthopedics<", ">Travmatologiya va ortopediya<", ">Травматология и ортопедия<"),
    (">Evidence based medicine<", ">Dalillarga asoslangan tibbiyot<", ">Доказательная медицина<"),
    (">Arthroplasty and arthroscopy<", ">Artroplastika va artroskopiya<", ">Артропластика и артроскопия<"),
    (">PubMed and NEJM research<", ">PubMed va NEJM boʻyicha izlanish<", ">Работа с PubMed и NEJM<"),
    (">Applied AI and deep learning<", ">Amaliy AI va chuqur oʻrganish<", ">Прикладной ИИ и глубокое обучение<"),
    (">Medical Telegram bots<", ">Tibbiy Telegram botlar<", ">Медицинские боты в Telegram<"),
    (">Data visualization<", ">Maʼlumotlarni vizuallashtirish<", ">Визуализация данных<"),
    (">Education</h2>", ">Taʼlim</h2>", ">Образование</h2>"),
    ("Doctor of Medicine (MD)", "Tibbiyot doktori (MD)", "Доктор медицины (MD)"),
    ("Central Asian University, Tashkent · GPA 3.81", "Central Asian University, Toshkent · GPA 3.81", "Central Asian University, Ташкент · GPA 3.81"),
    ("<strong>High school</strong>", "<strong>Maktab</strong>", "<strong>Школа</strong>"),
    ("1-maktab, Andijan shahar", "1-maktab, Andijon shahri", "Школа №1, Андижан"),
    ('aria-label="Native, 5 of 5"', 'aria-label="Ona tili, 5 dan 5"', 'aria-label="Родной, 5 из 5"'),
    ('aria-label="Advanced, 4 of 5"', 'aria-label="Yuqori, 5 dan 4"', 'aria-label="Продвинутый, 4 из 5"'),
    ('aria-label="Basic, 2 of 5"', 'aria-label="Boshlangʻich, 5 dan 2"', 'aria-label="Базовый, 2 из 5"'),
    (">Uzbek</span>", ">Oʻzbek</span>", ">Узбекский</span>"),
    (">English</span>", ">Ingliz</span>", ">Английский</span>"),
    (">Russian</span>", ">Rus</span>", ">Русский</span>"),
    (">German</span>", ">Nemis</span>", ">Немецкий</span>"),
    (">Native</span>", ">Ona tili</span>", ">Родной</span>"),
    (">Advanced</span>", ">Yuqori</span>", ">Продвинутый</span>"),
    (">Basic</span>", ">Boshlangʻich</span>", ">Базовый</span>"),

    # ---------- tagline ----------
    ('aria-label="Approach"', 'aria-label="Yondashuv"', 'aria-label="Подход"'),
    ('<span class="line">Clinician first,</span>', '<span class="line">Avvalo shifokor,</span>', '<span class="line">Прежде всего врач,</span>'),
    ('<span class="line">researcher by habit.</span>', '<span class="line">tadqiqot esa odatim.</span>', '<span class="line">исследователь по привычке.</span>'),
    ('<span class="line">Working where trauma care,</span>', '<span class="line">Travmatologiya, dalillar</span>', '<span class="line">Работаю на стыке травматологии,</span>'),
    ('<span class="line">evidence and clinical AI meet.</span>', '<span class="line">va klinik AI kesishgan joyda ishlayman.</span>', '<span class="line">доказательной медицины и клинического ИИ.</span>'),

    # ---------- experience ----------
    ("Clinical and professional path", "Klinik va kasbiy yoʻl", "Клинический и профессиональный путь"),
    ("Medical school, clinical work, research and teaching since 2019. Three of these roles run in parallel today.",
     "2019 yildan beri tibbiyot taʼlimi, klinik ish, ilmiy tadqiqot va oʻqitish. Bugun ulardan uchtasi parallel davom etmoqda.",
     "Медицинский университет, клиническая работа, исследования и преподавание с 2019 года. Сейчас три из этих ролей идут параллельно."),
    ("Roles over time, 2019 to today", "Lavozimlar xronologiyasi, 2019 yildan bugungacha", "Роли во времени, с 2019 года по сегодня"),
    ("Hover or tab through the bars for dates.", "Sanalarni koʻrish uchun ustunlar ustiga olib boring yoki Tab tugmasini bosing.", "Наведите курсор или нажмите Tab, чтобы увидеть даты."),
    ("</i>Ongoing</li>", "</i>Davom etmoqda</li>", "</i>Текущие</li>"),
    ("</i>Completed</li>", "</i>Yakunlangan</li>", "</i>Завершённые</li>"),
    ("<summary>View as table</summary>", "<summary>Jadval koʻrinishida</summary>", "<summary>Показать таблицей</summary>"),
    ('data-label="Timeline of roles from 2019 to today" data-today="Today"',
     'data-label="2019 yildan bugungacha lavozimlar xronologiyasi" data-today="Bugun"',
     'data-label="Хронология ролей с 2019 года по сегодня" data-today="Сегодня"'),
    (">Role</th>", ">Lavozim</th>", ">Роль</th>"),
    (">Organisation</th>", ">Tashkilot</th>", ">Организация</th>"),
    (">Dates</th>", ">Sanalar</th>", ">Даты</th>"),
    ("<td>MD student</td>", "<td>MD talabasi</td>", "<td>Студент медицинского факультета</td>"),
    ("<td>Teacher</td>", "<td>Oʻqituvchi</td>", "<td>Преподаватель</td>"),
    ("<td>Physician assistant</td>", "<td>Shifokor yordamchisi</td>", "<td>Ассистент врача</td>"),
    ("<td>Call centre agent</td>", "<td>Call markaz operatori</td>", "<td>Оператор call центра</td>"),
    ("<td>Research assistant</td>", "<td>Ilmiy yordamchi</td>", "<td>Научный ассистент</td>"),
    ("<td>Orthopedic resident</td>", "<td>Ortopediya ordinatori</td>", "<td>Ординатор по ортопедии</td>"),
    ('<span class="badge">Current</span>', '<span class="badge">Hozirgi</span>', '<span class="badge">Текущая</span>'),
    ("Orthopedic surgery resident, PGY2", "Ortopediya ordinatori, ikkinchi yil", "Ординатор по ортопедии, второй год"),
    ("Take part in orthopedic inpatient, outpatient and operative care under supervision.",
     "Nazorat ostida statsionar, ambulator va operatsion ortopedik yordamda ishtirok etaman.",
     "Участвую в стационарной, амбулаторной и оперативной ортопедической помощи под руководством наставников."),
    ("Assist with clinical assessment, perioperative workflow, documentation and patient education.",
     "Klinik baholash, perioperatsion jarayon, hujjatlashtirish va bemorlarni oʻqitishda yordam beraman.",
     "Помогаю с клинической оценкой, периоперационным процессом, документацией и обучением пациентов."),
    ("Building focused interests in trauma, arthroplasty, arthroscopy and evidence based orthopedic practice.",
     "Travmatologiya, artroplastika, artroskopiya va dalillarga asoslangan ortopedik amaliyotga yoʻnalgan qiziqishlarimni rivojlantirmoqdaman.",
     "Развиваю профильные интересы в травматологии, артропластике, артроскопии и доказательной ортопедической практике."),
    ("Helped optimize hospital operations planning with AI scheduling and workflow tools.",
     "AI asosidagi jadval tuzish va ish jarayoni vositalari yordamida shifoxona faoliyatini rejalashtirishni optimallashtirishga hissa qoʻshdim.",
     "Помог оптимизировать планирование работы больницы с помощью инструментов ИИ для расписания и рабочих процессов."),
    ("Developing a calibrated deep learning model for automated knee osteoarthritis grading, accepted as a poster at the 2026 AAHKS Annual Meeting.",
     "Tizza osteoartritini avtomatik baholash uchun kalibrlangan chuqur oʻrganish modelini ishlab chiqmoqdaman; ish 2026 yilgi AAHKS yillik yigʻilishida poster sifatida qabul qilindi.",
     "Разрабатываю калиброванную модель глубокого обучения для автоматической оценки остеоартрита коленного сустава; работа принята в виде постера на ежегодном собрании AAHKS 2026."),
    (">Research assistant</h2>", ">Ilmiy yordamchi</h2>", ">Научный ассистент</h2>"),
    ("Akfa Medline, Tashkent", "Akfa Medline, Toshkent", "Akfa Medline, Ташкент"),
    ("Run literature reviews on PubMed and Google Scholar for journal club sessions.",
     "Jurnal klubi mashgʻulotlari uchun PubMed va Google Scholarda adabiyot sharhlarini tayyorlayman.",
     "Провожу обзоры литературы в PubMed и Google Scholar для журнальных клубов."),
    ("Write patient education materials, including surgery information brochures.",
     "Bemorlar uchun oʻquv materiallari, jumladan jarrohlik haqidagi maʼlumot broshyuralarini yozaman.",
     "Пишу обучающие материалы для пациентов, в том числе информационные брошюры об операциях."),
    ("Publish medical articles and educational content on the Akfa Medline website.",
     "Akfa Medline saytida tibbiy maqolalar va maʼrifiy kontent eʼlon qilaman.",
     "Публикую медицинские статьи и образовательные материалы на сайте Akfa Medline."),
    (">Teacher</h2>", ">Oʻqituvchi</h2>", ">Преподаватель</h2>"),
    ("Muzaffar Online Education, Andijan", "Muzaffar Online Education, Andijon", "Muzaffar Online Education, Андижан"),
    ("Helped cofound one of the largest English learning platforms in Uzbekistan.",
     "Oʻzbekistondagi eng yirik ingliz tili oʻrganish platformalaridan biriga asos solishda ishtirok etdim.",
     "Участвовал в создании одной из крупнейших платформ для изучения английского языка в Узбекистане."),
    ("Work with students directly and give structured feedback on their writing.",
     "Talabalar bilan bevosita ishlayman va ularning yozma ishlariga tizimli fikr bildiraman.",
     "Работаю со студентами напрямую и даю структурированную обратную связь по их письменным работам."),
    (">Call centre agent</h2>", ">Call markaz operatori</h2>", ">Оператор call центра</h2>"),
    ("CAU Pulse, Tashkent", "CAU Pulse, Toshkent", "CAU Pulse, Ташкент"),
    ("Worked with the team to improve call handling processes and service quality.",
     "Jamoa bilan birga qoʻngʻiroqlarga ishlov berish jarayonlari va xizmat sifatini yaxshiladim.",
     "Вместе с командой улучшал обработку звонков и качество обслуживания."),
    (">Physician assistant</h2>", ">Shifokor yordamchisi</h2>", ">Ассистент врача</h2>"),
    ("Neuronet Ultra, Andijan", "Neuronet Ultra, Andijon", "Neuronet Ultra, Андижан"),
    ("Carried out supervised patient assessments to support diagnosis and treatment planning.",
     "Tashxis va davolashni rejalashtirish uchun nazorat ostida bemorlarni koʻrikdan oʻtkazdim.",
     "Под руководством врача проводил осмотр пациентов для диагностики и планирования лечения."),
    ("Assisted with the management of patients with back pain and with medication administration.",
     "Bel ogʻrigʻi boʻlgan bemorlarni davolash va dori vositalarini qoʻllashda yordam berdim.",
     "Помогал в ведении пациентов с болью в спине и во введении лекарственных препаратов."),
    ("Created a patient record management platform.",
     "Bemorlar maʼlumotlarini boshqarish platformasini yaratdim.",
     "Создал платформу для ведения медицинских записей пациентов."),

    # ---------- research ----------
    ("Research and scholarly work", "Ilmiy tadqiqotlar va ilmiy ishlar", "Исследования и научная работа"),
    ("Two published papers, three conference presentations, and applied AI work that grew out of clinical questions.",
     "Ikkita chop etilgan maqola, uchta konferensiya maʼruzasi va klinik savollardan kelib chiqqan amaliy AI ishlari.",
     "Две опубликованные статьи, три доклада на конференциях и прикладные проекты ИИ, выросшие из клинических вопросов."),
    ('reveal">Publications <span', 'reveal">Nashrlar <span', 'reveal">Публикации <span'),
    ('reveal">Conference presentations <span', 'reveal">Konferensiya maʼruzalari <span', 'reveal">Доклады на конференциях <span'),
    ('reveal">Applied AI projects</h2>', 'reveal">Amaliy AI loyihalari</h2>', 'reveal">Прикладные проекты ИИ</h2>'),
    ('reveal">Innovation and examinations</h2>', 'reveal">Innovatsiyalar va imtihonlar</h2>', 'reveal">Инновации и экзамены</h2>'),
    ('reveal">Extracurricular and organizing</h2>', 'reveal">Darsdan tashqari va tashkiliy faoliyat</h2>', 'reveal">Внеучебная и организационная деятельность</h2>'),
    ('reveal">Certificates <span', 'reveal">Sertifikatlar <span', 'reveal">Сертификаты <span'),
    ('reveal">Other training</h2>', 'reveal">Boshqa oʻquv kurslari</h2>', 'reveal">Другое обучение</h2>'),
    ('"badge">Published paper<', '"badge">Chop etilgan maqola<', '"badge">Опубликованная статья<'),
    (">Q1 journal<", ">Q1 jurnal<", ">Журнал Q1<"),
    ('"badge">Oral presentation<', '"badge">Ogʻzaki maʼruza<', '"badge">Устный доклад<'),
    (">Travel grant<", ">Safar granti<", ">Грант на поездку<"),
    ('"badge">Poster<', '"badge">Poster<', '"badge">Постер<'),
    ('"badge">Deep learning<', '"badge">Chuqur oʻrganish<', '"badge">Глубокое обучение<'),
    ('"badge">Operations<', '"badge">Operatsion boshqaruv<', '"badge">Операционное управление<'),
    ('"badge">Group innovation project<', '"badge">Guruh innovatsion loyihasi<', '"badge">Групповой инновационный проект<'),
    ('"badge">Examination<', '"badge">Imtihon<', '"badge">Экзамен<'),
    ("13 authors, including", "13 muallif, jumladan", "13 авторов, в том числе"),
    ("Matluba Akbarali kizi Mirzaeva and James Tsoi", "Matluba Akbarali kizi Mirzaeva va James Tsoi", "Matluba Akbarali kizi Mirzaeva и James Tsoi"),
    ("Abstract A574 at the 2026 AAHKS Annual Meeting, November 5 to 8, Gaylord Texan Resort &amp; Convention Center, Grapevine, Texas. Presented as an ePoster with recorded audio and video.",
     "A574 tezisi, AAHKS 2026 yillik yigʻilishi, 5–8 noyabr, Gaylord Texan Resort &amp; Convention Center, Grapevine, Texas. Audio va video yozuvli ePoster sifatida taqdim etildi.",
     "Тезис A574, ежегодное собрание AAHKS 2026, 5–8 ноября, Gaylord Texan Resort &amp; Convention Center, Грейпвайн, Техас. Представлен как ePoster с аудио и видеозаписью."),
    ('aria-label="355 posters were selected from more than 2,400 submitted abstracts, an acceptance rate under 15 percent"',
     'aria-label="2 400 dan ortiq yuborilgan tezisdan 355 ta poster tanlandi, qabul darajasi 15 foizdan past"',
     'aria-label="Из более чем 2 400 поданных тезисов отобрано 355 постеров, доля принятых менее 15 процентов"'),
    (">acceptance rate<", ">qabul darajasi<", ">доля принятых<"),
    ("<b>355</b> posters selected", "<b>355</b> ta poster tanlandi", "<b>355</b> постеров отобрано"),
    ("<b>2,400+</b> abstracts submitted", "<b>2 400+</b> tezis yuborildi", "<b>2 400+</b> тезисов подано"),
    ("Abstract O-087, Podium Session 8: Pediatrics, KUA 2025, COEX Seoul, October 23, 2025. Submitted as a medical student and accepted for oral presentation. Awarded a KUA travel grant and attended with Dr. Azimdjon Tursunkulov, an endourologist in Tashkent.",
     "O-087 tezisi, podium sessiyasi 8: Pediatriya, KUA 2025, COEX, Seul, 2025 yil 23 oktabr. Tibbiyot talabasi sifatida yuborilgan va ogʻzaki maʼruzaga qabul qilingan. KUA safar grantiga sazovor boʻldim va toshkentlik endourolog Dr. Azimdjon Tursunkulov bilan birga qatnashdim.",
     "Тезис O-087, подиумная сессия 8: педиатрия, KUA 2025, COEX, Сеул, 23 октября 2025 года. Подан в статусе студента медицинского факультета и принят для устного доклада. Получил грант KUA на поездку и участвовал вместе с доктором Азимджоном Турсункуловым, эндоурологом из Ташкента."),
    ("Presented at an endocrinology conference at Central Asian University.",
     "Central Asian Universityda endokrinologiya konferensiyasida taqdim etilgan.",
     "Представлен на конференции по эндокринологии в Central Asian University."),
    ("Automated KL grading for knee osteoarthritis", "Tizza osteoartritini KL shkalasi boʻyicha avtomatik baholash", "Автоматическая оценка остеоартрита коленного сустава по шкале KL"),
    ("Trained and calibrated a transfer learning model that grades knee osteoarthritis severity on the Kellgren and Lawrence scale from plain radiographs. This is the work behind the AAHKS 2026 abstract.",
     "Oddiy rentgenogrammalar boʻyicha tizza osteoartriti ogʻirligini Kellgren va Lawrence shkalasida baholaydigan transfer learning modelini oʻqitdim va kalibrladim. AAHKS 2026 tezisi aynan shu ishga asoslangan.",
     "Обучил и откалибровал модель на основе transfer learning, которая оценивает тяжесть остеоартрита коленного сустава по шкале Kellgren и Lawrence на обычных рентгенограммах. Именно эта работа легла в основу тезиса AAHKS 2026."),
    ("AI assisted operations planning", "AI yordamida faoliyatni rejalashtirish", "Планирование работы с помощью ИИ"),
    ("Helped optimize clinical operations planning at Akfa Medline University Hospital with AI scheduling and workflow tools.",
     "Akfa Medline University Hospitalda AI asosidagi jadval tuzish va ish jarayoni vositalari yordamida klinik faoliyatni rejalashtirishni optimallashtirishga yordam berdim.",
     "Помог оптимизировать планирование клинической работы в Akfa Medline University Hospital с помощью инструментов ИИ для расписания и рабочих процессов."),
    ("Using Telegram Bots and 3D Printed Pill Boxes to Improve Medication Adherence",
     "Dori qabul qilish intizomini yaxshilash uchun Telegram botlar va 3D printerda bosilgan dori qutilari",
     "Telegram боты и таблетницы, напечатанные на 3D принтере, для повышения приверженности лечению"),
    ("Group leader. Gold Medal at AKFA MEDINNOVA Expo 2023.", "Guruh rahbari. AKFA MEDINNOVA Expo 2023 da oltin medal.", "Руководитель группы. Золотая медаль на AKFA MEDINNOVA Expo 2023."),
    ("USMLE Step 1, passed", "USMLE Step 1 topshirilgan", "USMLE Step 1 сдан"),
    ("Test date: September 3, 2024", "Imtihon sanasi: 2024 yil 3 sentyabr", "Дата экзамена: 3 сентября 2024 года"),
    (">CAEC25 Congress</dt>", ">CAEC25 kongressi</dt>", ">Конгресс CAEC25</dt>"),
    ("Website management, doctor registration support, programme brochure and logo design support.",
     "Veb sayt boshqaruvi, shifokorlarni roʻyxatga olishda yordam, dastur broshyurasi va logotip dizaynida koʻmak.",
     "Управление сайтом, помощь в регистрации врачей, программная брошюра и помощь с дизайном логотипа."),
    (">Center of Endocrinology</dt>", ">Endokrinologiya markazi</dt>", ">Центр эндокринологии</dt>"),
    ("Volunteer medical interpreter and case presenter.", "Koʻngilli tibbiy tarjimon va klinik holatlar taqdimotchisi.", "Волонтёр: медицинский переводчик и докладчик клинических случаев."),
    ("Interviewer and social media manager for a voluntary organization.", "Koʻngillilar tashkilotida intervyuer va SMM menejer.", "Интервьюер и SMM менеджер в волонтёрской организации."),
    ("Took part and qualified for the semifinals.", "Ishtirok etdim va yarim finalga chiqdim.", "Участвовал и вышел в полуфинал."),

    # ---------- achievements ----------
    ("Awards and certifications", "Mukofotlar va sertifikatlar", "Награды и сертификаты"),
    ("Four competition awards since 2023, along with AHA life support credentials and continuing medical education.",
     "2023 yildan beri toʻrtta tanlov mukofoti, shuningdek AHA reanimatsiya sertifikatlari va uzluksiz tibbiy taʼlim.",
     "Четыре награды конкурсов с 2023 года, а также сертификаты AHA по реанимации и непрерывное медицинское образование."),
    ("Milestones, 2023 to 2026", "Muhim voqealar, 2023–2026", "Ключевые события, 2023–2026"),
    ("Dated awards, presentations, publications and credentials, by month.",
     "Mukofotlar, maʼruzalar, nashrlar va sertifikatlar oylar boʻyicha.",
     "Награды, доклады, публикации и сертификаты по месяцам."),
    ("</i>Milestone</li>", "</i>Voqea</li>", "</i>Событие</li>"),
    ('data-label="Milestones by type from 2023 to 2026"', 'data-label="2023–2026 yillardagi voqealar turlari boʻyicha"', 'data-label="События по типам, 2023–2026"'),
    ('data-lane-labels="Publications|Presentations|Awards|Exams &amp; credentials"',
     'data-lane-labels="Nashrlar|Maʼruzalar|Mukofotlar|Imtihon va sertifikatlar"',
     'data-lane-labels="Публикации|Доклады|Награды|Экзамены и сертификаты"'),
    (">Date</th>", ">Sana</th>", ">Дата</th>"),
    (">Type</th>", ">Turi</th>", ">Тип</th>"),
    (">Milestone</th>", ">Voqea</th>", ">Событие</th>"),
    ("<td>Award</td>", "<td>Mukofot</td>", "<td>Награда</td>"),
    ("<td>Exam</td>", "<td>Imtihon</td>", "<td>Экзамен</td>"),
    ("<td>Credential</td>", "<td>Sertifikat</td>", "<td>Сертификат</td>"),
    ("<td>Presentation</td>", "<td>Maʼruza</td>", "<td>Доклад</td>"),
    ("<td>Publication</td>", "<td>Nashr</td>", "<td>Публикация</td>"),
    ("<td>Gold Medal, AKFA MEDINNOVA Expo</td>", "<td>Oltin medal, AKFA MEDINNOVA Expo</td>", "<td>Золотая медаль, AKFA MEDINNOVA Expo</td>"),
    ("<td>3rd place, Samarkand-2020 Olympiad (Neurology)</td>", "<td>3-oʻrin, Samarkand-2020 olimpiadasi (nevrologiya)</td>", "<td>3 место, олимпиада Samarkand-2020 (неврология)</td>"),
    ("<td>1st place, Medicine of the Future 2024</td>", "<td>1-oʻrin, Medicine of the Future 2024</td>", "<td>1 место, Medicine of the Future 2024</td>"),
    ("<td>1st place, Samarkand-2020 Olympiad (Neurology)</td>", "<td>1-oʻrin, Samarkand-2020 olimpiadasi (nevrologiya)</td>", "<td>1 место, олимпиада Samarkand-2020 (неврология)</td>"),
    ("<td>AHA ACLS and BLS provider</td>", "<td>AHA ACLS va BLS provayderi</td>", "<td>Провайдер AHA ACLS и BLS</td>"),
    ("<td>Oral presentation, KUA 2025, Seoul</td>", "<td>Ogʻzaki maʼruza, KUA 2025, Seul</td>", "<td>Устный доклад, KUA 2025, Сеул</td>"),
    ("<td>UpToDate CME, AMA PRA Category 1</td>", "<td>UpToDate CME, AMA PRA 1 toifa</td>", "<td>UpToDate CME, AMA PRA категории 1</td>"),
    ("<td>Q1 systematic review, Biomedical Materials &amp; Devices</td>", "<td>Q1 tizimli sharh, Biomedical Materials &amp; Devices</td>", "<td>Систематический обзор Q1, Biomedical Materials &amp; Devices</td>"),
    ("<td>ePoster, AAHKS 2026 Annual Meeting</td>", "<td>ePoster, AAHKS 2026 yillik yigʻilishi</td>", "<td>ePoster, ежегодное собрание AAHKS 2026</td>"),
    ('place">1st<', 'place">I<', 'place">I<'),
    ('place">3rd<', 'place">III<', 'place">III<'),
    ('place">Gold<', 'place">Oltin<', 'place">Золото<'),
    (">Samarkand-2020 Olympiad (Neurology)</h2>", ">Samarkand-2020 olimpiadasi (nevrologiya)</h2>", ">Олимпиада Samarkand-2020 (неврология)</h2>"),
    # IV before V: "V International..." is a substring of "IV International..."
    ("IV International Olympiad for Medical Students, Samarkand State Medical University",
     "Tibbiyot talabalarining IV xalqaro olimpiadasi, Samarqand davlat tibbiyot universiteti",
     "IV Международная олимпиада студентов медицинских вузов, Самаркандский государственный медицинский университет"),
    (">V International Olympiad for Medical Students, Samarkand State Medical University",
     ">Tibbiyot talabalarining V xalqaro olimpiadasi, Samarqand davlat tibbiyot universiteti",
     ">V Международная олимпиада студентов медицинских вузов, Самаркандский государственный медицинский университет"),
    ("Medical Olympiad “Medicine of the Future 2024”</h2>", "“Medicine of the Future 2024” tibbiyot olimpiadasi</h2>", "Медицинская олимпиада «Medicine of the Future 2024»</h2>"),
    ("Best science project and poster, as group leader", "Eng yaxshi ilmiy loyiha va poster, guruh rahbari sifatida", "Лучший научный проект и постер, в роли руководителя группы"),
    ("Diploma I, 1st place, V International Olympiad of Medical Students “Samarkand-2020”, December 13 to 14, 2024",
     "I darajali diplom, 1-oʻrin, tibbiyot talabalarining V xalqaro olimpiadasi “Samarkand-2020”, 2024 yil 13–14 dekabr",
     "Диплом I степени, 1 место, V Международная олимпиада студентов медицинских вузов «Samarkand-2020», 13–14 декабря 2024 года"),
    ("First place diploma from the V International Olympiad of Medical Students, Samarkand 2024",
     "Tibbiyot talabalarining V xalqaro olimpiadasi 1-oʻrin diplomi, Samarqand 2024",
     "Диплом за первое место на V Международной олимпиаде студентов медицинских вузов, Самарканд 2024"),
    (">Samarkand Olympiad, 1st place<", ">Samarqand olimpiadasi, 1-oʻrin<", ">Олимпиада в Самарканде, 1 место<"),
    ("Certificate, Medical Olympiad “Medicine of the Future 2024”, Central Asian University, Tashkent, October 26 to 27, 2024",
     "Sertifikat, “Medicine of the Future 2024” tibbiyot olimpiadasi, Central Asian University, Toshkent, 2024 yil 26–27 oktabr",
     "Сертификат, медицинская олимпиада «Medicine of the Future 2024», Central Asian University, Ташкент, 26–27 октября 2024 года"),
    ("Certificate for the Medicine of the Future 2024 olympiad at Central Asian University",
     "Central Asian Universitydagi Medicine of the Future 2024 olimpiadasi sertifikati",
     "Сертификат олимпиады Medicine of the Future 2024 в Central Asian University"),
    ("Diploma III, 3rd place, IV International Olympiad of Medical Students “Samarkand-2020”, December 15 to 16, 2023",
     "III darajali diplom, 3-oʻrin, tibbiyot talabalarining IV xalqaro olimpiadasi “Samarkand-2020”, 2023 yil 15–16 dekabr",
     "Диплом III степени, 3 место, IV Международная олимпиада студентов медицинских вузов «Samarkand-2020», 15–16 декабря 2023 года"),
    ("Third place diploma from the IV International Olympiad of Medical Students, Samarkand 2023",
     "Tibbiyot talabalarining IV xalqaro olimpiadasi 3-oʻrin diplomi, Samarqand 2023",
     "Диплом за третье место на IV Международной олимпиаде студентов медицинских вузов, Самарканд 2023"),
    (">Samarkand Olympiad, 3rd place<", ">Samarqand olimpiadasi, 3-oʻrin<", ">Олимпиада в Самарканде, 3 место<"),
    ("Gold Medal, AKFA MEDINNOVA Expo 2023, group project on Telegram bots and 3D printed pill boxes",
     "Oltin medal, AKFA MEDINNOVA Expo 2023, Telegram botlar va 3D printerda bosilgan dori qutilari boʻyicha guruh loyihasi",
     "Золотая медаль, AKFA MEDINNOVA Expo 2023, групповой проект о Telegram ботах и таблетницах, напечатанных на 3D принтере"),
    ("Gold medal project award certificate from AKFA Medinnova Expo 2023",
     "AKFA Medinnova Expo 2023 loyihalar tanlovi oltin medal sertifikati",
     "Сертификат золотой медали за проект, AKFA Medinnova Expo 2023"),
    (">AKFA Medinnova, gold medal<", ">AKFA Medinnova, oltin medal<", ">AKFA Medinnova, золотая медаль<"),
    ("Certificate, 12 hour international medical conference “Healthcare of the Future”, Central Asian University, Tashkent, October 25 to 26, 2024",
     "Sertifikat, “Healthcare of the Future” xalqaro tibbiy konferensiyasi (12 soat), Central Asian University, Toshkent, 2024 yil 25–26 oktabr",
     "Сертификат, международная медицинская конференция «Healthcare of the Future» (12 часов), Central Asian University, Ташкент, 25–26 октября 2024 года"),
    ("Certificate of participation in the Healthcare of the Future medical conference",
     "Healthcare of the Future tibbiy konferensiyasida ishtirok sertifikati",
     "Сертификат участника медицинской конференции Healthcare of the Future"),
    ("AHA Advanced Cardiovascular Life Support (ACLS) Provider, issued May 19, 2025, renew by May 2027",
     "AHA kengaytirilgan kardioreanimatsiya (ACLS) provayderi, 2025 yil 19 mayda berilgan, 2027 yil mayigacha amal qiladi",
     "Провайдер AHA по расширенной кардиореанимации (ACLS), выдан 19 мая 2025 года, действителен до мая 2027 года"),
    ("American Heart Association ACLS provider certificate", "American Heart Association ACLS provayderi sertifikati", "Сертификат провайдера ACLS, American Heart Association"),
    (">AHA ACLS provider<", ">AHA ACLS provayderi<", ">Провайдер AHA ACLS<"),
    ("AHA Basic Life Support (BLS) Provider, issued May 14, 2025, renew by May 2027",
     "AHA asosiy reanimatsiya (BLS) provayderi, 2025 yil 14 mayda berilgan, 2027 yil mayigacha amal qiladi",
     "Провайдер AHA по базовой реанимации (BLS), выдан 14 мая 2025 года, действителен до мая 2027 года"),
    ("American Heart Association BLS provider certificate", "American Heart Association BLS provayderi sertifikati", "Сертификат провайдера BLS, American Heart Association"),
    (">AHA BLS provider<", ">AHA BLS provayderi<", ">Провайдер AHA BLS<"),
    ("<li>Meta-analysis Academy graduate</li>", "<li>Meta-analysis Academy bitiruvchisi</li>", "<li>Выпускник Meta-analysis Academy</li>"),
    ("<li>Introduction to Machine Learning, SoloLearn</li>", "<li>Introduction to Machine Learning kursi, SoloLearn</li>", "<li>Курс Introduction to Machine Learning, SoloLearn</li>"),
    ("<li>UpToDate CME, AMA PRA Category 1 Credit, Oct 2025</li>", "<li>UpToDate CME, AMA PRA 1 toifa krediti, okt 2025</li>", "<li>UpToDate CME, кредит AMA PRA категории 1, окт 2025</li>"),
    ("<li>“Healthcare of the Future” conference (12 hours), CAU 2024</li>", "<li>“Healthcare of the Future” konferensiyasi (12 soat), CAU 2024</li>", "<li>Конференция «Healthcare of the Future» (12 часов), CAU 2024</li>"),
    ("<li>Regular attendance at Healio and Cleveland Clinic webinars</li>", "<li>Healio va Cleveland Clinic vebinarlarida muntazam ishtirok</li>", "<li>Регулярное участие в вебинарах Healio и Cleveland Clinic</li>"),

    # ---------- skills ----------
    ("Tools of the trade", "Koʻnikmalar", "Навыки"),
    ("What I use on the ward, in the library and at the keyboard.",
     "Boʻlimda, kutubxonada va kompyuter oldida foydalanadigan koʻnikmalarim.",
     "То, чем я пользуюсь в отделении, в библиотеке и за клавиатурой."),
    (">Clinical</h2>", ">Klinik</h2>", ">Клинические</h2>"),
    (">Research</h2>", ">Ilmiy</h2>", ">Исследовательские</h2>"),
    (">Technical</h2>", ">Texnik</h2>", ">Технические</h2>"),
    (">Patient interaction<", ">Bemorlar bilan muloqot<", ">Работа с пациентами<"),
    (">Clinical communication<", ">Klinik kommunikatsiya<", ">Клиническая коммуникация<"),
    (">Perioperative documentation<", ">Perioperatsion hujjatlashtirish<", ">Периоперационная документация<"),
    (">Literature review (PubMed, Google Scholar)<", ">Adabiyot sharhi (PubMed, Google Scholar)<", ">Обзор литературы (PubMed, Google Scholar)<"),
    (">Meta-analysis</li>", ">Meta tahlil</li>", ">Метаанализ</li>"),
    (">Journal club preparation<", ">Jurnal klubiga tayyorgarlik<", ">Подготовка журнальных клубов<"),
    (">Statistical software<", ">Statistik dasturlar<", ">Статистическое ПО<"),
    (">Canva design<", ">Canva dizayn<", ">Дизайн в Canva<"),

    # ---------- projects ----------
    ("<h1 class=\"heading-2 hero-title\">Things I've built</h1>",
     "<h1 class=\"heading-2 hero-title\">Yaratgan loyihalarim</h1>",
     "<h1 class=\"heading-2 hero-title\">Мои проекты</h1>"),
    ("Free tools for medical students, built alongside my clinical work. They run in the browser, with nothing to install.",
     "Klinik ishim bilan bir qatorda tibbiyot talabalari uchun yaratgan bepul vositalarim. Ular brauzerda ishlaydi, hech narsa oʻrnatish shart emas.",
     "Бесплатные инструменты для студентов медицинских вузов, которые я создаю параллельно с клинической работой. Они работают в браузере, ничего устанавливать не нужно."),
    ('"badge">Web app<', '"badge">Veb ilova<', '"badge">Браузерное приложение<'),
    (">Free to use<", ">Bepul<", ">Бесплатно<"),
    (">Interface in Uzbek<", ">Interfeys oʻzbek tilida<", ">Интерфейс на узбекском<"),
    ("An interactive 3D anatomy atlas for Uzbek-speaking medical students.",
     "Oʻzbek tilida oʻqiydigan tibbiyot talabalari uchun interaktiv 3D anatomiya atlasi.",
     "Интерактивный 3D атлас анатомии для студентов медицинских вузов, обучающихся на узбекском языке."),
    ("Rotate real scanned human anatomy, click any structure for its name and a short description, hide or isolate parts to see what lies beneath, then test yourself in quiz mode. It works on phones and computers.",
     "Haqiqiy skanerlangan inson anatomiyasini aylantiring, istalgan tuzilmani bosib uning nomi va qisqa tavsifini koʻring, ostidagi qismlarni koʻrish uchun tuzilmalarni yashiring yoki alohida ajrating, soʻng test rejimida oʻzingizni sinang. Telefon va kompyuterda ishlaydi.",
     "Вращайте реальную отсканированную анатомию человека, нажмите на любую структуру, чтобы увидеть её название и краткое описание, скрывайте или выделяйте части, чтобы рассмотреть то, что под ними, а затем проверьте себя в режиме теста. Работает на телефоне и компьютере."),
    ("<span>Open the app</span>", "<span>Ilovani ochish</span>", "<span>Открыть приложение</span>"),
    (">Or go straight to a body system<", ">Yoki kerakli tana tizimini darhol oching<", ">Или сразу откройте нужную систему<"),
    ('aria-label="Body systems"', 'aria-label="Tana tizimlari"', 'aria-label="Системы организма"'),
    (">Skeleton</a>", ">Skelet</a>", ">Скелет</a>"),
    (">Internal organs</a>", ">Ichki aʼzolar</a>", ">Внутренние органы</a>"),
    (">Heart</a>", ">Yurak</a>", ">Сердце</a>"),
    (">Brain</a>", ">Bosh miya</a>", ">Головной мозг</a>"),
    (">Lower limb</a>", ">Oyoq</a>", ">Нижняя конечность</a>"),
    (">Knee joint</a>", ">Tizza boʻgʻimi</a>", ">Коленный сустав</a>"),
    (">Digestive tract</a>", ">Hazm qilish tizimi</a>", ">Пищеварительный тракт</a>"),
    ("Built with React and Three.js on anatomical scans from BodyParts3D (DBCLS) and Z-Anatomy, shared under CC BY-SA licences.",
     "React va Three.js yordamida BodyParts3D (DBCLS) va Z-Anatomy anatomik skanerlari asosida yaratilgan; ular CC BY-SA litsenziyalari ostida tarqatiladi.",
     "Создано на React и Three.js на основе анатомических сканов BodyParts3D (DBCLS) и Z-Anatomy, которые распространяются по лицензиям CC BY-SA."),

    # ---------- contact ----------
    ("Open to research collaborations and clinical projects", "Ilmiy hamkorlik va klinik loyihalar uchun ochiqman", "Открыт к научному сотрудничеству и клиническим проектам"),
    ("I'm happy to talk about orthopedic research, trauma care and collaborative clinical projects.",
     "Ortopediya boʻyicha tadqiqotlar, travmatologik yordam va hamkorlikdagi klinik loyihalar haqida suhbatlashishdan mamnunman.",
     "Буду рад обсудить исследования в ортопедии, травматологическую помощь и совместные клинические проекты."),
    ("<span>Copy address</span>", "<span>Manzilni nusxalash</span>", "<span>Скопировать адрес</span>"),
    ('data-msg-ok="Email address copied." data-msg-error="Copy failed. Select the address above instead." data-msg-unavailable="Copy is not available in this browser. Select the address above instead."',
     'data-msg-ok="Email manzil nusxalandi." data-msg-error="Nusxalab boʻlmadi. Yuqoridagi manzilni qoʻlda belgilang." data-msg-unavailable="Bu brauzerda nusxalash imkoni yoʻq. Yuqoridagi manzilni qoʻlda belgilang."',
     'data-msg-ok="Адрес почты скопирован." data-msg-error="Не удалось скопировать. Выделите адрес выше вручную." data-msg-unavailable="В этом браузере копирование недоступно. Выделите адрес выше вручную."'),

]

MONTHS = {
    "uz": dict(Jan="yan", Feb="fev", Mar="mar", Apr="apr", May="may", Jun="iyun",
               Jul="iyul", Aug="avg", Sep="sen", Oct="okt", Nov="noy", Dec="dek"),
    "ru": dict(Jan="янв", Feb="фев", Mar="мар", Apr="апр", May="май", Jun="июн",
               Jul="июл", Aug="авг", Sep="сен", Oct="окт", Nov="ноя", Dec="дек"),
}
PRESENT = {"uz": "hozirgacha", "ru": "сейчас"}
MONTH_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?=( \d{4}\b| – ))")

# Text that is the same in every language (names, acronyms, titles)
SAME = re.compile(
    r"^(Asadbek Sultonov|Asadbek|Sultonov|English|I|III|AS|EN|UZ|RU|Python|NumPy|SciPy|Pandas|ePoster|AAHKS 2026|"
    r"Harvard Business Case Competition|AKFA MEDINNOVA Expo 2023|Central Asian University|"
    r"Medicine of the Future 2024|Healthcare of the Future|CAU Tech Summit '25|USMLE Step 1|"
    r"Biomedical Materials & Devices|“Oddiy Talaba”|3D Anatomiya Laboratoriyasi|asadbeksltnv90@gmail\.com|DOI .*|"
    r"[\d.,%<+ –—·()]+|.*\b(Studies|Study|Uzbekistan|Cases|Diabetes)$|"
    r"Asadbek Sultonov, Mukhammadbektosh.*)$"
)


def translate(src, page, lang):
    out = src
    used = set()
    for i, row in enumerate(T):
        en, tr = row[0], row[1 if lang == "uz" else 2]
        if en in out:
            out = out.replace(en, tr)
            used.add(i)

    # dates like "Sep 2022" or "Jun – Aug 2024", and "– present"
    out = MONTH_RE.sub(lambda m: MONTHS[lang][m.group(1)], out)
    out = out.replace("– present", "– " + PRESENT[lang])

    # page language, locale and canonical URL
    out = out.replace('<html lang="en">', '<html lang="%s">' % lang, 1)
    out = out.replace('content="en_US"', 'content="%s"' % LANGS[lang], 1)
    tail = "" if page == "index.html" else page
    for attr in ('<link rel="canonical" href="', '<meta property="og:url" content="'):
        out = out.replace(attr + BASE + tail + '"', attr + BASE + lang + "/" + tail + '"', 1)

    # structured data: page URLs in this language (ids with # stay shared)
    def localize_ld(m):
        block = re.sub(r'"%s((?:[a-z-]+\.html)?)"' % re.escape(BASE), lambda u: '"%s%s/%s"' % (BASE, lang, u.group(1)), m.group(0))
        return block.replace('"inLanguage": "en"', '"inLanguage": "%s"' % lang)
    out = re.sub(r'<script type="application/ld\+json">.*?</script>', localize_ld, out, flags=re.S)
    out = re.sub(r"<!-- Generated by tools/pages\.py[^\n]*-->\n", "", out, count=1)

    # assets live one folder up
    out = re.sub(r'((?:src|href|data-full|data-video)=")(?=(?:assets|css|js)/)', r"\1../", out)

    # language switch: point each link at this page in that language
    def switch(m):
        tag, target = m.group(0), m.group(1)
        if target == lang:
            href = "./" if page == "index.html" else page
        elif target == "en":
            href = "../" if page == "index.html" else "../" + page
        else:
            href = "../%s/%s" % (target, "" if page == "index.html" else page)
        tag = re.sub(r'href="[^"]*"', 'href="%s"' % href, tag)
        tag = tag.replace(' aria-current="true"', "")
        if target == lang:
            tag = tag[:-1] + ' aria-current="true">'
        return tag
    out = re.sub(r'<a href="[^"]*" data-lang="(\w+)"[^>]*>', switch, out)

    note = "<!-- Generated by tools/i18n.py from ../%s. Edit the English page, then run: python3 tools/i18n.py -->\n" % page
    out = out.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + note, 1)
    return out, used


def leftovers(text):
    """Visible text and labels that still read exactly like the English source."""
    body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<svg\b.*?</svg>|<table\b.*?</table>", "", text, flags=re.S)
    found = []
    for m in re.finditer(r">([^<>]+)<", body):
        found.append(m.group(1))
    for m in re.finditer(r'(?<![\w-])(?:alt|aria-label|data-caption|title)="([^"]+)"', text):
        found.append(m.group(1))
    for m in re.finditer(r'<meta (?:name|property)="(?:description|og:description|og:title|twitter:title|twitter:description|og:image:alt)" content="([^"]+)"', text):
        found.append(m.group(1))
    out = []
    for t in found:
        t = html.unescape(" ".join(t.split()))
        if not t or SAME.match(t):
            continue
        if re.search(r"[A-Za-z]{3,}", t) and not re.search(r"[а-яА-ЯʻʼёЁ]", t):
            out.append(t)
    return out


def main():
    used_all = set()
    warnings = []
    sources = {}
    for page in PAGES:
        with open(os.path.join(ROOT, page), encoding="utf-8") as f:
            sources[page] = f.read()
    for lang in LANGS:
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        for page in PAGES:
            out, used = translate(sources[page], page, lang)
            used_all |= used
            with open(os.path.join(ROOT, lang, page), "w", encoding="utf-8") as f:
                f.write(out)
            if lang == "ru":
                for t in leftovers(out):
                    warnings.append("%s: %s" % (page, t))

    missing = [T[i][0] for i in range(len(T)) if i not in used_all]
    if missing:
        print("ERROR: these English strings are no longer in the source pages.")
        print("Update their entries in tools/i18n.py:\n")
        for m in missing:
            print("  - " + m[:120])
        sys.exit(1)
    if warnings:
        print("Check these: they look untranslated (English text with no table entry):\n")
        for w in sorted(set(warnings)):
            print("  - " + w[:140])
    print("Built uz/ and ru/ for: " + ", ".join(PAGES))


if __name__ == "__main__":
    main()
