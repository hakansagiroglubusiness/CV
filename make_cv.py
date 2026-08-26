# -*- coding: utf-8 -*-
"""Generate clean, ATS-friendly CV PDFs (EN + TR) for Hakan Sağıroğlu."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, HRFlowable, KeepTogether, Table, TableStyle)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('DVS', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVS-B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVS-O', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DVS', normal='DVS', bold='DVS-B', italic='DVS-O', boldItalic='DVS-B')

INK = HexColor('#1C1917')
SOFT = HexColor('#44403C')
MUTE = HexColor('#78716C')
ACCENT = HexColor('#C85F3C')
LINE = HexColor('#D6D3D1')

def styles():
    s = {}
    s['name'] = ParagraphStyle('name', fontName='DVS-B', fontSize=21, leading=25, textColor=INK)
    s['title'] = ParagraphStyle('title', fontName='DVS-B', fontSize=10.5, leading=14, textColor=ACCENT)
    s['contact'] = ParagraphStyle('contact', fontName='DVS', fontSize=8.5, leading=13, textColor=MUTE)
    s['h2'] = ParagraphStyle('h2', fontName='DVS-B', fontSize=10, leading=13, textColor=INK, spaceBefore=0)
    s['role'] = ParagraphStyle('role', fontName='DVS-B', fontSize=10, leading=13.5, textColor=INK)
    s['meta'] = ParagraphStyle('meta', fontName='DVS', fontSize=8.5, leading=12, textColor=MUTE)
    s['body'] = ParagraphStyle('body', fontName='DVS', fontSize=9, leading=13.2, textColor=SOFT)
    s['bullet'] = ParagraphStyle('bullet', fontName='DVS', fontSize=9, leading=13.2, textColor=SOFT,
                                 leftIndent=9, bulletIndent=0, spaceAfter=1.5)
    s['chip'] = ParagraphStyle('chip', fontName='DVS', fontSize=9, leading=13.5, textColor=SOFT)
    return s

S = styles()

def section(story, label):
    story.append(Spacer(1, 6.5*mm))
    story.append(Paragraph(label.upper(), ParagraphStyle('sec', parent=S['h2'], textColor=ACCENT,
                                                          fontSize=9.5, leading=12)))
    story.append(HRFlowable(width='100%', thickness=0.7, color=LINE, spaceBefore=2, spaceAfter=4.5))

def job(story, j, clients_label):
    head = Table(
        [[Paragraph('<b>%s</b>' % j['role'], S['role']),
          Paragraph(j['dates'], ParagraphStyle('d', parent=S['meta'], alignment=2))]],
        colWidths=[125*mm, 45*mm])
    head.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                              ('LEFTPADDING', (0,0), (-1,-1), 0),
                              ('RIGHTPADDING', (0,0), (-1,-1), 0),
                              ('TOPPADDING', (0,0), (-1,-1), 0),
                              ('BOTTOMPADDING', (0,0), (-1,-1), 0)]))
    block = [head,
             Paragraph('<font color="#C85F3C"><b>%s</b></font> <font color="#78716C">· %s</font>'
                       % (j['company'], j['mode']), S['meta'])]
    if j.get('clients'):
        block.append(Paragraph('<i>%s %s</i>' % (clients_label, j['clients']),
                               ParagraphStyle('cl', parent=S['meta'], fontName='DVS-O')))
    block.append(Spacer(1, 1.5*mm))
    for p in j['points']:
        block.append(Paragraph(p, S['bullet'], bulletText='•'))
    block.append(Spacer(1, 3.5*mm))
    story.append(KeepTogether(block))

def project(story, pr):
    line = '<b>%s</b> <font size="8" color="#78716C">— %s</font>' % (pr['name'], pr['stack'])
    if pr.get('link'):
        line += '  <font size="8" color="#C85F3C">%s</font>' % pr['link']
    block = [Paragraph(line, S['role']),
             Paragraph(pr['desc'], S['body']),
             Spacer(1, 2.5*mm)]
    story.append(KeepTogether(block))

def build(path, L):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=18*mm, rightMargin=18*mm,
                          topMargin=16*mm, bottomMargin=14*mm,
                          title=L['doc_title'], author='Hakan Sağıroğlu',
                          subject=L['title_line'])
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
    doc.addPageTemplates([PageTemplate(id='p', frames=[frame])])

    story = []
    story.append(Paragraph('Hakan Sağıroğlu', S['name']))
    story.append(Spacer(1, 1.2*mm))
    story.append(Paragraph(L['title_line'], S['title']))
    story.append(Spacer(1, 1.8*mm))
    story.append(Paragraph(
        'sagirogluhakan@outlook.com &nbsp;·&nbsp; +90 555 016 53 35 &nbsp;·&nbsp; '
        'linkedin.com/in/hakansgroglu &nbsp;·&nbsp; %s' % L['loc'], S['contact']))

    section(story, L['sum_h'])
    story.append(Paragraph(L['summary'], S['body']))

    section(story, L['exp_h'])
    for j in L['jobs']:
        job(story, j, L['clients_label'])

    section(story, L['skills_h'])
    for g in L['groups']:
        story.append(Paragraph('<b>%s:</b>&nbsp; %s' % (g['name'], ' · '.join(g['items'])), S['chip']))
        story.append(Spacer(1, 1.2*mm))

    section(story, L['proj_h'])
    for pr in L['projects']:
        project(story, pr)

    section(story, L['edu_h'])
    for e in L['edu']:
        story.append(KeepTogether([
            Paragraph('<b>%s</b> — %s' % (e['school'], e['degree']), S['role']),
            Paragraph(e['meta'], S['meta']),
            Spacer(1, 2.2*mm)]))

    doc.build(story)
    print('wrote', path)

EN = dict(
    doc_title='Hakan Sağıroğlu — CV',
    title_line='SENIOR PAID GROWTH MARKETER — GOOGLE ADS · META · TIKTOK',
    loc='Bursa, Türkiye · Open to remote',
    sum_h='Summary', exp_h='Experience', skills_h='Skills', proj_h='Selected Projects',
    edu_h='Education', clients_label='Clients —',
    summary=('4+ years running paid media end-to-end for brands and agencies — $200K+ monthly budgets '
             'across six platforms, with AI and automation as infrastructure and ROAS as the only compass. '
             'Across agency and brand, I own the full operation for premium D2C brands: from performance '
             'analysis to category-level campaign architecture, plus the internal tools that run it.'),
    jobs=[
        dict(role='Sr. Paid Growth Marketer', company='PlanB.Media', mode='Remote, Istanbul',
             dates='Aug 2025 — Present', clients='Premium D2C jewelry brands', points=[
            'Managing $200K+ monthly multi-platform ad spend across Google Ads, Meta, TikTok, Criteo, and RTB House',
            'Primary agency contact for premium D2C jewelry brands — leading operations, reporting, and client management',
            'Driving cross-channel optimization end-to-end toward blended ROAS/MER, reconciling attribution across platforms and GA4',
            'ROAS-focused budget strategy and category-level campaign architecture',
            'Built the internal tooling the operation runs on (see Projects)']),
        dict(role='Founder', company='Tezgah Studios', mode='Hybrid, Bursa',
             dates='Jan 2024 — Aug 2025',
             clients='Gold Gallery, Kafkas Jewelry, Learn and Go Academy, Azkaldi.com, Casa Nostra Bursa, and more',
             points=[
            'End-to-end digital consultancy for SMBs across their digitalization journey',
            'Built and optimized performance campaigns on Meta and Google Ads',
            'Brand identity, positioning, and organic-growth content strategy',
            'Managed digital content production incl. photo, video, and creative assets']),
        dict(role='Digital Performance & Media Account Executive', company='Optdcom', mode='Hybrid, Istanbul',
             dates='Jan 2023 — Dec 2023', clients='Akbank — Axess, Wings, Juzdan', points=[
            'Cut CPA by 40%+ on TikTok without sacrificing acquisition volume',
            'High-volume customer acquisition campaigns for Axess and Wings credit cards',
            'CPA-targeted optimization for the Juzdan app, growing sign-ups and engagement',
            'Multi-network strategy via TikTok and Taboola within banking compliance']),
        dict(role='Performance Marketing Specialist', company='Decathlon Turkey', mode='Hybrid, Istanbul',
             dates='Jan 2022 — Jan 2023', points=[
            'Scaled annual Google Ads spend by 70%+ while lifting ROAS by ~20%',
            'Managed Google Ads end-to-end: Search, Shopping, and Display',
            'Continuous A/B testing for Quality Score, CTR, and conversion; bid strategy development',
            'Maximized ROAS via audience segmentation and remarketing optimization']),
        dict(role='Digital Marketing Intern', company='Decathlon Turkey', mode='Part-time',
             dates='Feb 2021 — Jan 2022', points=[
            'Prepared weekly and monthly campaign performance reports',
            'Tracked KPIs from Google Analytics and ad platform data',
            'Competitor and industry research delivering actionable insights']),
    ],
    groups=[
        dict(name='Paid Media', items=['Google Ads','Meta Ads','TikTok Ads','Pinterest Ads','X Ads','Criteo','RTB House','Yandex']),
        dict(name='AI & Automation', items=['AI Tools','MCP','Workflow Automation','Reporting Automation']),
        dict(name='Analytics & Data', items=['GA4','Dataslayer','Looker Studio','Python','Google Sheets','Data Analysis']),
        dict(name='Operations', items=['Account Management','Client Communication','Reporting','360° Strategy','English (Advanced)']),
    ],
    projects=[
        dict(name='PlanB SEO', stack='AI · Search Console · GA4',
             desc='AI-powered SEO analysis and reporting automation: crawls the site, surfaces keyword and content '
                  'opportunities, and turns Search Console and GA4 data into automated SEO performance reports.'),
        dict(name='Viby', stack='Chrome Extension · AI',
             desc='A Chrome extension that sees the browser screen in real time, answers in context, and can take '
                  'over browser control to act when needed.'),
        dict(name='PlanB Ads', stack='Google Ads · Meta · TikTok',
             desc='An ad management and automation panel that runs Google, Meta, and TikTok campaigns from a single '
                  'interface — monitoring, optimization actions, and automation in one place.'),
        dict(name='Çırak', stack='Next.js · TypeScript · PostgreSQL · DataSlayer MCP',
             desc='A Performance Marketing Operating System that turns "where should budget go?" into a hierarchical, '
                  'evidence-linked allocation plan on marginal returns. A deterministic engine computes; the LLM only '
                  'narrates — no hallucinated metrics.'),
        dict(name='Klyr Publish', stack='Next.js · Playwright · Sharp · FFmpeg · Meta API',
             desc='Generates brand-accurate static + video ad creatives in 4 formats from a product URL and publishes '
                  'them to Meta as PAUSED drafts — cutting creative prep + campaign setup from 1–2 days to ~5 minutes. '
                  'Zero paid AI-API dependency (fully local render).'),
        dict(name='AI Burger', stack='Next.js · TypeScript · Prisma · SQLite · Playwright',
             desc='AI-native food ordering pilot for a burger restaurant in Bursa: customers describe what they crave '
                  'and get a personalized burger built strictly from real kitchen inventory. A deterministic engine '
                  'proposes, validates and prices every recipe.'),
        dict(name='SkillB', stack='Next.js · Vercel', link='skillb-project.vercel.app',
             desc='A reusable AI skill-library platform for packaging and sharing skills.'),
    ],
    edu=[
        dict(school='Kadir Has University', degree='BA — New Media',
             meta='2018 — 2022 · GPA 3.00 · 100% English · 75% Scholarship'),
        dict(school='Vilnius Gediminas Technical University', degree='Business Management',
             meta='2016 — 2018 · 100% English · Vilnius, Lithuania'),
    ],
)

TR = dict(
    doc_title='Hakan Sağıroğlu — CV',
    title_line='SENIOR PAID GROWTH MARKETER — GOOGLE ADS · META · TIKTOK',
    loc='Bursa, Türkiye · Uzaktan çalışmaya açık',
    sum_h='Özet', exp_h='Deneyim', skills_h='Yetkinlikler', proj_h='Seçili Projeler',
    edu_h='Eğitim', clients_label='Müşteriler —',
    summary=('Ajans ve marka tarafında 4+ yıldır ücretli medyayı uçtan uca yönetiyorum — altı platformda aylık '
             '$200K+ bütçe, altyapıda AI ve otomasyon, pusulada yalnızca ROAS. Premium D2C markalar için performans '
             'analizinden kategori bazlı kampanya mimarisine kadar operasyonun tamamı bende — üstelik operasyonu '
             'çalıştıran iç araçları da ben geliştiriyorum.'),
    jobs=[
        dict(role='Sr. Paid Growth Marketer', company='PlanB.Media', mode='Uzaktan, İstanbul',
             dates='Ağu 2025 — Devam', clients='Premium D2C mücevher markaları', points=[
            'Google Ads, Meta, TikTok, Criteo ve RTB House üzerinde aylık $200K+ reklam bütçesi yönetimi',
            'Premium D2C mücevher markalarının birincil ajans iletişim noktası — operasyon, raporlama ve müşteri yönetimi',
            'Kanallar arası optimizasyonu uçtan uca blended ROAS/MER hedefine taşımak; platformlar ile GA4 arası atribüsyon mutabakatı',
            'ROAS odaklı bütçe stratejisi ve kategori bazlı kampanya mimarisi',
            'Operasyonu çalıştıran iç araçları geliştirdim (bkz. Projeler)']),
        dict(role='Founder', company='Tezgah Studios', mode='Hibrit, Bursa',
             dates='Oca 2024 — Ağu 2025',
             clients='Gold Gallery, Kafkas Jewelry, Learn and Go Academy, Azkaldi.com, Casa Nostra Bursa ve daha fazlası',
             points=[
            'KOBİ’lere dijitalleşmenin tüm aşamalarında uçtan uca danışmanlık',
            'Meta ve Google Ads üzerinde performans odaklı kampanya kurulumu ve optimizasyonu',
            'Marka kimliği, konumlandırma ve organik büyüme odaklı içerik stratejisi',
            'Foto, video ve kreatif dahil dijital içerik üretim süreçlerinin yönetimi']),
        dict(role='Digital Performance & Media Account Executive', company='Optdcom', mode='Hibrit, İstanbul',
             dates='Oca 2023 — Ara 2023', clients='Akbank — Axess, Wings, Juzdan', points=[
            'TikTok’ta hacimden ödün vermeden CPA’i %40+ düşürme',
            'Axess ve Wings için yüksek hacimli müşteri kazanımı kampanyaları',
            'Juzdan uygulaması için CPA hedefli optimizasyonla yeni kullanıcı artışı',
            'TikTok ve Taboola dahil, bankacılık regülasyonlarına uyumlu çok ağlı medya stratejisi']),
        dict(role='Performance Marketing Specialist', company='Decathlon Türkiye', mode='Hibrit, İstanbul',
             dates='Oca 2022 — Oca 2023', points=[
            'Yıllık Google Ads harcamasını %70+ ölçeklerken ROAS’ı ~%20 artırma',
            'Search, Shopping ve Display dahil Google Ads hesaplarının uçtan uca yönetimi',
            'Kalite puanı, TO ve dönüşüm için sürekli A/B testi; teklif stratejisi geliştirme',
            'Segmentasyon ve remarketing optimizasyonuyla ROAS maksimizasyonu']),
        dict(role='Digital Marketing Intern', company='Decathlon Türkiye', mode='Yarı Zamanlı',
             dates='Şub 2021 — Oca 2022', points=[
            'Haftalık/aylık kampanya performans raporlarının hazırlanması',
            'GA ve reklam platformu verileriyle temel metrik takibi',
            'Rakip ve sektör analizleriyle ekibe aksiyon alınabilir içgörü']),
    ],
    groups=[
        dict(name='Ücretli Medya', items=['Google Ads','Meta Ads','TikTok Ads','Pinterest Ads','X Ads','Criteo','RTB House','Yandex']),
        dict(name='AI & Otomasyon', items=['AI Araçları','MCP','İş Akışı Otomasyonu','Raporlama Otomasyonu']),
        dict(name='Analiz & Veri', items=['GA4','Dataslayer','Looker Studio','Python','Google Sheets','Veri Analizi']),
        dict(name='Operasyon', items=['Hesap Yönetimi','Müşteri İletişimi','Raporlama','360° Strateji','İngilizce (İleri)']),
    ],
    projects=[
        dict(name='PlanB SEO', stack='AI · Search Console · GA4',
             desc='AI destekli SEO analizi ve raporlama otomasyonu: siteyi tarar, anahtar kelime ve içerik '
                  'fırsatlarını çıkarır; Search Console ve GA4 verisini otomatik SEO performans raporlarına dönüştürür.'),
        dict(name='Viby', stack='Chrome Extension · AI',
             desc='Tarayıcı ekranını gerçek zamanlı gören, bağlam içinde yanıtlayan ve gerektiğinde tarayıcı '
                  'kontrolünü devralıp aksiyon alabilen bir Chrome eklentisi.'),
        dict(name='PlanB Ads', stack='Google Ads · Meta · TikTok',
             desc='Google, Meta ve TikTok kampanyalarını tek panelden yöneten ve optimize eden reklam yönetim ve '
                  'otomasyon paneli — izleme, optimizasyon aksiyonları ve otomasyon tek yerde.'),
        dict(name='Çırak', stack='Next.js · TypeScript · PostgreSQL · DataSlayer MCP',
             desc='"Bütçe nereye?" sorusunu marjinal getiri üzerinden hiyerarşik, kanıta bağlı bir tahsis planına '
                  'çeviren Performance Marketing İşletim Sistemi. Deterministik motor hesaplar, LLM yalnızca anlatır '
                  '— halüsinasyonlu metrik yok.'),
        dict(name='Klyr Publish', stack='Next.js · Playwright · Sharp · FFmpeg · Meta API',
             desc='Ürün URL’sinden 4 formatta marka-sadık statik + video reklam üretip Meta’ya PAUSED taslak olarak '
                  'yayınlar — kreatif hazırlık + kampanya kurulumunu 1–2 günden ~5 dakikaya indirir. Ücretli AI '
                  'API’sine sıfır bağımlılık (tamamen yerel render).'),
        dict(name='AI Burger', stack='Next.js · TypeScript · Prisma · SQLite · Playwright',
             desc='Bursa’daki bir burger restoranı için AI-native sipariş pilotu: müşteri canının ne çektiğini '
                  'anlatır, mutfağın gerçek envanterinden kişiselleştirilmiş bir burger kurulur. Deterministik motor '
                  'her tarifi önerir, doğrular ve fiyatlandırır.'),
        dict(name='SkillB', stack='Next.js · Vercel', link='skillb-project.vercel.app',
             desc='Yeniden kullanılabilir AI skill kütüphanesi — skill’leri paketleyip paylaşmak için platform.'),
    ],
    edu=[
        dict(school='Kadir Has Üniversitesi', degree='Lisans — Yeni Medya',
             meta='2018 — 2022 · GPA 3.00 · %100 İngilizce · %75 Burs'),
        dict(school='Vilnius Gediminas Technical University', degree='Business Management',
             meta='2016 — 2018 · %100 İngilizce · Vilnius, Litvanya'),
    ],
)

import sys, os
out = sys.argv[1] if len(sys.argv) > 1 else '.'
build(os.path.join(out, 'Hakan-Sagiroglu-CV-EN.pdf'), EN)
build(os.path.join(out, 'Hakan-Sagiroglu-CV-TR.pdf'), TR)
