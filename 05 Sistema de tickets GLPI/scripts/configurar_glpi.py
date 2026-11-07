#!/usr/bin/env python3
"""Crea entidades, categorias, usuarios y tickets de EJEMPLO en GLPI usando su API.

Se ejecuta dentro de la VM. Lee el token de /root/.glpi_api_token.
Todos los datos son ficticios. No se crean contrasenas.
"""
import json
import sys
import urllib.request

BASE = "http://localhost/apirest.php"
TOKEN = open("/root/.glpi_api_token").read().strip()
SESSION = None


def call(method, path, body=None, headers=None):
    h = {"Content-Type": "application/json"}
    if SESSION:
        h["Session-Token"] = SESSION
    if headers:
        h.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            txt = r.read().decode()
    except urllib.error.HTTPError as e:
        print("ERROR", method, path, e.code, e.read().decode()[:300])
        sys.exit(1)
    return json.loads(txt) if txt else None


def add(_tipo, **fields):
    r = call("POST", f"/{_tipo}", {"input": fields})
    return r["id"]


def search_id(itemtype, name, field="name"):
    r = call("GET", f"/{itemtype}?range=0-200&searchText[{field}]={name}")
    for item in r:
        if item.get(field) == name:
            return item["id"]
    return None


SESSION = call("GET", "/initSession", headers={"Authorization": f"user_token {TOKEN}"})["session_token"]
call("POST", "/changeActiveEntities", {"entities_id": "all", "is_recursive": True})

EJ = "Dato de ejemplo para el portfolio. No es real."

# --- Entidades ---------------------------------------------------------
ent = {}
def refrescar_entidades():
    # Hay que refrescar las entidades activas tras crear una, o la sesion no la ve.
    call("POST", "/changeActiveEntities", {"entities_id": "all", "is_recursive": True})


ent["demo"] = add("Entity", name="Empresa Demo", entities_id=0, comment=EJ)
refrescar_entidades()
ent["madrid"] = add("Entity", name="Sede Madrid", entities_id=ent["demo"], comment=EJ)
refrescar_entidades()
ent["barcelona"] = add("Entity", name="Sede Barcelona", entities_id=ent["demo"], comment=EJ)
refrescar_entidades()
print("Entidades:", ent)

# --- Categorias --------------------------------------------------------
cats = {}
for nombre in ["Hardware", "Software", "Red y VPN", "Cuentas y accesos", "Impresoras", "Correo"]:
    cats[nombre] = add(
        "ITILCategory", name=nombre, entities_id=0, is_recursive=1,
        is_helpdeskvisible=1, is_incident=1, is_request=1, comment="Categoria de ejemplo.",
    )
print("Categorias:", cats)

# --- Usuarios ficticios (sin contrasena: no pueden iniciar sesion) -----
usuarios = [
    ("ana.garcia", "Ana", "Garcia", "Self-Service", "madrid"),
    ("marta.ruiz", "Marta", "Ruiz", "Self-Service", "madrid"),
    ("luis.martin", "Luis", "Martin", "Self-Service", "barcelona"),
    ("tecnico.n1", "Tecnico", "Nivel 1", "Hotliner", "demo"),
    ("tecnico.n2", "Tecnico", "Nivel 2", "Technician", "demo"),
]
uid = {}
for login, nombre, apellido, perfil, sede in usuarios:
    uid[login] = add(
        "User", name=login, firstname=nombre, realname=apellido,
        entities_id=ent[sede], comment=EJ, is_active=1,
    )
    pid = search_id("Profile", perfil)
    if pid is None:
        print("Perfil no encontrado:", perfil)
        sys.exit(1)
    add("Profile_User", users_id=uid[login], profiles_id=pid, entities_id=ent[sede], is_recursive=1)
print("Usuarios:", uid)

