#!/usr/bin/env python3
"""Sube las guias .md de /tmp/guias a la base de conocimiento de GLPI (API). Se ejecuta en la VM."""
import glob
import html
import json
import re
import sys
import urllib.request

BASE = "http://localhost/apirest.php"
TOKEN = open("/root/.glpi_api_token").read().strip()


def call(method, path, body=None, headers=None):
    h = {"Content-Type": "application/json"}
    h.update(headers or {})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        print("ERROR", method, path, e.code, e.read().decode()[:300])
        sys.exit(1)


def md_a_html(texto):
    out, en_codigo, lista = [], False, None
    for linea in texto.splitlines():
        if linea.strip().startswith("```"):
            out.append("</pre>" if en_codigo else "<pre>")
            en_codigo = not en_codigo
            continue
        if en_codigo:
            out.append(html.escape(linea))
            continue
        s = linea.strip()
        m_ol = re.match(r"^\d+\.\s+(.*)", s)
        m_ul = re.match(r"^-\s+(.*)", s)
        tipo = "ol" if m_ol else "ul" if m_ul else None
        if lista and lista != tipo:
            out.append(f"</{lista}>")
            lista = None
        if tipo and not lista:
            out.append(f"<{tipo}>")
            lista = tipo
        if tipo:
            out.append("<li>" + html.escape((m_ol or m_ul).group(1)) + "</li>")
        elif s.startswith("#"):
            nivel = min(len(s) - len(s.lstrip("#")) + 1, 4)
            out.append(f"<h{nivel}>{html.escape(s.lstrip('# '))}</h{nivel}>")
        elif s:
            out.append("<p>" + html.escape(s) + "</p>")
    if lista:
        out.append(f"</{lista}>")
    return "\n".join(out)


sesion = call("GET", "/initSession", headers={"Authorization": f"user_token {TOKEN}"})["session_token"]
H = {"Session-Token": sesion}
call("POST", "/changeActiveEntities", {"entities_id": "all", "is_recursive": True}, H)

for ruta in sorted(glob.glob("/tmp/guias/*.md")):
    md = open(ruta, encoding="utf-8").read()
    titulo = md.splitlines()[0].lstrip("# ").strip()
    r = call("POST", "/KnowbaseItem", {"input": {
        "name": "[EJEMPLO] " + titulo,
        "answer": md_a_html(md),
        "is_faq": 0, "entities_id": 0, "is_recursive": 1,
    }}, H)
    print("Guia", r["id"], titulo)
call("GET", "/killSession", None, H)
print("LISTO")
