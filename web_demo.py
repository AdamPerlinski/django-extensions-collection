#!/usr/bin/env python
"""
Web demo for Django Extensions Collection.
Run with: .venv/bin/python web_demo.py
Serves on http://localhost:3322
"""
import os
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return HttpResponse(HTML_PAGE, content_type='text/html')


@csrf_exempt
def api_validate(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    data = json.loads(request.body)
    validator_type = data.get('type')
    value = data.get('value', '')

    result = {'value': value, 'valid': False, 'detail': ''}

    if validator_type == 'phone':
        from django_extensions.phone_validator import is_valid_phone
        result['valid'] = is_valid_phone(value)
        result['detail'] = 'Valid phone number' if result['valid'] else 'Invalid phone number format'

    elif validator_type == 'credit_card':
        from django_extensions.credit_card_validator import is_valid_credit_card, get_card_type
        result['valid'] = is_valid_credit_card(value)
        if result['valid']:
            card_type = get_card_type(value)
            result['detail'] = f'{card_type}' if card_type else 'Valid card'
        else:
            result['detail'] = 'Invalid card number (Luhn check failed)'

    elif validator_type == 'color':
        from django_extensions.color_validator import is_valid_color, normalize_color
        result['valid'] = is_valid_color(value)
        if result['valid']:
            try:
                normalized = normalize_color(value)
                result['detail'] = f'Normalized: {normalized}'
                result['normalized'] = normalized
            except Exception:
                result['detail'] = 'Valid color'
        else:
            result['detail'] = 'Invalid color format'

    elif validator_type == 'url':
        from django_extensions.url_validator import is_valid_url
        result['valid'] = is_valid_url(value)
        result['detail'] = 'Valid URL' if result['valid'] else 'Invalid URL format'

    return JsonResponse(result)


@csrf_exempt
def api_template_tags(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    data = json.loads(request.body)
    operation = data.get('operation')
    value = data.get('value', '')

    result = {'input': value, 'output': '', 'operation': operation}

    try:
        if operation == 'intcomma':
            from django_extensions.humanize_tags.templatetags import intcomma
            result['output'] = str(intcomma(int(value)))
        elif operation == 'intword':
            from django_extensions.humanize_tags.templatetags import intword
            result['output'] = str(intword(int(value)))
        elif operation == 'ordinal':
            from django_extensions.humanize_tags.templatetags import ordinal
            result['output'] = str(ordinal(int(value)))
        elif operation == 'filesizeformat':
            from django_extensions.humanize_tags.templatetags import filesizeformat
            result['output'] = str(filesizeformat(int(value)))
        elif operation == 'duration':
            from django_extensions.humanize_tags.templatetags import duration
            result['output'] = str(duration(int(value)))
        elif operation == 'oxford_comma':
            from django_extensions.humanize_tags.templatetags import oxford_comma
            items = [x.strip() for x in value.split(',')]
            result['output'] = str(oxford_comma(items))
        elif operation == 'slugify':
            from django_extensions.string_tags.templatetags import slugify
            result['output'] = str(slugify(value))
        elif operation == 'title':
            from django_extensions.string_tags.templatetags import title
            result['output'] = str(title(value))
        elif operation == 'upper':
            from django_extensions.string_tags.templatetags import upper
            result['output'] = str(upper(value))
        elif operation == 'lower':
            from django_extensions.string_tags.templatetags import lower
            result['output'] = str(lower(value))
        elif operation == 'reverse_str':
            from django_extensions.string_tags.templatetags import reverse_str
            result['output'] = str(reverse_str(value))
        elif operation == 'remove_html':
            from django_extensions.string_tags.templatetags import remove_html
            result['output'] = str(remove_html(value))
        elif operation == 'truncate_chars':
            from django_extensions.string_tags.templatetags import truncate_chars
            result['output'] = str(truncate_chars(value, 20))
        elif operation == 'add':
            from django_extensions.math_tags.templatetags import add
            a, b = value.split(',')
            result['output'] = str(add(float(a.strip()), float(b.strip())))
        elif operation == 'multiply':
            from django_extensions.math_tags.templatetags import multiply
            a, b = value.split(',')
            result['output'] = str(multiply(float(a.strip()), float(b.strip())))
        elif operation == 'divide':
            from django_extensions.math_tags.templatetags import divide
            a, b = value.split(',')
            result['output'] = str(divide(float(a.strip()), float(b.strip())))
        elif operation == 'percentage':
            from django_extensions.math_tags.templatetags import percentage
            a, b = value.split(',')
            result['output'] = str(percentage(float(a.strip()), float(b.strip()))) + '%'
        elif operation == 'sqrt':
            from django_extensions.math_tags.templatetags import sqrt
            result['output'] = str(sqrt(float(value)))
        elif operation == 'power':
            from django_extensions.math_tags.templatetags import power
            a, b = value.split(',')
            result['output'] = str(power(float(a.strip()), float(b.strip())))
        else:
            result['output'] = 'Unknown operation'
    except Exception as e:
        result['output'] = f'Error: {e}'

    return JsonResponse(result)


@csrf_exempt
def api_generate_key(request):
    from django_extensions.generate_secret_key.management.commands.generate_secret_key import Command
    from io import StringIO
    cmd = Command()
    out = StringIO()
    cmd.stdout = out
    cmd.style = type('Style', (), {'SUCCESS': lambda self, x: x, 'WARNING': lambda self, x: x})()
    cmd.handle(length=50, no_special=False, count=1)
    key = out.getvalue().strip().split('\n')[0]
    return JsonResponse({'key': key})


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Django Extensions Collection — Docs &amp; Demo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0a0c;--surface:#111116;--surface2:#18181f;--surface3:#1e1e28;
  --border:#2a2a38;--border2:#3a3a4a;
  --text:#e8e8ef;--text2:#9898a8;--text3:#68687a;
  --accent:#c4f04d;--accent2:#a8d840;--accent-dim:rgba(196,240,77,0.08);
  --red:#ff4d6a;--green:#4dff91;--blue:#4da8ff;--orange:#ffa84d;--purple:#b84dff;
  --mono:'JetBrains Mono',monospace;--sans:'DM Sans',sans-serif;--serif:'Instrument Serif',serif;
}
html{font-size:15px;scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6;overflow-x:hidden}
::selection{background:var(--accent);color:var(--bg)}
body::after{content:'';position:fixed;inset:0;pointer-events:none;z-index:9999;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.03'/%3E%3C/svg%3E")}

.hero{padding:4rem 2rem 3rem;text-align:center;position:relative;background:linear-gradient(180deg,rgba(196,240,77,0.03) 0%,transparent 60%)}
.hero::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:600px;background:radial-gradient(circle,rgba(196,240,77,0.06) 0%,transparent 70%);pointer-events:none}
.hero-label{display:inline-block;font-family:var(--mono);font-size:.7rem;font-weight:500;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);border:1px solid var(--border);padding:.35rem 1rem;border-radius:100px;margin-bottom:1.5rem;background:var(--accent-dim)}
.hero h1{font-family:var(--serif);font-weight:400;font-size:clamp(2.4rem,5vw,4rem);line-height:1.15;color:var(--text);margin-bottom:.75rem;letter-spacing:-.02em}
.hero h1 em{font-style:italic;color:var(--accent)}
.hero p{color:var(--text2);font-size:1.05rem;max-width:560px;margin:0 auto 2rem}
.stats-bar{display:flex;justify-content:center;gap:2.5rem;flex-wrap:wrap;padding:1.5rem 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin:0 2rem}
.stat{text-align:center}
.stat-num{font-family:var(--mono);font-size:1.6rem;font-weight:700;color:var(--accent)}
.stat-label{font-size:.72rem;color:var(--text3);text-transform:uppercase;letter-spacing:.12em;margin-top:.15rem}

.nav{position:sticky;top:0;z-index:100;background:rgba(10,10,12,0.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:.6rem 2rem}
.nav-inner{display:flex;gap:.35rem;overflow-x:auto;max-width:1200px;margin:0 auto;padding:.2rem 0}
.nav-inner::-webkit-scrollbar{display:none}
.nav-btn{font-family:var(--mono);font-size:.65rem;padding:.35rem .7rem;border-radius:6px;border:1px solid transparent;background:transparent;color:var(--text3);cursor:pointer;white-space:nowrap;transition:all .15s;letter-spacing:.03em}
.nav-btn:hover{color:var(--text);border-color:var(--border)}
.nav-btn.active{background:var(--accent-dim);color:var(--accent);border-color:rgba(196,240,77,0.2)}

.container{max-width:1100px;margin:0 auto;padding:2rem}
section{margin-bottom:3.5rem;scroll-margin-top:4rem}
.section-header{display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem;padding-bottom:.75rem;border-bottom:1px solid var(--border)}
.section-tag{font-family:var(--mono);font-size:.6rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--bg);background:var(--accent);padding:.25rem .65rem;border-radius:4px}
.section-tag.ref{background:var(--blue)}
.section-tag.cloud{background:var(--purple)}
.section-title{font-family:var(--serif);font-size:1.6rem;font-weight:400;letter-spacing:-.01em}

.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.4rem;margin-bottom:1rem;transition:border-color .2s}
.card:hover{border-color:var(--border2)}
.card-label{font-family:var(--mono);font-size:.65rem;font-weight:500;color:var(--text3);text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem}
.grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}