# --- Tickets de ejemplo ------------------------------------------------
# tipo 1 = incidencia, 2 = peticion. urgencia/impacto 1..5.
tickets = [
    dict(t="[EJEMPLO] La impresora de la planta 2 no imprime", cat="Impresoras", tipo=1, sede="madrid",
         req="ana.garcia", urg=3, estado="resuelto",
         desc="Ticket de ejemplo. El usuario envia documentos a la impresora de la planta 2 y se quedan en cola.",
         seg="Se comprueba que la impresora esta encendida y con red. La cola de impresion estaba bloqueada.",
         sol="Se reinicia el servicio de cola de impresion del equipo y se vacia la cola. Imprime con normalidad."),
    dict(t="[EJEMPLO] La VPN no conecta desde casa", cat="Red y VPN", tipo=1, sede="barcelona",
         req="luis.martin", urg=4, estado="en curso",
         desc="Ticket de ejemplo. Al conectar a la VPN desde casa sale un error de autenticacion.",
         seg="Se confirma que el usuario tiene internet y que la cuenta no esta bloqueada. Pendiente de revisar el cliente VPN."),
    dict(t="[EJEMPLO] Contrasena olvidada de un usuario", cat="Cuentas y accesos", tipo=1, sede="madrid",
         req="marta.ruiz", urg=3, estado="cerrado",
         desc="Ticket de ejemplo. El usuario no recuerda su contrasena y no puede entrar en el equipo.",
         seg="Se verifica la identidad del usuario por una via alternativa antes de restablecer.",
         sol="Se restablece la contrasena con cambio obligatorio en el siguiente inicio de sesion."),
    dict(t="[EJEMPLO] El portatil va muy lento", cat="Hardware", tipo=1, sede="madrid",
         req="ana.garcia", urg=2, estado="pendiente",
         desc="Ticket de ejemplo. El portatil tarda varios minutos en arrancar y las aplicaciones se quedan colgadas.",
         seg="Se revisa el uso de disco y memoria. Se pide al usuario una ventana para ampliar la memoria."),
    dict(t="[EJEMPLO] Solicitud de alta de usuario nuevo", cat="Cuentas y accesos", tipo=2, sede="barcelona",
         req="luis.martin", urg=3, estado="asignado",
         desc="Ticket de ejemplo. Se solicita crear la cuenta y el correo de una persona que se incorpora el lunes."),
    dict(t="[EJEMPLO] No llega el correo a la cuenta compartida", cat="Correo", tipo=1, sede="madrid",
         req="marta.ruiz", urg=3, estado="nuevo",
         desc="Ticket de ejemplo. Los mensajes enviados a la cuenta compartida de administracion no llegan."),
    dict(t="[EJEMPLO] Monitor sin senal en un puesto", cat="Hardware", tipo=1, sede="barcelona",
         req="luis.martin", urg=2, estado="resuelto",
         desc="Ticket de ejemplo. El monitor del puesto 14 muestra 'sin senal' al arrancar el equipo.",
         seg="Se revisan cables y entradas del monitor.",
         sol="El cable de video estaba mal conectado. Se reconecta y se fija. Funciona."),
    dict(t="[EJEMPLO] Solicitud de instalacion de un programa", cat="Software", tipo=2, sede="madrid",
         req="ana.garcia", urg=2, estado="en curso",
         desc="Ticket de ejemplo. Se pide instalar un programa de edicion de PDF en el equipo del usuario.",
         seg="Se pide la aprobacion del responsable antes de instalar."),
]
ESTADO = {"nuevo": 1, "en curso": 2, "asignado": 2, "pendiente": 4, "resuelto": 5, "cerrado": 6}

for tk in tickets:
    t_id = add(
        "Ticket", name=tk["t"], content=tk["desc"], entities_id=ent[tk["sede"]],
        itilcategories_id=cats[tk["cat"]], type=tk["tipo"],
        urgency=tk["urg"], impact=tk["urg"], priority=tk["urg"],
        _users_id_requester=uid[tk["req"]],
    )
    if tk["estado"] not in ("nuevo",):
        call("POST", "/Ticket_User", {"input": {"tickets_id": t_id, "users_id": uid["tecnico.n1"], "type": 2}})
    if "seg" in tk:
        add("ITILFollowup", itemtype="Ticket", items_id=t_id, content=tk["seg"], users_id=uid["tecnico.n1"])
    if "sol" in tk:
        add("ITILSolution", itemtype="Ticket", items_id=t_id, content=tk["sol"], solutiontypes_id=0)
    if tk["estado"] == "pendiente":
        call("PUT", f"/Ticket/{t_id}", {"input": {"status": 4}})
    if tk["estado"] == "cerrado":
        call("PUT", f"/Ticket/{t_id}", {"input": {"status": 6}})
    print("Ticket", t_id, tk["estado"], tk["t"])

call("GET", "/killSession")
print("LISTO")
