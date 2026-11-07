# Publicación automática con GitHub Actions

Proyecto cloud: al subir un cambio al repositorio, la presentación se copia sola a S3 y se vacía la caché de CloudFront. Sin entrar a la consola de AWS y sin guardar claves.

**Estado:** terminado y probado. Un push a `main` publica la presentación en S3 y vacía la caché de CloudFront en unos 10 segundos. Comprobado: el HTML servido por CloudFront es idéntico al del repositorio.

## Cómo funciona

1. Subo un cambio a la rama `main` de GitHub.
2. GitHub Actions lanza el workflow `.github/workflows/deploy.yml`.
3. El workflow pide a AWS un permiso temporal (OIDC). No hay claves guardadas.
4. Copia `Presentacion Alberto Cuesta.html` al bucket de S3 con el nombre `Presentacion-Alberto-Cuesta.html`.
5. Vacía la caché de CloudFront (`/*`) para que el cambio se vea al momento.

## Por qué OIDC y no un usuario con claves

| | OIDC (elegido) | Usuario IAM con claves |
|---|---|---|
| Claves guardadas en GitHub | Ninguna | Dos secretos |
| Si algo se filtra | No hay nada que robar | Hay que borrar y rotar la clave |
| Caducidad | No caduca | Hay que rotarla |

## Qué hice en AWS

- Creé el **proveedor de identidad OIDC** `token.actions.githubusercontent.com` (audiencia `sts.amazonaws.com`).
- Creé la política `deploy-web-cloud` con permisos mínimos:
  - `s3:ListBucket` y `s3:GetBucketLocation` sobre el bucket.
  - `s3:PutObject` sobre los objetos del bucket.
  - `cloudfront:CreateInvalidation` sobre una sola distribución.
- Creé el rol `github-deploy-web-cloud` con esa política. Su confianza solo acepta mi repositorio `albeertx/portfolio` y la rama `main` (el `sub` lleva los IDs numéricos de usuario y repositorio, ver más abajo):

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:albeertx@<ID usuario>/portfolio@<ID repo>:ref:refs/heads/main"
  }
}
```

## El workflow

Los pasos del workflow:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: eu-west-1

- run: |
    aws s3 cp "01 Presentacion/Presentacion Alberto Cuesta.html" \
      "s3://${{ secrets.S3_BUCKET }}/Presentacion-Alberto-Cuesta.html" \
      --content-type "text/html; charset=utf-8"

- run: |
    aws cloudfront create-invalidation \
      --distribution-id "${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}" \
      --paths "/*"
```

Las rutas con espacios van entre comillas. En S3 el archivo se llama con guiones, porque es el objeto raíz de CloudFront.

## Secretos en GitHub

`AWS_ROLE_ARN`, `S3_BUCKET` y `CLOUDFRONT_DISTRIBUTION_ID`. No son claves de acceso, pero van como secretos para no escribirlos en el código.

## Problema que encontré y cómo lo resolví

La primera ejecución falló con `Not authorized to perform sts:AssumeRoleWithWebIdentity`. El rol esperaba este `sub`:

`repo:albeertx/portfolio:ref:refs/heads/main`

Subí un paso temporal al workflow que imprimía solo el `sub` del token (sin el token). GitHub lo enviaba con los IDs numéricos de usuario y repositorio:

`repo:albeertx@<ID usuario>/portfolio@<ID repo>:ref:refs/heads/main`

Actualicé la confianza del rol con ese valor exacto y quité el paso temporal. La segunda ejecución terminó bien. Con los IDs, otro repositorio con el mismo nombre no podría usar el rol.

## Comprobación

| Prueba | Resultado |
|---|---|
| Workflow tras el cambio de confianza | Correcto en 10 s: conectar con AWS, subir a S3 y vaciar caché |
| HTML servido por CloudFront frente al del repositorio | Idéntico |
| Antes del cambio de confianza | Falló al asumir el rol; no se tocó S3 |

## Pendiente

- Capturas del workflow en verde y del rol (con el ID de cuenta tapado).

## Seguridad

- No hay claves de AWS en ningún sitio.
- El ID de cuenta de AWS no se publica en este repositorio.
- Permisos mínimos y rol limitado a un repositorio y una rama.

## Coste

0 €. GitHub Actions es gratis para este uso, y IAM y OIDC no cuestan.
