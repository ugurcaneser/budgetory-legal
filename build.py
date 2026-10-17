"""Builds the Budgetory privacy site that GitHub Pages serves from docs/:

    index.html          the privacy policy, from the app's own texts (locales/<lang>.json) in the
                        order components/PrivacyPolicyModal.tsx shows them, so both say the same
    delete-account.html Google Play's account deletion page, from deletion/<lang>.json
    .nojekyll           so that GitHub Pages serves the files as they are

    python3 build.py    reads the app from ../Budgetory, or from $BUDGETORY_APP
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.environ.get('BUDGETORY_APP') or os.path.join(HERE, '..', 'Budgetory')
OUT = os.path.join(HERE, 'docs')
EMAIL = 'ugurcaneser@icloud.com'
LANGS = [
    # code, endonym
    ('en', 'English'),
    ('tr', 'Türkçe'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('ru', 'Русский'),
]
CODES = [code for code, _ in LANGS]

# The deletion page, in reading order: (kind, key or keys). Its anchors are named after the h2s.
DELETION = [
    ('h1', 'deleteTitle'),
    ('byline', 'deleteByline'),
    ('p', 'deleteIntro'),
    ('h2:in-app', 'deleteInAppTitle'),
    ('ol', ['deleteStep1', 'deleteStep2', 'deleteStep3', 'deleteStep4']),
    ('p', 'deleteInAppDone'),
    ('h2:email', 'deleteEmailTitle'),
    ('p', 'deleteEmail'),
    ('h2:deleted', 'deleteDeletedTitle'),
    ('ul', ['deleteDeletedFirebase', 'deleteDeletedServer', 'deleteDeletedDevice']),
    ('h2:kept', 'deleteKeptTitle'),
    ('ul', ['deleteKeptBackups', 'deleteKeptLogs', 'deleteKeptProviders']),
    ('h2:partial', 'deletePartialTitle'),
    ('p', 'deletePartial'),
]


def policy_blocks():
    """The policy's blocks as the app shows them: [(kind, key or [keys])], read from the component."""
    source = open(os.path.join(APP, 'components', 'PrivacyPolicyModal.tsx'), encoding='utf-8').read()
    body = source[source.index('const blocks: PolicyBlock[] = ['):]
    body = body[:body.index('\n  ];')]
    pattern = re.compile(
        r"\{\s*kind:\s*'(date|section|subsection|paragraph)',\s*text:\s*t\('(\w+)'\)\s*\}"
        r"|\{\s*kind:\s*'list',\s*items:\s*\[(.*?)\],?\s*\}",
        re.S,
    )
    blocks = []
    for match in pattern.finditer(body):
        if match.group(1):
            blocks.append((match.group(1), match.group(2)))
        else:
            blocks.append(('list', re.findall(r"t\('(\w+)'\)", match.group(3))))
    keys = [k for _, key in blocks for k in (key if isinstance(key, list) else [key])]
    assert len(keys) == len(set(keys)) == body.count("t('"), 'every text of the component must be read once'
    return blocks, keys


def slug(key):
    """policyScannerAndroidTitle -> scanner-android"""
    name = key[len('policy'):-len('Title')]
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()


def inline(text):
    out = html.escape(text, quote=False)
    # The developer's name stays on one line.
    out = out.replace('Uğurcan Eser', 'Uğurcan&nbsp;Eser')
    return out.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')


def anchor(code, name):
    return name if code == 'en' else f'{code}-{name}'


def policy_article(code, texts, blocks):
    parts = [f'<article class="lang" id="{code}" lang="{code}">', f'<h1>{inline(texts["privacyPolicy"])}</h1>']
    for kind, key in blocks:
        if kind == 'date':
            parts.append(f'<p class="updated">{inline(texts[key])}</p>')
        elif kind == 'section':
            parts.append(f'<h2 id="{anchor(code, slug(key))}">{inline(texts[key])}</h2>')
        elif kind == 'subsection':
            parts.append(f'<h3 id="{anchor(code, slug(key))}">{inline(texts[key])}</h3>')
        elif kind == 'paragraph':
            parts.append(f'<p>{inline(texts[key])}</p>')
        else:
            parts.append('<ul>' + ''.join(f'<li>{inline(texts[k])}</li>' for k in key) + '</ul>')
    parts.append('</article>')
    return '\n'.join(parts)


