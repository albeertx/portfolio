# Guía: la impresora no imprime

Guía de ejemplo de soporte de nivel 1 (Windows 10/11, impresora de red).

## Síntoma
El usuario envía un documento y no sale. Se queda en la cola o da error.

## Preguntas al usuario
1. ¿Imprime algún otro equipo en esa impresora?
2. ¿Qué mensaje sale en la impresora o en el equipo?
3. ¿Ha funcionado antes? ¿Qué cambió?

## Comprobaciones
1. La impresora está encendida, con papel y sin avisos en su pantalla.
2. La impresora responde en red. Desde el equipo:
   ```
   ping IP_DE_LA_IMPRESORA
   ```
3. Es la impresora predeterminada y no está en "Usar impresora sin conexión".
4. Hay trabajos atascados en la cola (Configuración → Impresoras y escáneres → Abrir cola).

## Solución
1. Cancelar todos los trabajos de la cola.
2. Si no se pueden cancelar, reiniciar el servicio de cola. En PowerShell como administrador:
   ```
   Restart-Service Spooler
   ```
3. Imprimir una página de prueba.
4. Si sigue sin funcionar, quitar la impresora y volver a añadirla. Si hace falta, reinstalar el controlador.

## Escalar a nivel 2 si
- La impresora no responde al `ping` en ningún equipo (red o impresora).
- Falla el controlador en varios equipos.
- La impresora da un error de hardware.

## Al cerrar el ticket, anotar
Causa, qué se hizo y si imprime una página de prueba.
