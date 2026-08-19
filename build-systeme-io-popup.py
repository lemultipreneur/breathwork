# -*- coding: utf-8 -*-
"""LP Breathwork -> bloc Code HTML Systeme.io.
Les boutons declenchent un clic sur le bouton Systeme.io invisible
(TRIGGER_ID), seul capable d'ouvrir une popup."""
import io, re

TRIGGER_ID = 'button-8bce75f3'

ns = {}
exec(io.open('build-systeme-io.py', encoding='utf-8').read().split("H = (")[0], ns)
scope_css, NORMALIZE, BASE, SCOPE, ASSETS = (
    ns['scope_css'], ns['NORMALIZE'], ns['BASE'], ns['SCOPE'], ns['ASSETS'])

page  = io.open('index.html', encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', page, re.S).group(1)
body  = re.search(r'<body>(.*?)</body>',  page, re.S).group(1)

for rel in ASSETS:
    body = body.replace('"%s"' % rel, '"%s%s"' % (BASE, rel))

# les 3 CTA deviennent des declencheurs
body = re.sub(r'<button class="(btn[^"]*)" data-open-modal>(.*?)</button>',
              r'<a class="\1" href="#" data-open-popup>\2</a>', body)

# mon popup maison disparait
body = re.sub(r'<!-- =+ POPUP FORMULAIRE =+ -->.*?(?=<script>)', '', body, flags=re.S)

SCRIPT = '''<script>
(function(){
  /* ============================================================
     ID du bouton Systeme.io invisible qui ouvre la popup.
     Si tu recrees ce bouton un jour, remplace la valeur ci-dessous
     par son nouvel identifiant : c'est la seule ligne a changer.
     ============================================================ */
  var TRIGGER_ID = '%s';

  function ouvrirPopup(e){
    if (e) e.preventDefault();
    var hote = document.getElementById(TRIGGER_ID);
    if (!hote){
      console.warn('[LP] Bouton Systeme.io "' + TRIGGER_ID + '" introuvable : la popup ne peut pas s\\'ouvrir.');
      return;
    }
    /* le bouton Systeme.io est parfois un conteneur : on vise le lien interieur */
    var cible = (hote.matches && hote.matches('a, button'))
              ? hote
              : (hote.querySelector('a, button') || hote);
    cible.click();
  }

  document.querySelectorAll('#noe-lp [data-open-popup]').forEach(function(b){
    b.addEventListener('click', ouvrirPopup);
  });

  /* barre collante mobile : apparait une fois le hero passe */
  var sticky = document.getElementById('sticky');
  var hero   = document.querySelector('#noe-lp .hero');
  if (sticky && hero && 'IntersectionObserver' in window){
    new IntersectionObserver(function(e){
      sticky.classList.toggle('show', !e[0].isIntersecting);
    }, {threshold:0}).observe(hero);
  }
})();
</script>''' % TRIGGER_ID

body = re.sub(r'<script>.*?</script>', SCRIPT, body, flags=re.S)
assert len(re.findall(r'<a class="btn[^"]*" href="#" data-open-popup>', body)) == 3
assert 'overlay' not in body

css = scope_css(style)
DEAD = ('.overlay', '.modal', '#signup-form', '.field', '.row-2', '.modal-close')
css = re.sub(r'([^{}\n][^{}]*)\{[^{}]*\}\n?',
             lambda m: '' if any(d in m.group(1) for d in DEAD) else m.group(0), css)
css = re.sub(r'\n{3,}', '\n\n', css)

extra = '%s .btn{text-align:center;text-decoration:none;cursor:pointer}' % SCOPE
imp = ("@import url('https://fonts.googleapis.com/css2?"
       "family=Inter:wght@400;500;600;700;800&display=swap');")
hdr = ('<!-- ============================================================\n'
       '     LANDING PAGE Breathwork - a coller dans un bloc "Code HTML"\n'
       '\n'
       '     PREREQUIS : un bouton Systeme.io d\'identifiant %s\n'
       '     doit exister sur cette page, regle pour ouvrir ta popup.\n'
       '     Rends-le invisible, ne le supprime pas : ce sont mes boutons\n'
       '     qui cliquent dessus a la place du visiteur.\n'
       '     ============================================================ -->' % TRIGGER_ID)

out = (hdr + '\n<style>\n' + imp + '\n\n' + NORMALIZE + '\n\n' + extra + '\n\n'
       + css.strip() + '\n</style>\n\n<div id="noe-lp">\n' + body.strip() + '\n</div>\n')
io.open('systeme-io-popup.html', 'w', encoding='utf-8').write(out)
print('systeme-io-popup.html : %d Ko, declencheur %s' % (len(out)//1024, TRIGGER_ID))
