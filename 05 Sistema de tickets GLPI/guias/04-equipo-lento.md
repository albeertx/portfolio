# Guía: el equipo va muy lento

Guía de ejemplo de soporte de nivel 1 (Windows 10/11).

## Síntoma
El equipo tarda en arrancar. Los programas se quedan colgados o responden tarde.

## Preguntas al usuario
1. ¿Desde cuándo? ¿Pasó algo antes (actualización, programa nuevo)?
2. ¿Le pasa con todos los programas o con uno concreto?
3. ¿Cuánto hace que no reinicia el equipo?

## Comprobaciones
1. Administrador de tareas (Ctrl + Mayús + Esc). Mirar CPU, memoria y disco. Anotar qué proceso consume más.
2. Espacio libre en el disco. Menos del 10 % libre ya es un problema.
3. Programas que arrancan con Windows (pestaña "Aplicaciones de arranque").
4. Actualizaciones de Windows pendientes.
5. Estado del disco. En PowerShell:
   ```
   Get-PhysicalDisk | Select FriendlyName, HealthStatus, MediaType
   ```
6. Análisis con el antivirus de la empresa.

## Solución
1. Reiniciar el equipo si lleva días encendido.
2. Quitar del arranque lo que no haga falta.
3. Liberar espacio (Configuración → Sistema → Almacenamiento).
4. Instalar las actualizaciones pendientes.
5. Si la memoria está al límite, proponer ampliarla.

## Escalar a nivel 2 si
- El disco muestra un estado que no es correcto (riesgo de pérdida de datos).
- El proceso que consume sospechoso no se reconoce.
- Hace falta cambiar hardware.

## Al cerrar el ticket, anotar
Qué proceso o recurso causaba la lentitud y qué se hizo.