.input-row{display:flex;gap:.5rem;margin-bottom:.75rem;align-items:stretch}
.input{flex:1;font-family:var(--mono);font-size:.85rem;padding:.6rem .8rem;background:var(--surface2);border:1px solid var(--border);border-radius:6px;color:var(--text);outline:none;transition:border-color .2s}
.input:focus{border-color:var(--accent)}
.input::placeholder{color:var(--text3)}
select.input{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%239898a8'%3E%3Cpath d='M2 4l4 4 4-4'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right .8rem center;padding-right:2rem}
.btn{font-family:var(--mono);font-size:.75rem;font-weight:600;padding:.6rem 1.2rem;border:none;border-radius:6px;cursor:pointer;transition:all .15s;white-space:nowrap;letter-spacing:.03em}
.btn-primary{background:var(--accent);color:var(--bg)}
.btn-primary:hover{background:var(--accent2);transform:translateY(-1px)}

.result{font-family:var(--mono);font-size:.82rem;padding:.7rem .9rem;border-radius:6px;background:var(--surface2);border:1px solid var(--border);min-height:2.2rem;display:flex;align-items:center;gap:.5rem;transition:all .3s;word-break:break-all}
.result.valid{border-color:rgba(77,255,145,0.3);background:rgba(77,255,145,0.04)}
.result.valid .result-icon{color:var(--green)}
.result.invalid{border-color:rgba(255,77,106,0.3);background:rgba(255,77,106,0.04)}
.result.invalid .result-icon{color:var(--red)}
.result-icon{font-size:1rem;flex-shrink:0}
.result-text{color:var(--text2)}
.result-detail{color:var(--text3);font-size:.72rem;margin-top:.1rem}
.result.waiting{color:var(--text3);font-style:italic}

.tag-demo{display:flex;align-items:center;gap:.5rem;padding:.5rem 0;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:.8rem}
.tag-demo:last-child{border:none}
.tag-op{color:var(--accent);min-width:140px;flex-shrink:0;font-weight:500}
.tag-arrow{color:var(--text3)}
.tag-result{color:var(--text)}

.color-preview{width:32px;height:32px;border-radius:6px;border:1px solid var(--border);flex-shrink:0;transition:all .3s}
.key-output{font-family:var(--mono);font-size:.78rem;padding:.8rem 1rem;background:var(--surface2);border:1px solid var(--border);border-radius:6px;color:var(--accent);word-break:break-all;line-height:1.6;min-height:2.5rem;transition:all .3s;user-select:all}

.model-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.2rem;transition:all .2s}
.model-card:hover{border-color:var(--accent);transform:translateY(-2px)}
.model-name{font-family:var(--mono);font-weight:600;font-size:.9rem;color:var(--accent);margin-bottom:.3rem}
.model-desc{font-size:.82rem;color:var(--text2);line-height:1.5}
.model-fields{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.6rem}
.model-field{font-family:var(--mono);font-size:.62rem;padding:.2rem .5rem;background:var(--surface3);border-radius:4px;color:var(--text3)}

pre.code{font-family:var(--mono);font-size:.75rem;padding:1rem;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text2);line-height:1.7;overflow-x:auto;white-space:pre;margin:.5rem 0}
.code-block{font-family:var(--mono);font-size:.78rem;padding:1rem;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text2);line-height:1.7;overflow-x:auto;white-space:pre}
.hl-kw{color:var(--purple)}.hl-fn{color:var(--blue)}.hl-str{color:var(--green)}.hl-cmt{color:var(--text3);font-style:italic}.hl-num{color:var(--orange)}

.doc-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.5rem;margin-bottom:1.25rem}
.doc-card h3{font-family:var(--mono);font-weight:600;font-size:1rem;color:var(--accent);margin-bottom:.25rem}
.doc-card .doc-desc{font-size:.88rem;color:var(--text2);margin-bottom:.75rem}
.doc-card .doc-install{font-family:var(--mono);font-size:.72rem;color:var(--text3);margin-bottom:.75rem;padding:.4rem .7rem;background:var(--surface2);border-radius:4px;display:inline-block}

.api-table{width:100%;font-size:.78rem;border-collapse:collapse;margin:.5rem 0}
.api-table th{font-family:var(--mono);font-weight:500;text-align:left;color:var(--text3);padding:.35rem .5rem;border-bottom:1px solid var(--border);font-size:.68rem;text-transform:uppercase;letter-spacing:.08em}
.api-table td{padding:.35rem .5rem;border-bottom:1px solid var(--border);color:var(--text2)}
.api-table td:first-child{font-family:var(--mono);color:var(--accent);font-size:.75rem;white-space:nowrap}

.ext-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.5rem}
.ext-chip{font-family:var(--mono);font-size:.68rem;padding:.45rem .7rem;background:var(--surface2);border:1px solid var(--border);border-radius:6px;color:var(--text2);transition:all .2s;cursor:pointer;display:flex;align-items:center;gap:.4rem}
.ext-chip:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.ext-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}

@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.fade-up{animation:fadeUp .5s ease both}
.stagger-1{animation-delay:.05s}.stagger-2{animation-delay:.1s}.stagger-3{animation-delay:.15s}

@media(max-width:640px){.container{padding:1.5rem 1rem}.stats-bar{gap:1.5rem;margin:0 1rem}.hero{padding:3rem 1rem 2rem}.input-row{flex-direction:column}.grid-2,.grid-3{grid-template-columns:1fr}}
</style>
</head>
<body>

<div class="hero fade-up">
  <span class="hero-label">v1.0.0 &middot; 51 Extensions &middot; MIT License</span>
  <h1>Django Extensions<br><em>Collection</em></h1>
  <p>Production-ready utilities for models, fields, validators, template tags, management commands, middleware, decorators, and cloud integrations. Full documentation and live demos.</p>
</div>

<div class="stats-bar fade-up stagger-1">
  <div class="stat"><div class="stat-num">51</div><div class="stat-label">Extensions</div></div>
  <div class="stat"><div class="stat-num">680</div><div class="stat-label">Tests Passing</div></div>
  <div class="stat"><div class="stat-num">14</div><div class="stat-label">Categories</div></div>
  <div class="stat"><div class="stat-num">8.9k</div><div class="stat-label">Lines of Tests</div></div>
</div>

<nav class="nav">
  <div class="nav-inner">
    <button class="nav-btn active" onclick="scrollTo_('validators')">Validators</button>
    <button class="nav-btn" onclick="scrollTo_('humanize')">Humanize</button>
    <button class="nav-btn" onclick="scrollTo_('strings')">Strings</button>
    <button class="nav-btn" onclick="scrollTo_('math')">Math</button>
    <button class="nav-btn" onclick="scrollTo_('models')">Models</button>
    <button class="nav-btn" onclick="scrollTo_('fields')">Fields</button>
    <button class="nav-btn" onclick="scrollTo_('managers')">Managers</button>
    <button class="nav-btn" onclick="scrollTo_('commands')">Commands</button>
    <button class="nav-btn" onclick="scrollTo_('middleware')">Middleware</button>
    <button class="nav-btn" onclick="scrollTo_('decorators')">Decorators</button>
    <button class="nav-btn" onclick="scrollTo_('utilities')">Utilities</button>
    <button class="nav-btn" onclick="scrollTo_('aws')">AWS</button>
    <button class="nav-btn" onclick="scrollTo_('services')">Services</button>
    <button class="nav-btn" onclick="scrollTo_('ai')">AI</button>
    <button class="nav-btn" onclick="scrollTo_('infra')">Infra</button>
    <button class="nav-btn" onclick="scrollTo_('extensions')">All 51</button>
  </div>
</nav>

<div class="container">

<!-- ========== VALIDATORS ========== -->
<section id="validators" class="fade-up stagger-2">
  <div class="section-header">
    <span class="section-tag">Live</span>
    <h2 class="section-title">Validators</h2>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-label">Phone Validator</div>
      <div class="input-row">
        <input class="input" id="phone-input" placeholder="+15551234567" value="+15551234567">
        <button class="btn btn-primary" onclick="validate('phone','phone-input','phone-result')">Validate</button>
      </div>
      <div class="result waiting" id="phone-result"><span class="result-text">Press validate to test</span></div>
    </div>
    <div class="card">
      <div class="card-label">Credit Card Validator</div>
      <div class="input-row">
        <input class="input" id="cc-input" placeholder="4111111111111111" value="4111111111111111">
        <button class="btn btn-primary" onclick="validate('credit_card','cc-input','cc-result')">Validate</button>
      </div>
      <div class="result waiting" id="cc-result"><span class="result-text">Press validate to test</span></div>
    </div>
    <div class="card">
      <div class="card-label">Color Validator</div>
      <div class="input-row">
        <div class="color-preview" id="color-swatch" style="background:#c4f04d"></div>
        <input class="input" id="color-input" placeholder="#FF5733" value="#c4f04d">
        <button class="btn btn-primary" onclick="validateColor()">Validate</button>
      </div>
      <div class="result waiting" id="color-result"><span class="result-text">Press validate to test</span></div>
    </div>
    <div class="card">
      <div class="card-label">URL Validator</div>
      <div class="input-row">
        <input class="input" id="url-input" placeholder="https://example.com" value="https://example.com">
        <button class="btn btn-primary" onclick="validate('url','url-input','url-result')">Validate</button>
      </div>
      <div class="result waiting" id="url-result"><span class="result-text">Press validate to test</span></div>
    </div>
  </div>

  <!-- Validator Docs -->
  <div class="doc-card" style="margin-top:1.25rem">
    <h3>PhoneNumberValidator</h3>
    <div class="doc-desc">Phone number validation with E.164, North American, and international format support.</div>
    <span class="doc-install">pip: built-in &middot; from django_extensions.phone_validator import PhoneNumberValidator, is_valid_phone</span>
    <pre class="code"><span class="hl-cmt"># Form / Model validation</span>
