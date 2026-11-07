# Guía: la VPN no conecta

Guía de ejemplo de soporte de nivel 1 (usuario en remoto).

## Síntoma
El cliente VPN no conecta, o conecta y después no se accede a nada.

## Preguntas al usuario
1. ¿Qué mensaje de error sale exactamente? (Pedir captura.)
2. ¿Tiene internet? ¿Abre una página web?
3. ¿Desde dónde conecta? (Casa, wifi pública, móvil compartido.)
4. ¿Ha cambiado su contraseña hace poco?

## Comprobaciones
1. Hay internet. Desde el equipo:
   ```
   ping 8.8.8.8
   ping google.com
   ```
   Si el primero responde y el segundo no, es un problema de DNS.
2. La hora y la fecha del equipo son correctas. Una hora mal puesta rompe la autenticación.
3. La cuenta no está bloqueada ni caducada.
4. El cliente VPN está actualizado.
5. Otra red. Probar con los datos del móvil. Algunas redes bloquean la VPN.

## Solución
- Credenciales: restablecer o desbloquear la cuenta y probar de nuevo.
- Cliente: cerrar, abrir de nuevo y, si no funciona, reinstalarlo.
- Red: cambiar de red o reiniciar el router.
- Si conecta pero no abre recursos internos, revisar el DNS del adaptador de la VPN.

## Escalar a nivel 2 si
- Varios usuarios fallan a la vez (puede ser el servidor VPN).
- El error indica certificado caducado o rechazo del servidor.

## Al cerrar el ticket, anotar
Mensaje de error, causa y cómo se resolvió.
