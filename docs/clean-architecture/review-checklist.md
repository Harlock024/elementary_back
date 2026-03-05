## Checklist de revisión arquitectónica

- [ ] La lógica de negocio del workflow vive en `application/use_cases`.
- [ ] `domain` no importa Django, DRF ni modelos ORM.
- [ ] Las vistas HTTP delegan en un caso de uso (sin orquestación de negocio compleja).
- [ ] El acceso a datos se realiza por un adaptador de `infrastructure` que implementa un puerto.
- [ ] El endpoint mantiene ruta, método y formato de respuesta esperado.
- [ ] Existen pruebas unitarias de caso de uso y pruebas de endpoint para el workflow migrado.
- [ ] Se removió lógica duplicada legado del workflow migrado.