phone = forms.CharField(validators=[PhoneNumberValidator()])

<span class="hl-cmt"># Quick check</span>
is_valid_phone(<span class="hl-str">'+15551234567'</span>)  <span class="hl-cmt"># True</span>

<span class="hl-cmt"># Options</span>
PhoneNumberValidator(format=<span class="hl-str">'e164'</span>)
PhoneNumberValidator(region=<span class="hl-str">'US'</span>)
PhoneNumberValidator(require_country_code=<span class="hl-kw">True</span>)</pre>
    <table class="api-table">
      <tr><th>Format</th><th>Example</th><th>Valid</th></tr>
      <tr><td>E.164</td><td>+15551234567</td><td>Yes</td></tr>
      <tr><td>North American</td><td>555-123-4567</td><td>Yes</td></tr>
      <tr><td>Parentheses</td><td>(555) 123-4567</td><td>Yes</td></tr>
      <tr><td>International</td><td>+44 20 7946 0958</td><td>Yes</td></tr>
    </table>
  </div>

  <div class="doc-card">
    <h3>CreditCardValidator</h3>
    <div class="doc-desc">Luhn algorithm validation with card type detection (Visa, Mastercard, Amex, Discover, JCB, Diners).</div>
    <span class="doc-install">from django_extensions.credit_card_validator import CreditCardValidator, is_valid_card, get_card_type</span>
    <pre class="code">is_valid_card(<span class="hl-str">'4111111111111111'</span>)  <span class="hl-cmt"># True</span>
get_card_type(<span class="hl-str">'4111111111111111'</span>)  <span class="hl-cmt"># 'visa'</span>
get_card_type(<span class="hl-str">'5500000000000004'</span>)  <span class="hl-cmt"># 'mastercard'</span>
get_card_type(<span class="hl-str">'378282246310005'</span>)   <span class="hl-cmt"># 'amex'</span>

<span class="hl-cmt"># Only accept specific types</span>
CreditCardValidator(accepted_cards=[<span class="hl-str">'visa'</span>, <span class="hl-str">'mastercard'</span>])</pre>
  </div>

  <div class="grid-2">
    <div class="doc-card">
      <h3>ColorValidator</h3>
      <div class="doc-desc">CSS color validation and normalization (hex, RGB, RGBA, HSL, HSLA).</div>
      <pre class="code">is_valid_color(<span class="hl-str">'#FF5733'</span>)           <span class="hl-cmt"># True</span>
is_valid_color(<span class="hl-str">'rgb(255, 100, 50)'</span>) <span class="hl-cmt"># True</span>
normalize_color(<span class="hl-str">'#fff'</span>)             <span class="hl-cmt"># '#FFFFFF'</span>
hex_to_rgb(<span class="hl-str">'#FF5733'</span>)              <span class="hl-cmt"># (255, 87, 51)</span></pre>
    </div>
    <div class="doc-card">
      <h3>URLValidator</h3>
      <div class="doc-desc">Enhanced URL validation with localhost, IP, TLD, and scheme controls.</div>
      <pre class="code">is_valid_url(<span class="hl-str">'https://example.com'</span>) <span class="hl-cmt"># True</span>

URLValidator(allow_localhost=<span class="hl-kw">True</span>)
URLValidator(allow_ip=<span class="hl-kw">True</span>)
URLValidator(schemes=[<span class="hl-str">'http'</span>, <span class="hl-str">'https'</span>, <span class="hl-str">'ftp'</span>])
URLValidator(allowed_tlds=[<span class="hl-str">'com'</span>, <span class="hl-str">'org'</span>])</pre>
    </div>
  </div>
</section>

<!-- ========== HUMANIZE TAGS ========== -->
<section id="humanize" class="fade-up stagger-3">
  <div class="section-header">
    <span class="section-tag">Live</span>
    <h2 class="section-title">Humanize Tags</h2>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-label">Number Formatting</div>
      <div class="input-row">
        <input class="input" id="humanize-input" placeholder="1000000" value="2847593">
        <select class="input" id="humanize-op" style="max-width:160px">
          <option value="intcomma">intcomma</option>
          <option value="intword">intword</option>
          <option value="ordinal">ordinal</option>
          <option value="filesizeformat">filesizeformat</option>
          <option value="duration">duration</option>
        </select>
        <button class="btn btn-primary" onclick="runTag('humanize-input','humanize-op','humanize-result')">Run</button>
      </div>
      <div class="result waiting" id="humanize-result"><span class="result-text">Press run to transform</span></div>
    </div>
    <div class="card">
      <div class="card-label">Oxford Comma</div>
      <div class="input-row">
        <input class="input" id="oxford-input" placeholder="apples, oranges, bananas" value="Django, Flask, FastAPI">
        <button class="btn btn-primary" onclick="runTagDirect('oxford-input','oxford_comma','oxford-result')">Run</button>
      </div>
      <div class="result waiting" id="oxford-result"><span class="result-text">Press run to transform</span></div>
    </div>
  </div>
  <div class="card" style="margin-top:1rem">
    <div class="card-label">Quick Examples</div>
    <div class="tag-demo"><span class="tag-op">1000000|intcomma</span><span class="tag-arrow">&rarr;</span><span class="tag-result" id="ex-intcomma">...</span></div>
    <div class="tag-demo"><span class="tag-op">1500000|intword</span><span class="tag-arrow">&rarr;</span><span class="tag-result" id="ex-intword">...</span></div>
    <div class="tag-demo"><span class="tag-op">42|ordinal</span><span class="tag-arrow">&rarr;</span><span class="tag-result" id="ex-ordinal">...</span></div>
    <div class="tag-demo"><span class="tag-op">1073741824|filesize</span><span class="tag-arrow">&rarr;</span><span class="tag-result" id="ex-filesize">...</span></div>
    <div class="tag-demo"><span class="tag-op">3661|duration</span><span class="tag-arrow">&rarr;</span><span class="tag-result" id="ex-duration">...</span></div>
  </div>
  <div class="doc-card" style="margin-top:1rem">
    <h3>humanize_tags</h3>
    <div class="doc-desc">Make data human-readable: intcomma, intword, ordinal, filesizeformat, naturaltime, duration, oxford_comma, pluralize.</div>
    <span class="doc-install">{% load humanize_ext %} &middot; {{ value|intcomma }} &middot; {{ value|ordinal }}</span>
    <pre class="code">intcomma(<span class="hl-num">1000000</span>)    <span class="hl-cmt"># "1,000,000"</span>
intword(<span class="hl-num">1500000</span>)     <span class="hl-cmt"># "1.5 million"</span>
ordinal(<span class="hl-num">42</span>)           <span class="hl-cmt"># "42nd"</span>
filesizeformat(<span class="hl-num">1048576</span>) <span class="hl-cmt"># "1.0 MiB"</span>
duration(<span class="hl-num">3661</span>)        <span class="hl-cmt"># "1 hour, 1 minute, 1 second"</span>
naturaltime(dt)      <span class="hl-cmt"># "5 minutes ago"</span>
oxford_comma([<span class="hl-str">'a'</span>,<span class="hl-str">'b'</span>,<span class="hl-str">'c'</span>])  <span class="hl-cmt"># "a, b, and c"</span></pre>
  </div>
</section>

<!-- ========== STRING TAGS ========== -->
<section id="strings">
  <div class="section-header">
    <span class="section-tag">Live</span>
    <h2 class="section-title">String Tags</h2>
  </div>
  <div class="card">
    <div class="input-row">
      <input class="input" id="string-input" placeholder="Hello World! This Is A Test" value="Hello World! This Is A Test">
      <select class="input" id="string-op" style="max-width:170px">
        <option value="slugify">slugify</option><option value="title">title</option><option value="upper">upper</option>
        <option value="lower">lower</option><option value="reverse_str">reverse</option>
        <option value="truncate_chars">truncate(20)</option><option value="remove_html">remove_html</option>
      </select>
      <button class="btn btn-primary" onclick="runTag('string-input','string-op','string-result')">Run</button>
    </div>
    <div class="result waiting" id="string-result"><span class="result-text">Press run to transform</span></div>
  </div>
  <div class="doc-card" style="margin-top:1rem">
    <h3>string_tags</h3>
    <div class="doc-desc">String manipulation: slugify, title, upper, lower, capitalize, reverse_str, truncate_chars, truncate_words, strip, replace, split, join_str, remove_html, regex_replace, pad_left, pad_right, startswith, endswith, contains, repeat.</div>
    <span class="doc-install">{% load string_ext %} &middot; {{ text|slugify }} &middot; {{ text|truncate_chars:50 }}</span>
    <pre class="code">slugify(<span class="hl-str">"Hello World!"</span>)       <span class="hl-cmt"># "hello-world"</span>
remove_html(<span class="hl-str">"&lt;b&gt;Bold&lt;/b&gt;"</span>)    <span class="hl-cmt"># "Bold"</span>
truncate_chars(<span class="hl-str">"Long text..."</span>, <span class="hl-num">15</span>) <span class="hl-cmt"># "Long text..."</span>
replace(<span class="hl-str">"hello"</span>, <span class="hl-str">"l,r"</span>)       <span class="hl-cmt"># "herro"</span>
regex_replace(text, <span class="hl-str">"\\d+,NUM"</span>)  <span class="hl-cmt"># replaces digits</span></pre>
  </div>
