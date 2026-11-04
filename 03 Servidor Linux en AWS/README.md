# Servidor Linux en AWS (EC2, nginx y firewall)

Proyecto de sistemas: un servidor Ubuntu en la nube con servidor web, firewall y acceso seguro por clave.

**Estado:** terminado y documentado. Para no generar gasto, la instancia y la distribución de CloudFront se eliminaron al acabar, así que la dirección del servidor ya no está activa. Quedan aquí los comandos, las pruebas y las capturas.

La página que servía el servidor está en [web/index.html](web/index.html).

## Qué hice

- Lancé una instancia **EC2** `t3.micro` con **Ubuntu Server 26.04 LTS** en la región `eu-west-1` (Irlanda).
- Configuré el **grupo de seguridad** de AWS: SSH (22) solo desde mi IP y HTTP (80) abierto. HTTPS cerrado.
- Entré por **SSH con par de claves** (`.pem`) desde PowerShell.
- Instalé **nginx** y comprobé que sirve la página.
- Activé el firewall del propio servidor, **UFW**: primero permití SSH y HTTP, después lo encendí.
- Creé un usuario **sin permisos de administrador** (`alberto`) que entra con la misma clave.
- Comprobé que el SSH **no admite contraseña** y que root no puede entrar con contraseña.
- Instalé las actualizaciones pendientes, incluidas las de seguridad.
- Cambié la página de bienvenida de nginx por una propia.
- Puse **CloudFront** por delante del servidor para servir la web por **HTTPS** con el certificado de `*.cloudfront.net`, sin comprar dominio. El HTTP se redirige solo a HTTPS.

## Comandos

Conectar (desde PowerShell, con la clave protegida):

```powershell
icacls "clave-servidor-linux.pem" /inheritance:r /grant:r "$($env:USERNAME):R"
ssh -i "clave-servidor-linux.pem" ubuntu@IP_PUBLICA
```

Servidor web:

```bash
sudo apt update && sudo apt install -y nginx
systemctl status nginx --no-pager | head -5
```

Firewall (el orden importa: primero SSH, después encender):

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
sudo ufw --force enable
sudo ufw status verbose
```

Usuario sin permisos de administrador:

```bash
sudo adduser --disabled-password --gecos "" alberto
sudo mkdir -p /home/alberto/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/alberto/.ssh/authorized_keys
sudo chown -R alberto:alberto /home/alberto/.ssh
sudo chmod 700 /home/alberto/.ssh && sudo chmod 600 /home/alberto/.ssh/authorized_keys
```

Comprobar el SSH:

```bash
sudo sshd -T | grep -E "^(passwordauthentication|permitrootlogin|pubkeyauthentication)"
```

Resultado: `passwordauthentication no`, `pubkeyauthentication yes`, `permitrootlogin prohibit-password`.

Actualizar:

```bash
sudo apt upgrade -y
```

## Comprobaciones

| Prueba | Resultado |
|---|---|
| Entrar como `alberto` por SSH con la clave | Funciona |
| `sudo ls` como `alberto` | Denegado: no está en sudoers |
| `http://IP_PUBLICA` desde fuera | Responde 200 con mi página |
| HTTPS (443) directo al servidor | Cerrado, como estaba previsto |
| `https://` por CloudFront | Responde 200 con candado; HTTP redirige a HTTPS (301) |

## HTTPS con CloudFront

El servidor solo escucha en el puerto 80. CloudFront recibe las visitas por HTTPS y pide la página al servidor por HTTP.

- Origen: el DNS público de la instancia, protocolo HTTP, puerto 80.
- WAF desactivado: tiene coste fijo y no hace falta aquí.
- Limitación conocida: el tramo entre CloudFront y el servidor no va cifrado. Para cifrarlo haría falta un dominio propio y un certificado en el servidor (por ejemplo Let's Encrypt).

## Capturas

En la carpeta [capturas](capturas):

- [grupo-seguridad.png](capturas/grupo-seguridad.png): reglas de entrada de AWS. Mi IP está tapada a propósito.
- [pagina-https.png](capturas/pagina-https.png): la página abierta por HTTPS.
- [salida-servidor.txt](capturas/salida-servidor.txt): salida real de los comandos en el servidor: versión de Ubuntu, estado de nginx, UFW, configuración del SSH y el usuario `alberto`.
- [prueba-sudo-alberto.txt](capturas/prueba-sudo-alberto.txt): `alberto` entra por SSH y `sudo` se lo deniega.

Las pruebas del servidor están en texto, no en imagen, porque son la salida literal de los comandos.

## Seguridad

- La clave `.pem` no se sube nunca al repositorio.
- Sin contraseñas: solo acceso por clave.
- Principio de mínimo privilegio: el usuario diario no es administrador.

## Coste y cierre

Entra en el plan gratuito de AWS con créditos. Al terminar, la instancia se termina para que no genere gasto.
