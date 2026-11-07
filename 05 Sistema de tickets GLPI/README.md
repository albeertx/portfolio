# Sistema de tickets de soporte con GLPI

Proyecto de Help Desk: un sistema de tickets GLPI montado desde cero en una máquina virtual Ubuntu, con entidades, categorías, usuarios, tickets de ejemplo y guías de resolución de problemas.

**Estado:** montado y probado en local. Sin coste (0 €). La máquina virtual no está publicada en internet, así que no hay enlace al sistema. Quedan aquí los pasos, las capturas y las guías.

**Ver la página en vivo:** https://albeertx.github.io/portfolio/05%20Sistema%20de%20tickets%20GLPI/web/

El código de la página está en [web/index.html](web/index.html).

> **Todos los datos son de ejemplo.** Las entidades, los usuarios y los 8 tickets son ficticios y llevan la marca "[EJEMPLO]". No hay datos reales ni contraseñas en este repositorio.

## Qué hice

- Creé una **máquina virtual** con VirtualBox 7.2.22: 2 GB de RAM, 1 CPU y 20 GB de disco.
- Instalé **Ubuntu Server 26.04.1 LTS** y activé SSH.
- Instalé **Apache 2.4.66**, **MariaDB 11.8.6** y **PHP 8.5.4** con las extensiones que pide GLPI.
- Descargué e instalé **GLPI 12.0.1**, con Apache apuntando a su carpeta `public/`.
- Creé una base de datos propia y un usuario de base de datos solo para GLPI.
- Cambié la contraseña del administrador y **desactivé las cuentas por defecto** (`tech`, `normal` y `post-only`).
- Configuré **3 entidades**, **6 categorías**, **5 usuarios ficticios** y asigné perfiles.
- Creé **8 tickets de ejemplo** en distintos estados.
- Escribí **4 guías** de resolución de problemas y las subí a la base de conocimiento de GLPI.

## Cómo está montado

| Pieza | Detalle |
|---|---|
| Máquina virtual | VirtualBox, red NAT con reenvío del puerto 8080 del PC al 80 de la VM |
| Sistema | Ubuntu Server 26.04.1 LTS |
| Servidor web | Apache 2.4.66 con `mod_rewrite` |
| Base de datos | MariaDB 11.8.6 |
| Lenguaje | PHP 8.5.4 |
| Aplicación | GLPI 12.0.1 |

## Organización de GLPI

**Entidades** (todas de ejemplo): Empresa Demo, con dos sedes: Sede Madrid y Sede Barcelona.

**Categorías:** Hardware, Software, Red y VPN, Cuentas y accesos, Impresoras y Correo.

**Usuarios ficticios** (sin contraseña, no pueden iniciar sesión):

| Usuario | Perfil | Entidad |
|---|---|---|
| ana.garcia | Self-Service | Sede Madrid |
| marta.ruiz | Self-Service | Sede Madrid |
| luis.martin | Self-Service | Sede Barcelona |
| tecnico.n1 | Hotliner (técnico de nivel 1) | Empresa Demo |
| tecnico.n2 | Technician (técnico de nivel 2) | Empresa Demo |

Uso los **perfiles que trae GLPI**. No he creado perfiles propios.

## Tickets de ejemplo

| # | Título | Categoría | Sede | Estado |
|---|---|---|---|---|
| 2 | La impresora de la planta 2 no imprime | Impresoras | Madrid | Resuelto |
| 3 | La VPN no conecta desde casa | Red y VPN | Barcelona | En curso |
| 4 | Contraseña olvidada de un usuario | Cuentas y accesos | Madrid | Cerrado |
| 5 | El portátil va muy lento | Hardware | Madrid | En espera |
| 6 | Solicitud de alta de usuario nuevo | Cuentas y accesos | Barcelona | En curso (asignado) |
| 7 | No llega el correo a la cuenta compartida | Correo | Madrid | Nuevo |
| 8 | Monitor sin señal en un puesto | Hardware | Barcelona | Resuelto |
| 9 | Solicitud de instalación de un programa | Software | Madrid | En curso (asignado) |

Los tickets los creé con la API de GLPI y el script [scripts/configurar_glpi.py](scripts/configurar_glpi.py). Por eso todos tienen la misma fecha de creación. Es un dato de ejemplo, no un histórico real.

## Guías de resolución de problemas

Cada guía tiene: síntoma, preguntas al usuario, comprobaciones, solución, cuándo escalar y qué anotar al cerrar.