</section>

<!-- ========== MATH TAGS ========== -->
<section id="math">
  <div class="section-header">
    <span class="section-tag">Live</span>
    <h2 class="section-title">Math Tags</h2>
  </div>
  <div class="card">
    <div class="card-label">Calculator</div>
    <div class="input-row">
      <input class="input" id="math-input" placeholder="10, 5" value="144">
      <select class="input" id="math-op" style="max-width:160px">
        <option value="sqrt">sqrt</option><option value="add">add (a, b)</option>
        <option value="multiply">multiply (a, b)</option><option value="divide">divide (a, b)</option>
        <option value="percentage">percentage (a, b)</option><option value="power">power (a, b)</option>
      </select>
      <button class="btn btn-primary" onclick="runTag('math-input','math-op','math-result')">Run</button>
    </div>
    <div class="result waiting" id="math-result"><span class="result-text">Press run to calculate</span></div>
  </div>
  <div class="doc-card" style="margin-top:1rem">
    <h3>math_tags</h3>
    <div class="doc-desc">Mathematical operations: add, subtract, multiply, divide, modulo, power, percentage, abs_value, round_num, floor, ceil, min_value, max_value, clamp, sqrt, calculate.</div>
    <span class="doc-install">{% load math_ext %} &middot; {{ value|add:10 }} &middot; {{ value|percentage:total }}</span>
    <pre class="code">{{ <span class="hl-num">5</span>|add:<span class="hl-num">3</span> }}          <span class="hl-cmt"># 8</span>
{{ <span class="hl-num">10</span>|multiply:<span class="hl-num">2</span> }}     <span class="hl-cmt"># 20</span>
{{ <span class="hl-num">25</span>|percentage:<span class="hl-num">100</span> }} <span class="hl-cmt"># 25.0</span>
{{ <span class="hl-num">15</span>|clamp:<span class="hl-str">"0,10"</span> }}   <span class="hl-cmt"># 10</span>
{{ <span class="hl-num">16</span>|sqrt }}            <span class="hl-cmt"># 4.0</span>
{% calculate <span class="hl-str">"2 + 3 * 4"</span> %} <span class="hl-cmt"># 14</span></pre>
  </div>
</section>

<!-- ========== URL TAGS ========== -->

<!-- ========== MODEL MIXINS ========== -->
<section id="models">
  <div class="section-header">
    <span class="section-tag ref">Docs</span>
    <h2 class="section-title">Model Mixins</h2>
  </div>
  <div class="grid-3">
    <div class="model-card"><div class="model-name">TimeStampedModel</div><div class="model-desc">Auto-managed created/modified timestamps</div><div class="model-fields"><span class="model-field">created</span><span class="model-field">modified</span></div></div>
    <div class="model-card"><div class="model-name">UUIDModel</div><div class="model-desc">UUID primary key with short ID helpers</div><div class="model-fields"><span class="model-field">id (uuid4)</span><span class="model-field">short_id</span><span class="model-field">hex_id</span></div></div>
    <div class="model-card"><div class="model-name">SoftDeleteModel</div><div class="model-desc">Soft delete with is_deleted flag and manager</div><div class="model-fields"><span class="model-field">is_deleted</span><span class="model-field">deleted_at</span><span class="model-field">restore()</span><span class="model-field">hard_delete()</span></div></div>
    <div class="model-card"><div class="model-name">OrderedModel</div><div class="model-desc">Explicit ordering with move operations</div><div class="model-fields"><span class="model-field">order</span><span class="model-field">move_up()</span><span class="model-field">move_down()</span><span class="model-field">swap()</span></div></div>
    <div class="model-card"><div class="model-name">StatusModel</div><div class="model-desc">Status field with state transitions</div><div class="model-fields"><span class="model-field">status</span><span class="model-field">status_changed_at</span><span class="model-field">is_&lt;status&gt;</span><span class="model-field">set_status()</span></div></div>
    <div class="model-card"><div class="model-name">SluggedModel</div><div class="model-desc">Auto-generated unique slugs from source field</div><div class="model-fields"><span class="model-field">slug</span><span class="model-field">slug_source_field</span></div></div>
    <div class="model-card"><div class="model-name">ActivatorModel</div><div class="model-desc">Time-based activation windows</div><div class="model-fields"><span class="model-field">activate_date</span><span class="model-field">deactivate_date</span><span class="model-field">is_active</span></div></div>
    <div class="model-card"><div class="model-name">TitleSlugModel</div><div class="model-desc">Title + auto-slug + description combo</div><div class="model-fields"><span class="model-field">title</span><span class="model-field">slug</span><span class="model-field">description</span></div></div>
  </div>

  <div class="doc-card" style="margin-top:1.25rem">
    <h3>Usage &amp; Composition</h3>
    <pre class="code"><span class="hl-kw">from</span> django_extensions.timestamped_model <span class="hl-kw">import</span> <span class="hl-fn">TimeStampedModel</span>
<span class="hl-kw">from</span> django_extensions.uuid_model <span class="hl-kw">import</span> <span class="hl-fn">UUIDModel</span>
<span class="hl-kw">from</span> django_extensions.soft_delete_model <span class="hl-kw">import</span> <span class="hl-fn">SoftDeleteModel</span>

<span class="hl-kw">class</span> <span class="hl-fn">Article</span>(TimeStampedModel, UUIDModel, SoftDeleteModel):
    title = models.CharField(max_length=<span class="hl-num">200</span>)
    body = models.TextField()

article = Article.objects.create(title=<span class="hl-str">"Hello"</span>, body=<span class="hl-str">"World"</span>)
article.id         <span class="hl-cmt"># 550e8400-e29b-41d4-...</span>
article.short_id   <span class="hl-cmt"># "550e8400"</span>
article.created    <span class="hl-cmt"># auto-set on create</span>
article.modified   <span class="hl-cmt"># auto-updated on save</span>

article.delete()   <span class="hl-cmt"># soft delete (is_deleted=True)</span>
Article.objects.count()      <span class="hl-cmt"># 0 (excludes deleted)</span>
Article.all_objects.count()  <span class="hl-cmt"># 1</span>
article.restore()  <span class="hl-cmt"># undo soft delete</span></pre>
  </div>

  <div class="grid-2">
    <div class="doc-card">
      <h3>StatusModel Example</h3>
      <pre class="code"><span class="hl-kw">class</span> <span class="hl-fn">Order</span>(StatusModel):
    STATUS_CHOICES = [
        (<span class="hl-str">'pending'</span>, <span class="hl-str">'Pending'</span>),
        (<span class="hl-str">'processing'</span>, <span class="hl-str">'Processing'</span>),
        (<span class="hl-str">'shipped'</span>, <span class="hl-str">'Shipped'</span>),
    ]
    customer = models.CharField(max_length=<span class="hl-num">200</span>)

