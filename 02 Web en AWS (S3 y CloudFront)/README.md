# Web en AWS (S3 y CloudFront)

Proyecto de cloud: mi presentación profesional alojada en AWS.

**En vivo:** https://dqy9jq042m8oh.cloudfront.net

## Cómo funciona

```
Visitante  ──HTTPS──▶  CloudFront  ──OAC──▶  S3 (privado)
```

- Los archivos están en un bucket de **Amazon S3**, en la región `eu-west-1` (Irlanda).
- El bucket es **privado**: el acceso público está bloqueado.
- **CloudFront** es la única puerta de entrada y da HTTPS.
- CloudFront lee el bucket con un **control de acceso de origen (OAC)**.
- Una **alerta de presupuesto de gasto cero** avisa por correo si hay cargos.

## Servicios

| Servicio | Para qué |
|---|---|
| Amazon S3 | Guardar la presentación |
| CloudFront | Servirla por HTTPS y con caché |
| Política de bucket | Dejar entrar solo a CloudFront |
| AWS Budgets | Alerta de gasto cero |

## Decisiones

- WAF desactivado: tiene coste fijo mensual y no hace falta para una página estática.
- Bucket sin versiones ni bloqueo de objetos: así se puede borrar todo fácilmente.
- Objeto raíz de CloudFront: la presentación, para que la dirección principal la abra directamente.

## Capturas

En la carpeta [capturas](capturas):

- [bucket-privado.png](capturas/bucket-privado.png): el bucket de S3 con "Bloquear todo el acceso público" activado.
- [cloudfront-origen-oac.png](capturas/cloudfront-origen-oac.png): el origen de CloudFront (el bucket de S3) con su control de acceso de origen (OAC).
- [web-publicada-https.png](capturas/web-publicada-https.png): la presentación abierta desde la dirección de CloudFront, por HTTPS.

Mi ID de cuenta de AWS no sale en ninguna captura: están recortadas a propósito.

## Cómo borrar todo

1. CloudFront: desactivar la distribución y, cuando termine, borrarla.
2. S3: vaciar el bucket y borrarlo.