- [La impresora no imprime](guias/01-impresora-no-imprime.md)
- [La VPN no conecta](guias/02-vpn-no-conecta.md)
- [Contraseña olvidada o cuenta bloqueada](guias/03-contrasena-olvidada.md)
- [El equipo va muy lento](guias/04-equipo-lento.md)

Las 4 están también en la base de conocimiento de GLPI (script [scripts/subir_guias.py](scripts/subir_guias.py)).

## Comandos principales

Instalar los paquetes:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y apache2 mariadb-server php libapache2-mod-php php-mysql php-curl php-gd \
  php-intl php-mbstring php-xml php-bcmath php-zip php-bz2 php-ldap php-apcu php-cli curl tar
```

Descargar GLPI y dejarlo en `/var/www` (las carpetas `config`, `files` y `marketplace` pertenecen a `www-data`):

```bash
curl -sSL -o glpi.tgz https://github.com/glpi-project/glpi/releases/download/12.0.1/glpi-12.0.1.tgz
sudo tar -xzf glpi.tgz -C /var/www/
sudo chown -R www-data:www-data /var/www/glpi/config /var/www/glpi/files /var/www/glpi/marketplace
```

Apache: `DocumentRoot` en `/var/www/glpi/public`, con `mod_rewrite` activado:

```bash
sudo a2enmod rewrite
sudo a2ensite glpi
sudo apachectl configtest && sudo systemctl reload apache2
```

Base de datos (la contraseña la elijo yo y no se guarda en el repositorio):

```sql
CREATE DATABASE glpi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'glpi'@'localhost' IDENTIFIED BY '********';
GRANT ALL PRIVILEGES ON glpi.* TO 'glpi'@'localhost';
```

Instalar GLPI desde la consola:

```bash
cd /var/www/glpi
sudo -u www-data php bin/console db:install --db-host=localhost --db-name=glpi \
  --db-user=glpi --db-password='********' --default-language=es_ES --no-interaction
```

Cuentas por defecto: cambiar la del administrador y desactivar las demás:

```bash
sudo -u www-data php bin/console user:reset_password glpi
sudo -u www-data php bin/console user:disable tech
sudo -u www-data php bin/console user:disable normal
sudo -u www-data php bin/console user:disable post-only
```

## Problema real: la VM se colgaba

Con 2 CPU, Ubuntu arrancaba y después se bloqueaba (`watchdog: BUG: soft lockup - CPU#0 stuck`). Windows ya tiene activo su hipervisor y VirtualBox va por encima, lo que afecta al reloj de la VM. La solución fue dejar **1 CPU**, activar el reloj `hpet` y el proveedor de paravirtualización `kvm`. Después el instalador y GLPI funcionaron sin problemas.

## Capturas

En la carpeta [capturas](capturas):

- [01-instalador-ubuntu-idioma.png](capturas/01-instalador-ubuntu-idioma.png): instalador de Ubuntu Server.
- [02-instalacion-ubuntu-completa.png](capturas/02-instalacion-ubuntu-completa.png): instalación completada.
- [03-glpi-login.png](capturas/03-glpi-login.png): pantalla de acceso de GLPI.
- [04-lista-tickets.png](capturas/04-lista-tickets.png): los 8 tickets de ejemplo.
- [05-ticket-impresora-resuelto.png](capturas/05-ticket-impresora-resuelto.png): ticket resuelto, con su seguimiento y solución.
- [06-ticket-vpn-en-curso.png](capturas/06-ticket-vpn-en-curso.png): ticket en curso.
- [07-entidades.png](capturas/07-entidades.png): entidades.
- [08-categorias.png](capturas/08-categorias.png): categorías.
- [09-usuarios.png](capturas/09-usuarios.png): usuarios.
- [10-base-conocimiento.png](capturas/10-base-conocimiento.png): las 4 guías en la base de conocimiento.

Las capturas de GLPI las hice con Edge sobre `localhost`. No se ven contraseñas.

## Seguridad

- No hay contraseñas, claves ni tokens en el repositorio.
- Las cuentas por defecto de GLPI están cambiadas o desactivadas.
- Los usuarios ficticios no tienen contraseña.
- La máquina virtual solo es accesible desde mi PC.
- Para configurar activé la API de GLPI con una clave temporal. La desactivé y la borré al terminar.

## Qué mejoraría

- Crear perfiles propios (técnico de nivel 1 y nivel 2) con permisos ajustados.
- Configurar notificaciones por correo y un acuerdo de nivel de servicio (SLA).
- Añadir el inventario de equipos con el agente de GLPI.
- Cifrar el acceso con HTTPS (certificado) si el sistema se publicara.
- Copias de seguridad automáticas de la base de datos.

## Coste

0 €. Todo corre en local en mi PC, con software libre.