def deletion_article(code, texts):
    parts = [f'<article class="lang" id="{code}" lang="{code}">']
    for kind, key in DELETION:
        if kind == 'h1':
            parts.append(f'<h1>{inline(texts[key])}</h1>')
        elif kind == 'byline':
            parts.append(f'<p class="updated">{inline(texts[key])}</p>')
        elif kind.startswith('h2:'):
            parts.append(f'<h2 id="{anchor(code, kind[3:])}">{inline(texts[key])}</h2>')
        elif kind == 'p':
            parts.append(f'<p>{inline(texts[key])}</p>')
        else:
            parts.append(f'<{kind}>' + ''.join(f'<li>{inline(texts[k])}</li>' for k in key) + f'</{kind}>')
    parts.append('</article>')
    return '\n'.join(parts)


CSS = """
:root {
  color-scheme: light dark;
  --bg: #fbfaf7;
  --text: #1c1d1f;
  --muted: #5d6066;
  --rule: #e2dfd8;
  --link: #2450c4;
  --chip: #efece5;
  --chip-text: #2a2b2e;
  --chip-on: #1c1d1f;
  --chip-on-text: #fbfaf7;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121315;
    --text: #e9e9ec;
    --muted: #a3a6ad;
    --rule: #2b2d31;
    --link: #93b2ff;
    --chip: #1f2124;
    --chip-text: #d9dade;
    --chip-on: #e9e9ec;
    --chip-on-text: #121315;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 17px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  overflow-wrap: break-word;
}
.wrap { max-width: 44rem; margin: 0 auto; padding: 0 16px; }
header { border-bottom: 1px solid var(--rule); }
header .wrap { padding-top: 14px; padding-bottom: 14px; display: flex; flex-direction: column; gap: 10px; }
.top { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 16px; }
.brand { font-weight: 650; letter-spacing: -0.01em; font-size: 1.05rem; color: var(--text); text-decoration: none; }
.pages { display: flex; flex-wrap: wrap; gap: 4px 16px; font-size: 0.95rem; }
.pages a { color: var(--muted); text-decoration: none; }
.pages a:hover { text-decoration: underline; }
.pages a[aria-current="page"] { color: var(--text); font-weight: 600; }
#languages ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px; }
#languages a {
  display: inline-block;
  padding: 5px 11px;
  border-radius: 999px;
  background: var(--chip);
  color: var(--chip-text);
  text-decoration: none;
  font-size: 0.88rem;
  line-height: 1.4;
}
#languages a:hover { text-decoration: underline; }
#languages a[aria-current="true"] { background: var(--chip-on); color: var(--chip-on-text); }
a { color: var(--link); }
a:focus-visible { outline: 2px solid var(--link); outline-offset: 2px; }
main { padding-top: 8px; padding-bottom: 64px; }
html:not(.js) .lang + .lang { border-top: 1px solid var(--rule); margin-top: 48px; }
.js .lang { display: none; }
%(shown)s { display: block; }
h1 { font-size: 1.9rem; line-height: 1.2; letter-spacing: -0.015em; margin: 32px 0 6px; }
h2 { font-size: 1.35rem; line-height: 1.3; margin: 40px 0 10px; }
h3 { font-size: 1.08rem; line-height: 1.35; margin: 26px 0 6px; }
h1, h2, h3 { scroll-margin-top: 16px; }
p, ul, ol { margin: 0 0 14px; }
ul, ol { padding-left: 1.4em; }
li { margin: 0 0 8px; }
ol li { padding-left: 0.2em; }
.updated { color: var(--muted); font-size: 0.95rem; margin-bottom: 24px; }
[lang="de"], [lang="ru"], [lang="tr"] { hyphens: auto; -webkit-hyphens: auto; hyphenate-limit-chars: 10 4 4; }
@media (max-width: 480px) {
  body { font-size: 16px; }
  h1 { font-size: 1.65rem; margin-top: 24px; }
  h2 { font-size: 1.25rem; }
}
""".replace('%(shown)s', ',\n'.join(f'[data-lang="{code}"] #{code}' for code in CODES))

HEAD_SCRIPT = """
(function () {
  var m = /^(tr|de|fr|es|ru)(-|$)/.exec(decodeURIComponent(location.hash.slice(1)));
  var root = document.documentElement;
  root.className = 'js';
  root.setAttribute('data-lang', m ? m[1] : 'en');
  root.lang = m ? m[1] : 'en';
})();
"""

