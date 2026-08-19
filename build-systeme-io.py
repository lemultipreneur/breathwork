# -*- coding: utf-8 -*-
"""Genere les versions Systeme.io des deux pages (CSS cantonne a #noe-lp)."""
import io, re

BASE  = 'https://lemultipreneur.github.io/breathwork/'
SCOPE = '#noe-lp'
FONT  = "'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
ASSETS = ['noe.jpg', 'formation.jpg'] + ['temoignages/poster-%d.jpg' % i for i in (1,2,3)] \
                     + ['temoignages/temoignage-%d.mp4' % i for i in (1,2,3)]

def scope_selector(sel):
    sel = ' '.join(sel.split())
    if not sel:                 return None
    if sel == ':root':          return SCOPE + ', :root'
    if sel == 'html':           return None
    if sel == 'body':           return SCOPE
    if sel == 'body.no-scroll': return 'body.no-scroll'
    if sel == '*':              return SCOPE + ', ' + SCOPE + ' *'
    return SCOPE + ' ' + sel

def scope_rules(css):
    out, i = [], 0
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        out.append(css[i:m.start()]); i = m.end()
        parts = [p for p in (scope_selector(s) for s in m.group(1).split(',')) if p]
        if parts:
            out.append('%s{%s}\n' % (','.join(parts), m.group(2).strip()))
    out.append(css[i:])
    return ''.join(out)

def scope_css(style):
    style = re.sub(r'/\*.*?\*/', '', style, flags=re.S)
    last, res = 0, []
    for m in re.finditer(r'@media[^{]+\{', style):
        depth, j = 1, m.end()
        while depth:
            if style[j] == '{': depth += 1
            elif style[j] == '}': depth -= 1
            j += 1
        res.append(scope_rules(style[last:m.start()]))
        res.append('\n' + ' '.join(m.group(0).split()) + '\n'
                   + scope_rules(style[m.end():j-1]) + '}\n')
        last = j
    res.append(scope_rules(style[last:]))
    return re.sub(r'\n{3,}', '\n\n', ''.join(res)).strip()

NORMALIZE = """
%(s)s, %(s)s *{
  font-family:%(f)s;
  box-sizing:border-box;
  -webkit-font-smoothing:antialiased;
}
%(s)s *{
  margin:0;padding:0;border:0;outline:0;
  background:transparent;list-style:none;float:none;
  text-transform:none;letter-spacing:normal;
  color:inherit;text-align:inherit;font-style:normal;line-height:inherit;
  text-shadow:none;box-shadow:none;border-radius:0;
}
%(s)s a{text-decoration:none}
%(s)s{line-height:1.6;text-align:left}
""".strip() % {'s': SCOPE, 'f': FONT}

# Habille le formulaire Systeme.io colle dans le popup pour qu'il reprenne la DA
SIO_FORM_CSS = """
%(s)s #sio-form input:not([type=checkbox]):not([type=radio]):not([type=submit]),
%(s)s #sio-form select,
%(s)s #sio-form textarea{
  width:100%%;font-family:inherit;font-size:16px;color:var(--ink);
  padding:14px 16px;margin-bottom:14px;
  border:1px solid var(--line);border-radius:12px;background:#FBFCFE;
}
%(s)s #sio-form input:focus,%(s)s #sio-form select:focus,%(s)s #sio-form textarea:focus{
  outline:none;border-color:var(--blue-500);background:#fff;
  box-shadow:0 0 0 4px rgba(44,123,242,.14);
}
%(s)s #sio-form label{display:block;font-size:13.5px;font-weight:600;margin-bottom:7px}
%(s)s #sio-form button,
%(s)s #sio-form input[type=submit],
%(s)s #sio-form .btn{
  width:100%%;display:block;cursor:pointer;border:0;
  font-family:inherit;font-size:16px;font-weight:700;letter-spacing:.02em;
  color:#fff;background:linear-gradient(180deg,var(--blue-500),var(--blue-600));
  padding:20px 30px;border-radius:14px;margin-top:10px;
  box-shadow:var(--shadow-cta);
}
""".strip() % {'s': SCOPE}