order.is_pending     <span class="hl-cmt"># True</span>
order.set_status(<span class="hl-str">'processing'</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>ActivatorModel Example</h3>
      <pre class="code"><span class="hl-kw">class</span> <span class="hl-fn">Promotion</span>(ActivatorModel):
    name = models.CharField(max_length=<span class="hl-num">200</span>)
    discount = models.IntegerField()

promo = Promotion.objects.create(
    name=<span class="hl-str">"Sale"</span>, discount=<span class="hl-num">20</span>,
    activate_date=timezone.now(),
    deactivate_date=timezone.now() + timedelta(days=<span class="hl-num">30</span>)
)
Promotion.objects.active()   <span class="hl-cmt"># currently active</span>
Promotion.objects.expired()  <span class="hl-cmt"># past window</span></pre>
    </div>
  </div>
</section>

<!-- ========== CUSTOM FIELDS ========== -->
<section id="fields">
  <div class="section-header">
    <span class="section-tag ref">Docs</span>
    <h2 class="section-title">Custom Fields</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>AutoCreatedField / AutoModifiedField</h3>
      <div class="doc-desc">DateTimeFields that auto-set on create/save. More control than auto_now_add/auto_now.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.auto_created_field <span class="hl-kw">import</span> AutoCreatedField
<span class="hl-kw">from</span> django_extensions.auto_modified_field <span class="hl-kw">import</span> AutoModifiedField

<span class="hl-kw">class</span> <span class="hl-fn">Article</span>(models.Model):
    created = AutoCreatedField()
    modified = AutoModifiedField()</pre>
    </div>
    <div class="doc-card">
      <h3>ShortUUIDField</h3>
      <div class="doc-desc">Shorter UUID representation for URL-friendly IDs.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.short_uuid_field <span class="hl-kw">import</span> ShortUUIDField

<span class="hl-kw">class</span> <span class="hl-fn">Item</span>(models.Model):
    uid = ShortUUIDField()  <span class="hl-cmt"># "dGhpcyBpc"</span></pre>
    </div>
    <div class="doc-card">
      <h3>EncryptedField</h3>
      <div class="doc-desc">Fernet-encrypted fields for sensitive data. Requires <code>cryptography</code> package.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.encrypted_field <span class="hl-kw">import</span> EncryptedField

<span class="hl-kw">class</span> <span class="hl-fn">User</span>(models.Model):
    ssn = EncryptedField(max_length=<span class="hl-num">11</span>)
    notes = EncryptedTextField()
<span class="hl-cmt"># Data encrypted at rest, decrypted on read
# Also: EncryptedEmailField, EncryptedIntegerField,
#        EncryptedJSONField</span></pre>
    </div>
    <div class="doc-card">
      <h3>JSONSchemaField</h3>
      <div class="doc-desc">JSONField with schema validation. Requires <code>jsonschema</code> package.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.json_schema_field <span class="hl-kw">import</span> JSONSchemaField

<span class="hl-kw">class</span> <span class="hl-fn">Config</span>(models.Model):
    data = JSONSchemaField(schema={
        <span class="hl-str">'type'</span>: <span class="hl-str">'object'</span>,
        <span class="hl-str">'properties'</span>: {
            <span class="hl-str">'name'</span>: {<span class="hl-str">'type'</span>: <span class="hl-str">'string'</span>},
            <span class="hl-str">'count'</span>: {<span class="hl-str">'type'</span>: <span class="hl-str">'integer'</span>}
        }
    })</pre>
    </div>
    <div class="doc-card">
      <h3>MoneyField</h3>
      <div class="doc-desc">Currency-aware Decimal storage. Creates two columns: amount + currency code (ISO 4217).</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.money_field <span class="hl-kw">import</span> MoneyField

<span class="hl-kw">class</span> <span class="hl-fn">Product</span>(models.Model):
    price = MoneyField(max_digits=<span class="hl-num">10</span>, decimal_places=<span class="hl-num">2</span>,
                       default_currency=<span class="hl-str">'USD'</span>)

product.price            <span class="hl-cmt"># Decimal('19.99')</span>
product.price_currency   <span class="hl-cmt"># 'USD'</span>
format_money(product.price, <span class="hl-str">'USD'</span>)  <span class="hl-cmt"># "$19.99"</span></pre>
    </div>
    <div class="doc-card">
      <h3>PhoneField</h3>
      <div class="doc-desc">Phone number field with built-in validation and formatting.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.phone_field <span class="hl-kw">import</span> PhoneField

<span class="hl-kw">class</span> <span class="hl-fn">Contact</span>(models.Model):
    phone = PhoneField()  <span class="hl-cmt"># auto-validates, stores E.164</span></pre>
    </div>
  </div>
</section>

<!-- ========== MANAGERS ========== -->
<section id="managers">
  <div class="section-header">
    <span class="section-tag ref">Docs</span>
    <h2 class="section-title">Managers</h2>
  </div>
  <div class="grid-3">
    <div class="doc-card">
      <h3>SoftDeleteManager</h3>
      <div class="doc-desc">Filters out soft-deleted records by default.</div>
      <pre class="code">objects = SoftDeleteManager()
<span class="hl-cmt"># .all() excludes deleted
# .deleted() only deleted
# .with_deleted() everything</span></pre>
    </div>
    <div class="doc-card">
      <h3>ActiveManager</h3>
      <div class="doc-desc">Filters to only active records (status-based).</div>
      <pre class="code">objects = ActiveManager()
<span class="hl-cmt"># .active() currently active
# .inactive() not active</span></pre>
    </div>
    <div class="doc-card">
      <h3>RandomManager</h3>
      <div class="doc-desc">Adds random ordering and selection.</div>
      <pre class="code">objects = RandomManager()
<span class="hl-cmt"># .random() random queryset
# .random_item() single random</span></pre>
    </div>
  </div>
</section>

<!-- ========== MANAGEMENT COMMANDS ========== -->
<section id="commands">
  <div class="section-header">
    <span class="section-tag">Live</span>
    <h2 class="section-title">Management Commands</h2>
  </div>
  <div class="card">
    <div class="card-label">generate_secret_key</div>
    <p style="font-size:.85rem;color:var(--text2);margin-bottom:.75rem">Generate a cryptographically secure Django secret key.</p>
    <button class="btn btn-primary" onclick="generateKey()" style="margin-bottom:.75rem">Generate New Key</button>
    <div class="key-output" id="key-output">Click the button to generate...</div>
  </div>
  <div class="grid-2" style="margin-top:1rem">
    <div class="doc-card">
      <h3>shell_plus</h3>
      <div class="doc-desc">Enhanced Django shell that auto-imports all models, settings, and common utilities.</div>
      <pre class="code">$ ./manage.py shell_plus

<span class="hl-cmt"># Auto-imports all models, settings, etc.</span>
>>> Article.objects.filter(status=<span class="hl-str">'published'</span>)
>>> User.objects.count()</pre>
    </div>
    <div class="doc-card">
      <h3>show_urls</h3>
      <div class="doc-desc">Display all URL patterns with names and view functions.</div>
      <pre class="code">$ ./manage.py show_urls

/            home         views.index
/about/      about        views.about
/users/&lt;pk&gt;/ user-detail  views.user_detail</pre>
    </div>
    <div class="doc-card">
      <h3>clean_pyc</h3>
      <div class="doc-desc">Recursively remove .pyc files and __pycache__ directories.</div>
      <pre class="code">$ ./manage.py clean_pyc --dry-run
$ ./manage.py clean_pyc</pre>
    </div>
    <div class="doc-card">
      <h3>reset_db</h3>
      <div class="doc-desc">Reset database to empty state with safety confirmation prompt.</div>
      <pre class="code">$ ./manage.py reset_db
<span class="hl-str">Are you sure? This will destroy all data. [y/N]</span></pre>
    </div>
  </div>
</section>

<!-- ========== MIDDLEWARE ========== -->
<section id="middleware">
  <div class="section-header">
    <span class="section-tag ref">Docs</span>
    <h2 class="section-title">Middleware</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>TimezoneMiddleware</h3>
      <div class="doc-desc">Activate per-user timezone from user profile, session, or cookie. Priority: user field &gt; session &gt; cookie &gt; default.</div>
      <pre class="code"><span class="hl-cmt"># settings.py</span>
MIDDLEWARE = [
    ...
    <span class="hl-str">'django_extensions.timezone_middleware.TimezoneMiddleware'</span>,
]

<span class="hl-cmt"># User model</span>
<span class="hl-kw">class</span> <span class="hl-fn">User</span>(AbstractUser):
    timezone = models.CharField(max_length=<span class="hl-num">50</span>, default=<span class="hl-str">'UTC'</span>)

<span class="hl-cmt"># Or via session</span>
request.session[<span class="hl-str">'django_timezone'</span>] = <span class="hl-str">'US/Eastern'</span></pre>
    </div>
    <div class="doc-card">
      <h3>RequestLoggingMiddleware</h3>
      <div class="doc-desc">Log HTTP requests and responses with method, path, status, duration, and size. Auto-redacts sensitive data.</div>
      <pre class="code"><span class="hl-cmt"># Output:</span>
<span class="hl-str">[2024-01-15 10:30:00] GET /api/users/ 200 0.045s 1.2KB</span>

<span class="hl-cmt"># settings.py</span>
REQUEST_LOGGING = {
    <span class="hl-str">'SLOW_REQUEST_THRESHOLD'</span>: <span class="hl-num">1.0</span>,
    <span class="hl-str">'EXCLUDE_PATHS'</span>: [<span class="hl-str">'/health/'</span>, <span class="hl-str">'/static/'</span>],
    <span class="hl-str">'SENSITIVE_FIELDS'</span>: [<span class="hl-str">'password'</span>, <span class="hl-str">'token'</span>],
    <span class="hl-str">'LOG_REQUEST_BODY'</span>: <span class="hl-kw">False</span>,
}</pre>
    </div>
  </div>
</section>

<!-- ========== DECORATORS ========== -->
<section id="decorators">
  <div class="section-header">
    <span class="section-tag ref">Docs</span>
    <h2 class="section-title">Decorators</h2>
  </div>
  <div class="grid-3">
    <div class="doc-card">
      <h3>@ajax_required</h3>
      <div class="doc-desc">Restrict views to AJAX requests. Returns 400 for non-AJAX. Checks X-Requested-With and Accept headers.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.ajax_required \
    <span class="hl-kw">import</span> ajax_required

<span class="hl-fn">@ajax_required</span>
<span class="hl-kw">def</span> <span class="hl-fn">api</span>(request):
    <span class="hl-kw">return</span> JsonResponse({<span class="hl-str">'ok'</span>: <span class="hl-kw">True</span>})

<span class="hl-cmt"># Options:</span>
<span class="hl-fn">@ajax_required</span>(debug_bypass=<span class="hl-kw">True</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>@anonymous_required</h3>
      <div class="doc-desc">Restrict to unauthenticated users. Redirects logged-in users to LOGIN_REDIRECT_URL.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.anonymous_required \
    <span class="hl-kw">import</span> anonymous_required

<span class="hl-fn">@anonymous_required</span>
<span class="hl-kw">def</span> <span class="hl-fn">login_view</span>(request):
    <span class="hl-kw">return</span> render(request, <span class="hl-str">'login.html'</span>)

<span class="hl-cmt"># Custom redirect:</span>
<span class="hl-fn">@anonymous_required</span>(redirect_url=<span class="hl-str">'/dash/'</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>@superuser_required</h3>
      <div class="doc-desc">Restrict to superusers. Non-superusers get 403 or redirect to login.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.superuser_required \
    <span class="hl-kw">import</span> superuser_required

<span class="hl-fn">@superuser_required</span>
<span class="hl-kw">def</span> <span class="hl-fn">admin_panel</span>(request):
    <span class="hl-kw">return</span> render(request, <span class="hl-str">'admin.html'</span>)

<span class="hl-cmt"># Raise instead of redirect:</span>
<span class="hl-fn">@superuser_required</span>(raise_exception=<span class="hl-kw">True</span>)</pre>
    </div>
  </div>
</section>

<!-- ========== UTILITIES ========== -->
<section id="utilities">
  <div class="section-header">
    <span class="section-tag ref">Docs</span>
    <h2 class="section-title">Utilities</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>cache_decorator</h3>
      <div class="doc-desc">Cache function results with Django's cache backend. Supports TTL, key prefixes, custom key functions, conditional caching, and invalidation.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.cache_decorator <span class="hl-kw">import</span> cache_result

<span class="hl-fn">@cache_result</span>(timeout=<span class="hl-num">3600</span>, key_prefix=<span class="hl-str">'myapp'</span>)
<span class="hl-kw">def</span> <span class="hl-fn">expensive</span>(x, y):
    <span class="hl-kw">return</span> x ** y

<span class="hl-cmt"># Invalidate</span>
invalidate_cache(expensive, <span class="hl-num">2</span>, <span class="hl-num">10</span>)

<span class="hl-cmt"># Conditional: only cache non-None</span>
<span class="hl-fn">@cache_result</span>(condition=<span class="hl-kw">lambda</span> r: r <span class="hl-kw">is not None</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>pagination_utils</h3>
      <div class="doc-desc">Enhanced paginator with page range helper and convenience function.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.pagination_utils <span class="hl-kw">import</span> paginate, get_page_range

<span class="hl-cmt"># In a view</span>
page = paginate(Article.objects.all(),
                request.GET.get(<span class="hl-str">'page'</span>, <span class="hl-num">1</span>), per_page=<span class="hl-num">20</span>)

page.object_list    <span class="hl-cmt"># items on page</span>
page.has_next()     <span class="hl-cmt"># True/False</span>
get_page_range(page, window=<span class="hl-num">2</span>)  <span class="hl-cmt"># [3,4,5,6,7]</span></pre>
    </div>
    <div class="doc-card">
      <h3>email_utils &mdash; EmailBuilder</h3>
      <div class="doc-desc">Fluent builder for complex emails with HTML, attachments, CC/BCC, custom headers, and preview.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.email_utils <span class="hl-kw">import</span> EmailBuilder

(EmailBuilder()
    .subject(<span class="hl-str">'Welcome!'</span>)
    .to(<span class="hl-str">'user@example.com'</span>)
    .cc(<span class="hl-str">'manager@example.com'</span>)
    .from_email(<span class="hl-str">'noreply@example.com'</span>)
    .html(<span class="hl-str">'&lt;h1&gt;Welcome!&lt;/h1&gt;'</span>)
    .text(<span class="hl-str">'Welcome!'</span>)
    .attach(<span class="hl-str">'report.pdf'</span>, pdf_bytes, <span class="hl-str">'application/pdf'</span>)
    .header(<span class="hl-str">'X-Priority'</span>, <span class="hl-str">'1'</span>)
    .send())</pre>
    </div>
    <div class="doc-card">
      <h3>email_utils &mdash; Template &amp; HTML</h3>
      <div class="doc-desc">Quick helpers for template-based and HTML emails.</div>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.email_utils <span class="hl-kw">import</span> send_html_email, send_template_email

send_html_email(
    subject=<span class="hl-str">'Welcome!'</span>,
    html_content=<span class="hl-str">'&lt;h1&gt;Hello&lt;/h1&gt;'</span>,
    to=[<span class="hl-str">'user@example.com'</span>]
)

send_template_email(
    subject=<span class="hl-str">'Order Confirmation'</span>,
    template_name=<span class="hl-str">'emails/order.html'</span>,
    context={<span class="hl-str">'order'</span>: order},
    to=[user.email]
)</pre>
    </div>
  </div>
</section>

<!-- ========== AWS ========== -->
<section id="aws">
  <div class="section-header">
    <span class="section-tag cloud">Cloud</span>
    <h2 class="section-title">AWS Integrations</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>aws_s3_storage</h3>
      <div class="doc-desc">S3 file storage backend. Use as DEFAULT_FILE_STORAGE or direct upload/download. Supports presigned URLs.</div>
      <span class="doc-install">pip install boto3</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.aws_s3_storage <span class="hl-kw">import</span> S3Storage, s3_upload

<span class="hl-cmt"># As default storage</span>
DEFAULT_FILE_STORAGE = <span class="hl-str">'django_extensions.aws_s3_storage.S3Storage'</span>

<span class="hl-cmt"># Direct upload</span>
url = s3_upload(file_obj, <span class="hl-str">'uploads/image.png'</span>)

<span class="hl-cmt"># Presigned URL</span>
url = generate_presigned_url(<span class="hl-str">'private/doc.pdf'</span>, expiration=<span class="hl-num">3600</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>aws_ses_email</h3>
      <div class="doc-desc">SES email backend. Drop-in replacement for Django's email, plus bulk email and template support.</div>
      <span class="doc-install">pip install boto3</span>
      <pre class="code">EMAIL_BACKEND = <span class="hl-str">'django_extensions.aws_ses_email.SESEmailBackend'</span>

<span class="hl-cmt"># Direct SES</span>
send_ses_email(
    subject=<span class="hl-str">'Hello'</span>,
    body=<span class="hl-str">'Welcome!'</span>,
    html_body=<span class="hl-str">'&lt;h1&gt;Welcome!&lt;/h1&gt;'</span>,
    to=[<span class="hl-str">'user@example.com'</span>]
)

<span class="hl-cmt"># Bulk with templates</span>
send_bulk_email(template=<span class="hl-str">'welcome'</span>, destinations=[...])</pre>
    </div>
    <div class="doc-card">
      <h3>aws_sns_notifications</h3>
      <div class="doc-desc">SNS for pub/sub topics, SMS, and push notifications.</div>
      <span class="doc-install">pip install boto3</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.aws_sns_notifications <span class="hl-kw">import</span> publish_message, publish_sms

publish_message(<span class="hl-str">'Order confirmed'</span>, subject=<span class="hl-str">'Order #123'</span>)
publish_sms(<span class="hl-str">'+15551234567'</span>, <span class="hl-str">'Your code is 123456'</span>)

notifier = SNSNotifier(topic_arn=<span class="hl-str">'arn:aws:sns:...'</span>)
notifier.publish_json({<span class="hl-str">'event'</span>: <span class="hl-str">'user_created'</span>})</pre>
    </div>
    <div class="doc-card">
      <h3>aws_sqs_queue</h3>
      <div class="doc-desc">SQS message queue with send, receive, batch operations, and dead letter queue support.</div>
      <span class="doc-install">pip install boto3</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.aws_sqs_queue <span class="hl-kw">import</span> SQSQueue

queue = SQSQueue(<span class="hl-str">'my-queue'</span>)
queue.send({<span class="hl-str">'event'</span>: <span class="hl-str">'user_created'</span>, <span class="hl-str">'id'</span>: <span class="hl-num">123</span>})

<span class="hl-kw">for</span> msg <span class="hl-kw">in</span> queue.receive(max_messages=<span class="hl-num">10</span>):
    process(msg.body)
    msg.delete()</pre>
    </div>
  </div>
</section>

<!-- ========== SERVICES ========== -->
<section id="services">
  <div class="section-header">
    <span class="section-tag cloud">Cloud</span>
    <h2 class="section-title">Payments &amp; Messaging</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>stripe_payments</h3>
      <div class="doc-desc">Stripe integration: payment intents, customers, subscriptions, checkout sessions, webhooks, and refunds.</div>
      <span class="doc-install">pip install stripe</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.stripe_payments <span class="hl-kw">import</span> (
    create_payment_intent, create_customer,
    create_subscription, verify_webhook
)

intent = create_payment_intent(
    amount=<span class="hl-num">2000</span>,  <span class="hl-cmt"># $20.00 in cents</span>
    currency=<span class="hl-str">'usd'</span>,
    metadata={<span class="hl-str">'order_id'</span>: <span class="hl-str">'12345'</span>}
)

<span class="hl-cmt"># Webhook verification</span>
event = verify_webhook(payload, sig_header)
<span class="hl-kw">if</span> event.type == <span class="hl-str">'payment_intent.succeeded'</span>:
    handle_success(event.data.object)</pre>
    </div>
    <div class="doc-card">
      <h3>twilio_sms</h3>
      <div class="doc-desc">Twilio SMS, WhatsApp, bulk messaging, verification codes, and incoming webhook validation.</div>
      <span class="doc-install">pip install twilio</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.twilio_sms <span class="hl-kw">import</span> send_sms, send_whatsapp

send_sms(to=<span class="hl-str">'+15559876543'</span>, body=<span class="hl-str">'Hello!'</span>)
send_whatsapp(to=<span class="hl-str">'+15559876543'</span>, body=<span class="hl-str">'Hi via WhatsApp!'</span>)

<span class="hl-cmt"># Verification flow</span>
send_verification(<span class="hl-str">'+15559876543'</span>)
is_valid = check_verification(<span class="hl-str">'+15559876543'</span>, <span class="hl-str">'123456'</span>)

<span class="hl-cmt"># Bulk</span>
send_bulk_sms(recipients=[...], body=<span class="hl-str">'Announcement!'</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>slack_notifications</h3>
      <div class="doc-desc">Slack webhooks: simple messages, blocks, attachments, and a SlackNotifier class with info/success/warning/error levels.</div>
      <span class="doc-install">SLACK_WEBHOOK_URL in settings</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.slack_notifications <span class="hl-kw">import</span> send_message, SlackNotifier

send_message(<span class="hl-str">'Hello!'</span>, channel=<span class="hl-str">'#general'</span>)

notifier = SlackNotifier(channel=<span class="hl-str">'#alerts'</span>)
notifier.success(<span class="hl-str">'Deploy complete!'</span>)
notifier.error(<span class="hl-str">'Build failed!'</span>)

<span class="hl-cmt"># Error with context</span>
notify_error(exception, context={<span class="hl-str">'user_id'</span>: <span class="hl-num">123</span>})</pre>
    </div>
    <div class="doc-card">
      <h3>discord_notifications</h3>
      <div class="doc-desc">Discord webhooks: messages, rich embeds with fields/author/footer, and DiscordNotifier class.</div>
      <span class="doc-install">DISCORD_WEBHOOK_URL in settings</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.discord_notifications <span class="hl-kw">import</span> send_embed

send_embed(
    title=<span class="hl-str">'New Order'</span>,
    description=<span class="hl-str">'Order #12345 placed'</span>,
    color=<span class="hl-num">0x00ff00</span>,
    fields=[
        {<span class="hl-str">'name'</span>: <span class="hl-str">'Customer'</span>, <span class="hl-str">'value'</span>: <span class="hl-str">'John'</span>, <span class="hl-str">'inline'</span>: <span class="hl-kw">True</span>},
        {<span class="hl-str">'name'</span>: <span class="hl-str">'Amount'</span>, <span class="hl-str">'value'</span>: <span class="hl-str">'$99.99'</span>, <span class="hl-str">'inline'</span>: <span class="hl-kw">True</span>}
    ]
)</pre>
    </div>
  </div>
</section>

<!-- ========== AI ========== -->
<section id="ai">
  <div class="section-header">
    <span class="section-tag cloud">Cloud</span>
    <h2 class="section-title">AI Integrations</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>openai_integration</h3>
      <div class="doc-desc">OpenAI API: chat completions, streaming, embeddings, image generation, moderation, and function calling.</div>
      <span class="doc-install">pip install openai &middot; OPENAI_API_KEY in settings</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.openai_integration <span class="hl-kw">import</span> (
    chat_completion, OpenAIClient, get_embedding,
    generate_image, stream_chat, moderate
)

response = chat_completion([
    {<span class="hl-str">'role'</span>: <span class="hl-str">'user'</span>, <span class="hl-str">'content'</span>: <span class="hl-str">'What is Django?'</span>}
])

client = OpenAIClient()
response = client.chat(<span class="hl-str">'Summarize this'</span>,
    system_prompt=<span class="hl-str">'Be concise.'</span>)

<span class="hl-cmt"># Streaming</span>
<span class="hl-kw">for</span> chunk <span class="hl-kw">in</span> stream_chat(messages):
    <span class="hl-kw">print</span>(chunk, end=<span class="hl-str">''</span>)

embedding = get_embedding(<span class="hl-str">'Hello!'</span>)  <span class="hl-cmt"># [0.123, ...]</span>
image_url = generate_image(<span class="hl-str">'A sunset'</span>)</pre>
    </div>
    <div class="doc-card">
      <h3>anthropic_integration</h3>
      <div class="doc-desc">Anthropic Claude API: text completion, chat, streaming, token counting, and vision (image analysis).</div>
      <span class="doc-install">pip install anthropic &middot; ANTHROPIC_API_KEY in settings</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.anthropic_integration <span class="hl-kw">import</span> (
    text_completion, AnthropicClient,
    stream_completion, count_tokens
)

response = text_completion(<span class="hl-str">'Explain quantum computing'</span>)

client = AnthropicClient()
response = client.chat(<span class="hl-str">'What is ML?'</span>,
    system_prompt=<span class="hl-str">'Be concise.'</span>,
    model=<span class="hl-str">'claude-3-sonnet-20240229'</span>)

<span class="hl-cmt"># Streaming</span>
<span class="hl-kw">for</span> chunk <span class="hl-kw">in</span> stream_completion(<span class="hl-str">'Tell me a story'</span>):
    <span class="hl-kw">print</span>(chunk, end=<span class="hl-str">''</span>)

tokens = count_tokens(<span class="hl-str">'Hello!'</span>)  <span class="hl-cmt"># int</span></pre>
    </div>
  </div>
</section>

<!-- ========== INFRASTRUCTURE ========== -->
<section id="infra">
  <div class="section-header">
    <span class="section-tag cloud">Cloud</span>
    <h2 class="section-title">Infrastructure</h2>
  </div>
  <div class="grid-2">
    <div class="doc-card">
      <h3>redis_cache</h3>
      <div class="doc-desc">Redis caching, rate limiting, distributed locks, pub/sub, and a full RedisClient with hash/list ops.</div>
      <span class="doc-install">pip install redis &middot; REDIS_URL in settings</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.redis_cache <span class="hl-kw">import</span> (
    cache_get, cache_set, rate_limit, distributed_lock
)

cache_set(<span class="hl-str">'user:123'</span>, {<span class="hl-str">'name'</span>: <span class="hl-str">'John'</span>}, ttl=<span class="hl-num">3600</span>)
user = cache_get(<span class="hl-str">'user:123'</span>)

<span class="hl-cmt"># Rate limiting</span>
<span class="hl-kw">if not</span> rate_limit(f<span class="hl-str">'api:user:{id}'</span>, limit=<span class="hl-num">100</span>, window=<span class="hl-num">60</span>):
    <span class="hl-kw">return</span> JsonResponse({<span class="hl-str">'error'</span>: <span class="hl-str">'Rate limit'</span>}, status=<span class="hl-num">429</span>)

<span class="hl-cmt"># Distributed lock</span>
<span class="hl-kw">with</span> distributed_lock(<span class="hl-str">'my-resource'</span>, timeout=<span class="hl-num">30</span>):
    do_critical_work()

<span class="hl-cmt"># Pub/Sub</span>
publish(<span class="hl-str">'channel:events'</span>, {<span class="hl-str">'event'</span>: <span class="hl-str">'new_order'</span>})</pre>
    </div>
    <div class="doc-card">
      <h3>sentry_integration</h3>
      <div class="doc-desc">Sentry error tracking: exception capture, messages, user context, breadcrumbs, tags, and performance monitoring.</div>
      <span class="doc-install">pip install sentry-sdk &middot; SENTRY_DSN in settings</span>
      <pre class="code"><span class="hl-kw">from</span> django_extensions.sentry_integration <span class="hl-kw">import</span> (
    init_sentry, capture_exception, capture_message,
    set_user, set_context, add_breadcrumb, start_transaction
)

init_sentry()  <span class="hl-cmt"># Call in settings.py</span>

<span class="hl-kw">try</span>:
    risky_operation()
<span class="hl-kw">except</span> Exception <span class="hl-kw">as</span> e:
    capture_exception(e)

set_user({<span class="hl-str">'id'</span>: user.id, <span class="hl-str">'email'</span>: user.email})
set_context(<span class="hl-str">'order'</span>, {<span class="hl-str">'id'</span>: order.id})

<span class="hl-cmt"># Performance monitoring</span>
<span class="hl-kw">with</span> start_transaction(op=<span class="hl-str">'task'</span>, name=<span class="hl-str">'process_order'</span>):
    process()</pre>
    </div>
  </div>
</section>

<!-- ========== ALL EXTENSIONS ========== -->
<section id="extensions">
  <div class="section-header">
    <span class="section-tag">Map</span>
    <h2 class="section-title">All 51 Extensions</h2>
  </div>
  <div class="ext-grid">
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>timestamped_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>uuid_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>soft_delete</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>soft_delete_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>ordered_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>status_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>slugged_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>activator_model</div>
    <div class="ext-chip" onclick="scrollTo_('models')"><span class="ext-dot" style="background:var(--accent)"></span>title_slug_model</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>auto_created_field</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>auto_modified_field</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>short_uuid_field</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>encrypted_field</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>json_schema_field</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>money_field</div>
    <div class="ext-chip" onclick="scrollTo_('fields')"><span class="ext-dot" style="background:var(--blue)"></span>phone_field</div>
    <div class="ext-chip" onclick="scrollTo_('managers')"><span class="ext-dot" style="background:var(--purple)"></span>soft_delete_manager</div>
    <div class="ext-chip" onclick="scrollTo_('managers')"><span class="ext-dot" style="background:var(--purple)"></span>active_manager</div>
    <div class="ext-chip" onclick="scrollTo_('managers')"><span class="ext-dot" style="background:var(--purple)"></span>random_manager</div>
    <div class="ext-chip" onclick="scrollTo_('validators')"><span class="ext-dot" style="background:var(--red)"></span>phone_validator</div>
    <div class="ext-chip" onclick="scrollTo_('validators')"><span class="ext-dot" style="background:var(--red)"></span>credit_card_validator</div>
    <div class="ext-chip" onclick="scrollTo_('validators')"><span class="ext-dot" style="background:var(--red)"></span>color_validator</div>
    <div class="ext-chip" onclick="scrollTo_('validators')"><span class="ext-dot" style="background:var(--red)"></span>url_validator</div>
    <div class="ext-chip" onclick="scrollTo_('humanize')"><span class="ext-dot" style="background:var(--orange)"></span>humanize_tags</div>
    <div class="ext-chip" onclick="scrollTo_('strings')"><span class="ext-dot" style="background:var(--orange)"></span>url_tags</div>
    <div class="ext-chip" onclick="scrollTo_('math')"><span class="ext-dot" style="background:var(--orange)"></span>math_tags</div>
    <div class="ext-chip" onclick="scrollTo_('strings')"><span class="ext-dot" style="background:var(--orange)"></span>string_tags</div>
    <div class="ext-chip" onclick="scrollTo_('commands')"><span class="ext-dot" style="background:var(--green)"></span>shell_plus</div>
    <div class="ext-chip" onclick="scrollTo_('commands')"><span class="ext-dot" style="background:var(--green)"></span>show_urls</div>
    <div class="ext-chip" onclick="scrollTo_('commands')"><span class="ext-dot" style="background:var(--green)"></span>clean_pyc</div>
    <div class="ext-chip" onclick="scrollTo_('commands')"><span class="ext-dot" style="background:var(--green)"></span>reset_db</div>
    <div class="ext-chip" onclick="scrollTo_('commands')"><span class="ext-dot" style="background:var(--green)"></span>generate_secret_key</div>
    <div class="ext-chip" onclick="scrollTo_('middleware')"><span class="ext-dot" style="background:#888"></span>timezone_middleware</div>
    <div class="ext-chip" onclick="scrollTo_('middleware')"><span class="ext-dot" style="background:#888"></span>request_logging_middleware</div>
    <div class="ext-chip" onclick="scrollTo_('decorators')"><span class="ext-dot" style="background:#888"></span>ajax_required</div>
    <div class="ext-chip" onclick="scrollTo_('decorators')"><span class="ext-dot" style="background:#888"></span>anonymous_required</div>
    <div class="ext-chip" onclick="scrollTo_('decorators')"><span class="ext-dot" style="background:#888"></span>superuser_required</div>
    <div class="ext-chip" onclick="scrollTo_('utilities')"><span class="ext-dot" style="background:#888"></span>cache_decorator</div>
    <div class="ext-chip" onclick="scrollTo_('utilities')"><span class="ext-dot" style="background:#888"></span>pagination_utils</div>
    <div class="ext-chip" onclick="scrollTo_('utilities')"><span class="ext-dot" style="background:#888"></span>email_utils</div>
    <div class="ext-chip" onclick="scrollTo_('aws')"><span class="ext-dot" style="background:#4da8ff"></span>aws_s3_storage</div>
    <div class="ext-chip" onclick="scrollTo_('aws')"><span class="ext-dot" style="background:#4da8ff"></span>aws_ses_email</div>
    <div class="ext-chip" onclick="scrollTo_('aws')"><span class="ext-dot" style="background:#4da8ff"></span>aws_sns_notifications</div>
    <div class="ext-chip" onclick="scrollTo_('aws')"><span class="ext-dot" style="background:#4da8ff"></span>aws_sqs_queue</div>
    <div class="ext-chip" onclick="scrollTo_('services')"><span class="ext-dot" style="background:#ffa84d"></span>stripe_payments</div>
    <div class="ext-chip" onclick="scrollTo_('services')"><span class="ext-dot" style="background:#ffa84d"></span>twilio_sms</div>
    <div class="ext-chip" onclick="scrollTo_('services')"><span class="ext-dot" style="background:#ffa84d"></span>slack_notifications</div>
    <div class="ext-chip" onclick="scrollTo_('services')"><span class="ext-dot" style="background:#ffa84d"></span>discord_notifications</div>
    <div class="ext-chip" onclick="scrollTo_('ai')"><span class="ext-dot" style="background:#b84dff"></span>openai_integration</div>
    <div class="ext-chip" onclick="scrollTo_('ai')"><span class="ext-dot" style="background:#b84dff"></span>anthropic_integration</div>
    <div class="ext-chip" onclick="scrollTo_('infra')"><span class="ext-dot" style="background:#ff4d6a"></span>redis_cache</div>
    <div class="ext-chip" onclick="scrollTo_('infra')"><span class="ext-dot" style="background:#ff4d6a"></span>sentry_integration</div>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem;font-family:var(--mono);font-size:.65rem">
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:var(--accent);display:inline-block"></span><span style="color:var(--text3)">Models</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:var(--blue);display:inline-block"></span><span style="color:var(--text3)">Fields</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:var(--purple);display:inline-block"></span><span style="color:var(--text3)">Managers</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:var(--red);display:inline-block"></span><span style="color:var(--text3)">Validators</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:var(--orange);display:inline-block"></span><span style="color:var(--text3)">Tags</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:var(--green);display:inline-block"></span><span style="color:var(--text3)">Commands</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:#888;display:inline-block"></span><span style="color:var(--text3)">Utilities</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:#4da8ff;display:inline-block"></span><span style="color:var(--text3)">AWS</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:#ffa84d;display:inline-block"></span><span style="color:var(--text3)">Services</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:#b84dff;display:inline-block"></span><span style="color:var(--text3)">AI</span></span>
    <span style="display:flex;align-items:center;gap:.3rem"><span class="ext-dot" style="background:#ff4d6a;display:inline-block"></span><span style="color:var(--text3)">Infrastructure</span></span>
  </div>
</section>

</div>

<div style="text-align:center;padding:2rem;border-top:1px solid var(--border);color:var(--text3);font-size:.78rem;font-family:var(--mono)">
  Django Extensions Collection v1.0.0 &middot; MIT License &middot; 680 tests passing
</div>

<script>
function scrollTo_(id) {
  document.getElementById(id).scrollIntoView({behavior:'smooth'});
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  if(event && event.target && event.target.classList) event.target.classList.add('active');
}

const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const id = e.target.id;
      document.querySelectorAll('.nav-btn').forEach(b => {
        const t = b.textContent.toLowerCase();
        const match = t === id || t.startsWith(id.substring(0,4));
        b.classList.toggle('active', match);
      });
    }
  });
}, {threshold: 0.2});
document.querySelectorAll('section[id]').forEach(s => observer.observe(s));

async function validate(type, inputId, resultId) {
  const value = document.getElementById(inputId).value;
  const el = document.getElementById(resultId);
  el.className = 'result';
  el.innerHTML = '<span class="result-text" style="animation:pulse .8s infinite">Validating...</span>';
  const res = await fetch('/api/validate/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type,value})});
  const data = await res.json();
  el.className = 'result ' + (data.valid ? 'valid' : 'invalid');
  el.innerHTML = `<span class="result-icon">${data.valid?'\u2713':'\u2717'}</span><div><div class="result-text">${data.valid?'Valid':'Invalid'}</div><div class="result-detail">${data.detail}</div></div>`;
}

async function validateColor() {
  const value = document.getElementById('color-input').value;
  const el = document.getElementById('color-result');
  const swatch = document.getElementById('color-swatch');
  el.className = 'result';
  const res = await fetch('/api/validate/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'color',value})});
  const data = await res.json();
  el.className = 'result ' + (data.valid ? 'valid' : 'invalid');
  el.innerHTML = `<span class="result-icon">${data.valid?'\u2713':'\u2717'}</span><div><div class="result-text">${data.valid?'Valid':'Invalid'}</div><div class="result-detail">${data.detail}</div></div>`;
  swatch.style.background = data.valid ? value : 'var(--surface2)';
}

async function runTag(inputId, opId, resultId) {
  const value = document.getElementById(inputId).value;
  const operation = document.getElementById(opId).value;
  const el = document.getElementById(resultId);
  const res = await fetch('/api/tags/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation,value})});
  const data = await res.json();
  el.className = 'result valid';
  el.innerHTML = `<span class="result-icon">&rarr;</span><span class="result-text" style="color:var(--text)">${data.output}</span>`;
}

async function runTagDirect(inputId, op, resultId) {
  const value = document.getElementById(inputId).value;
  const el = document.getElementById(resultId);
  const res = await fetch('/api/tags/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation:op,value})});
  const data = await res.json();
  el.className = 'result valid';
  el.innerHTML = `<span class="result-icon">&rarr;</span><span class="result-text" style="color:var(--text)">${data.output}</span>`;
}

async function generateKey() {
  const el = document.getElementById('key-output');
  el.style.opacity = '0.5';
  el.textContent = 'Generating...';
  const res = await fetch('/api/generate-key/', {method:'POST'});
  const data = await res.json();
  el.style.opacity = '1';
  el.textContent = data.key;
}

async function loadExamples() {
  const examples = [['intcomma','1000000','ex-intcomma'],['intword','1500000','ex-intword'],['ordinal','42','ex-ordinal'],['filesizeformat','1073741824','ex-filesize'],['duration','3661','ex-duration']];
  for (const [op, val, id] of examples) {
    const res = await fetch('/api/tags/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation:op,value:val})});
    const data = await res.json();
    document.getElementById(id).textContent = data.output;
  }
}

document.getElementById('color-input').addEventListener('input', e => {
  document.getElementById('color-swatch').style.background = e.target.value;
});

loadExamples();
</script>
</body>
</html>"""


# URL config
from django.urls import path

urlpatterns = [
    path('', index),
    path('api/validate/', api_validate),
    path('api/tags/', api_template_tags),
    path('api/generate-key/', api_generate_key),
]


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.core.management import execute_from_command_line

    settings.ROOT_URLCONF = 'web_demo'

    sys.argv = ['web_demo', 'runserver', '0.0.0.0:3322', '--noreload']
    execute_from_command_line(sys.argv)