SCRIPT = """
(function () {
  var langs = %(langs)s;
  var labels = %(labels)s;
  var root = document.documentElement;
  function update(scroll) {
    var id = decodeURIComponent(location.hash.slice(1));
    var m = /^(tr|de|fr|es|ru)(-|$)/.exec(id);
    var lang = m ? m[1] : 'en';
    var text = labels[lang];
    root.setAttribute('data-lang', lang);
    root.lang = lang;
    langs.forEach(function (code) {
      var link = document.getElementById('to-' + code);
      if (code === lang) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    // The links to the two pages keep the language.
    ['policy', 'deletion'].forEach(function (page) {
      var link = document.getElementById('page-' + page);
      link.textContent = text[page];
      link.setAttribute('href', link.getAttribute('data-file') + (lang === 'en' ? '' : '#' + lang));
    });
    document.getElementById('pages').setAttribute('aria-label', 'Budgetory');
    document.getElementById('languages').setAttribute('aria-label', text.language);
    document.title = 'Budgetory \\u2013 ' + text[%(page)s];
    if (!scroll) return;
    var target = id && document.getElementById(id);
    if (target && langs.indexOf(id) < 0) target.scrollIntoView();
    else window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', function () { update(true); });
  update(false);
})();
"""


def page(kind, title, description, articles, labels):
    current = {'policy': 'index.html', 'deletion': 'delete-account.html'}
    pages = ''.join(
        f'<a id="page-{name}" href="{file}" data-file="{file}"{" aria-current=" + chr(34) + "page" + chr(34) if name == kind else ""}>'
        f'{html.escape(labels["en"][name])}</a>'
        for name, file in current.items()
    )
    chips = ''.join(
        f'<li><a id="to-{code}" href="#{code}" hreflang="{code}" lang="{code}"'
        f'{" aria-current=" + chr(34) + "true" + chr(34) if code == "en" else ""}>{name}</a></li>'
        for code, name in LANGS
    )
    script = SCRIPT % {
        'langs': json.dumps(CODES),
        'labels': json.dumps(labels, ensure_ascii=False),
        'page': json.dumps(kind),
    }
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="description" content="{html.escape(description)}">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
<script>{HEAD_SCRIPT}</script>
</head>
<body>
<header>
<div class="wrap">
<div class="top">
<a class="brand" href="index.html">Budgetory</a>
<nav id="pages" class="pages" aria-label="Budgetory">{pages}</nav>
</div>
<nav id="languages" aria-label="Language"><ul>{chips}</ul></nav>
</div>
</header>
<main class="wrap">
{articles}
</main>
<script>{script}</script>
</body>
</html>
"""


def main():
    blocks, keys = policy_blocks()
    locales = {code: json.load(open(os.path.join(APP, 'locales', f'{code}.json'), encoding='utf-8')) for code in CODES}
    deletion = {
        code: json.load(open(os.path.join(HERE, 'deletion', f'{code}.json'), encoding='utf-8'))
        for code in CODES
    }
    for code in CODES:
        missing = [key for key in keys + ['privacyPolicy', 'deleteAccount', 'language'] if key not in locales[code]]
        assert not missing, (code, missing)
        missing = [k for _, key in DELETION for k in (key if isinstance(key, list) else [key]) if k not in deletion[code]]
        assert not missing, (code, missing)
    labels = {
        code: {
            'policy': locales[code]['privacyPolicy'],
            'deletion': locales[code]['deleteAccount'],
            'language': locales[code]['language'],
        }
        for code in CODES
    }
    os.makedirs(OUT, exist_ok=True)
    policy_html = page(
        'policy',
        'Budgetory Privacy Policy',
        'How the Budgetory app uses your personal data. In English, Türkçe, Deutsch, Français, Español and Русский.',
        '\n'.join(policy_article(code, locales[code], blocks) for code in CODES),
        labels,
    )
    deletion_html = page(
        'deletion',
        'Delete a Budgetory Account',
        'How to delete your Budgetory account and its data, in the app or by email.',
        '\n'.join(deletion_article(code, deletion[code]) for code in CODES),
        labels,
    )
    for name, content in [('index.html', policy_html), ('delete-account.html', deletion_html), ('.nojekyll', '')]:
        with open(os.path.join(OUT, name), 'w', encoding='utf-8') as handle:
            handle.write(content)
        print('wrote', os.path.relpath(os.path.join(OUT, name), HERE), len(content.encode('utf-8')), 'bytes')


if __name__ == '__main__':
    main()