FORM_SLOT = '''      <!-- ================================================================
           ZONE FORMULAIRE
           Remplace TOUT le contenu de <div id="sio-form"> par le code
           d'integration de ton formulaire Systeme.io.
           Le CSS au-dessus l'habillera automatiquement aux couleurs de la page.
           Le formulaire ci-dessous n'est qu'un visuel : il n'enregistre rien.
           ================================================================ -->
      <div id="sio-form">

        <form id="signup-form" novalidate>
          <div class="row-2">
            <div class="field">
              <label for="firstname">Prenom</label>
              <input type="text" id="firstname" name="firstname" autocomplete="given-name" placeholder="Noe" required>
            </div>
            <div class="field">
              <label for="lastname">Nom</label>
              <input type="text" id="lastname" name="lastname" autocomplete="family-name" placeholder="Perret" required>
            </div>
          </div>
          <div class="field">
            <label for="email">Adresse email</label>
            <input type="email" id="email" name="email" autocomplete="email" placeholder="ton@email.com" required>
          </div>
          <div class="field">
            <label for="phone">Numero de telephone (WhatsApp)</label>
            <input type="tel" id="phone" name="phone" autocomplete="tel" placeholder="+33 6 12 34 56 78" required>
          </div>
          <button type="submit" class="btn btn-full">JE VALIDE MA PLACE</button>
        </form>

      </div>
      <p class="micro">Experience transformative 100%% offerte</p>
'''

def build(src_path, out_path, header, form_slot=False, extra_css=''):
    src = io.open(src_path, encoding='utf-8').read()
    style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
    body  = re.search(r'<body>(.*?)</body>',  src, re.S).group(1)

    for rel in ASSETS:
        body = body.replace('"%s"' % rel, '"%s%s"' % (BASE, rel))
    body = body.replace("'confirmation.html'", "'%sconfirmation.html'" % BASE)

    if form_slot:
        old = re.search(r'    <form id="signup-form".*?</form>\n\n?(      <p class="micro">[^<]*</p>\n)?',
                        body, re.S)
        body = body[:old.start()] + (FORM_SLOT % ()) + body[old.end():]
        # le handler ne doit s'activer que si le formulaire de demo est encore la
        body = body.replace("  form.addEventListener('submit', function(e){",
                            "  if (!form) return;\n  form.addEventListener('submit', function(e){")

    css = scope_css(style)
    imp = ("@import url('https://fonts.googleapis.com/css2?"
           "family=Inter:wght@400;500;600;700;800&display=swap');")
    out = (header + '\n<style>\n' + imp + '\n\n' + NORMALIZE + '\n\n'
           + (extra_css + '\n\n' if extra_css else '') + css + '\n</style>\n\n'
           + '<div id="noe-lp">\n' + body.strip() + '\n</div>\n')
    io.open(out_path, 'w', encoding='utf-8').write(out)
    return len(out)

H = ('<!-- ============================================================\n'
     '     %s - a coller dans un bloc "Code HTML" de Systeme.io\n'
     '     CSS + markup + scripts : tout est inclus.\n'
     '     Le CSS est cantonne a #noe-lp : il ne deborde pas sur ta page,\n'
     '     et le theme Systeme.io ne peut pas deteindre sur lui.\n'
     '     ============================================================ -->')

n1 = build('index.html', 'systeme-io.html',
           H % 'LANDING PAGE Breathwork', form_slot=True, extra_css=SIO_FORM_CSS)
n2 = build('confirmation.html', 'systeme-io-confirmation.html',
           H % 'PAGE DE CONFIRMATION Breathwork')
print('landing      : %d Ko' % (n1 // 1024))
print('confirmation : %d Ko' % (n2 // 1024))
