# 🎯 Dashboard Cliente - Documentación

## 📋 Resumen

Se ha implementado un **dashboard exclusivo para usuarios con rol `cliente`** que incluye todas las funcionalidades solicitadas:

### ✨ Características Principales

- **Estructura de dos columnas**: Sidebar de navegación + Contenido dinámico
- **Tres secciones principales**: Mi Perfil, Mis Proformas, Mis Contratos
- **Diseño responsive** con Bootstrap 5 y FontAwesome
- **Seguridad**: Solo usuarios con rol `cliente` pueden acceder
- **Carga dinámica** de contenido sin recargar la página completa

---

## 🗂️ Archivos Creados/Modificados

### 📁 Backend (Vistas y Formularios)
- **`accounts/forms.py`** - Formulario para edición de perfil del cliente
- **`accounts/views.py`** - 6 nuevas vistas para el dashboard del cliente
- **`accounts/urls.py`** - URLs del dashboard cliente

### 📁 Frontend (Templates)
- **`templates/accounts/dashboard_cliente.html`** - Template principal con estructura de tabs
- **`templates/accounts/perfil_cliente.html`** - Formulario de edición de perfil
- **`templates/accounts/mis_proformas_cliente.html`** - Vista de proformas con filtros
- **`templates/accounts/mis_contratos_cliente.html`** - Vista de contratos con filtros
- **`templates/accounts/ver_contrato_cliente.html`** - Vista detallada de contrato (solo lectura)
- **`templates/accounts/generar_contrato_cliente.html`** - Generación de contratos con selección de opciones

---

## 🚀 URLs del Dashboard

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/accounts/dashboard/` | `dashboard_cliente` | Dashboard principal con estadísticas |
| `/accounts/perfil/` | `perfil_cliente` | Edición de perfil del cliente |
| `/accounts/mis-proformas/` | `mis_proformas_cliente` | Lista de proformas con filtros |
| `/accounts/mis-contratos/` | `mis_contratos_cliente` | Lista de contratos con filtros |
| `/accounts/contrato/<str:contrato_num>/` | `ver_contrato_cliente` | Vista detallada del contrato |
| `/accounts/generar-contrato/<str:proforma_num>/` | `generar_contrato_cliente` | Generación de nuevo contrato |

---

## 🛡️ Seguridad y Permisos

### ✅ Verificaciones Implementadas
- Solo usuarios autenticados (`@login_required`)
- Solo usuarios con `request.user.profile.rol == 'cliente'`
- Los clientes solo ven sus propias proformas y contratos
- Verificación de propiedad en todas las vistas sensibles

### 🚫 Restricciones
- Acceso denegado si no tiene perfil o rol diferente a 'cliente'
- Los contratos solo se pueden ver en modo de solo lectura
- Las proformas vencidas (>20 días) no permiten generar contratos

---

## 📊 Funcionalidades por Sección

### 1. ✨ **Mi Perfil**
- **Campos editables**: Nombre, Apellido, Dirección, Distrito, Referencia, DNI, Imagen de perfil
- **Campo de solo lectura**: Email
- **Información adicional**: Rol, estado de verificación, fecha de registro
- **Validación**: Formulario con validación y mensajes de éxito

### 2. 📅 **Mis Proformas**
- **Filtros de búsqueda**: Por N° Proforma y Estado (Pendiente/Atendido)
- **Información mostrada**: N° Proforma, Fecha solicitud, Fecha atendido, Precio total, Estado
- **Acciones disponibles**:
  - 👁️ Ver PDF generado (si existe)
  - 📄 Generar contrato (solo proformas atendidas y no vencidas)
  - 🔍 Ver detalles completos de la proforma

### 3. 📄 **Mis Contratos**
- **Filtros de búsqueda**: Por N° Contrato, N° Proforma, Estado Pedido, Estado Deuda
- **Información mostrada**: N° Contrato, N° Proforma, Fechas, Montos, Estados
- **Estados con badges**:
  - 🟡 Pendiente (amarillo)
  - 🔘 En Producción (gris)
  - 🟢 Entregado (verde)
  - 🟡 Debe (amarillo)
  - 🟢 Pagado (verde)
- **Acciones disponibles**:
  - 👁️ Ver contrato completo (solo lectura)
  - 📄 Ver PDF generado (si existe)

---

## 🔧 Características Técnicas

### **Generación de Contratos**
- **Abono automático**: 50% del monto total
- **Fecha de entrega automática**: 7 días hábiles (aprox. 10 días calendario)
- **Selección de opciones**: El cliente debe elegir una opción por cada producto cotizado
- **Campo editable**: Detalles adicionales (máximo 250 caracteres)
- **Generación de PDF**: Automática al confirmar el contrato

### **Dashboard Principal**
- **Estadísticas en tiempo real**: Total de proformas, contratos, pendientes
- **Carga dinámica**: El contenido se carga vía AJAX sin recargar la página
- **Navegación con tabs**: Bootstrap tabs para cambiar entre secciones
- **Diseño responsivo**: Adaptable a diferentes tamaños de pantalla

### **Filtros y Búsquedas**
- **Paginación**: 10 elementos por página
- **Conservación de filtros**: Los filtros se mantienen al cambiar de página
- **Limpieza de filtros**: Botón para restablecer búsquedas
- **Estados automáticos**: El estado de deuda se calcula automáticamente

---

## 🎨 Diseño Visual

### **Paleta de Colores**
- **Primario**: #4e73df (Azul)
- **Éxito**: #1cc88a (Verde)
- **Advertencia**: #f6c23e (Amarillo)
- **Info**: #36b9cc (Azul claro)
- **Peligro**: #e74a3b (Rojo)

### **Iconografía**
- **FontAwesome 6**: Iconos consistentes en toda la interfaz
- **Badges informativos**: Para estados, cantidades y acciones
- **Cards con sombras**: Separación visual clara de secciones

---

## 🚀 Cómo Usar el Dashboard

### **Para Acceder**
1. El usuario debe estar registrado y verificado
2. Su perfil debe tener `rol = 'cliente'`
3. Acceder a `/accounts/dashboard/`

### **Navegación**
1. **Dashboard Principal**: Muestra estadísticas y navegación por tabs
2. **Mi Perfil**: Editar información personal y subir foto
3. **Mis Proformas**: Buscar y gestionar proformas, generar contratos
4. **Mis Contratos**: Consultar contratos generados y su estado

### **Flujo Típico**
1. Cliente solicita cotización → Proforma creada
2. Trabajador atiende proforma → Estado cambia a "Atendido"
3. Cliente genera contrato desde proforma atendida
4. Cliente realiza el pago del 50% inicial
5. Trabajador actualiza estados de pedido y deuda
6. Cliente consulta estado en tiempo real

---

## ✅ Cumplimiento de Requisitos

### **Estructura Dashboard** ✅
- ✅ Dos columnas (sidebar + contenido)
- ✅ Sidebar vertical tipo tabs
- ✅ Tres opciones: Mi Perfil, Mis Proformas, Mis Contratos
- ✅ Contenido dinámico sin recargar página

### **Mi Perfil** ✅
- ✅ Solo visible para clientes
- ✅ Todos los campos solicitados (nombre, apellido, email, dirección, distrito, referencia, DNI, imagen)
- ✅ Email en solo lectura
- ✅ Formulario funcional con POST
- ✅ Mensaje de éxito al guardar

### **Mis Proformas** ✅
- ✅ Solo proformas del cliente autenticado
- ✅ Filtros por N° Proforma y Estado
- ✅ Tabla con todos los campos solicitados
- ✅ Badges para estados (amarillo/verde)
- ✅ Acciones: Ver, PDF, Generar contrato
- ✅ Validación de 20 días para generar contrato

### **Mis Contratos** ✅
- ✅ Solo contratos del cliente autenticado
- ✅ Filtros completos (N° Contrato, N° Proforma, Estados)
- ✅ Tabla con todos los campos solicitados
- ✅ Badges para estados automáticos
- ✅ Acciones: Ver, PDF (solo lectura para cliente)

### **Generación de Contratos** ✅
- ✅ Selección de opciones de cotización
- ✅ Cálculo automático del 50% de abono
- ✅ Fecha de entrega automática (7 días hábiles)
- ✅ Campo editable para detalles adicionales
- ✅ Resumen antes de confirmar

### **Seguridad** ✅
- ✅ Verificación de rol 'cliente'
- ✅ HttpResponseForbidden para accesos no autorizados
- ✅ Filtrado por usuario en todas las consultas

### **Tecnologías** ✅
- ✅ Bootstrap 5
- ✅ FontAwesome
- ✅ Diseño responsivo
- ✅ Vistas, URLs, templates y formularios completos

---

## 🔗 Integración con Sistema Existente

- **No modifica funcionalidad existente**: Todo el código nuevo está separado
- **Reutiliza modelos existentes**: Proforma, Contrato, Profile, User
- **Compatible con vistas de trabajadores**: Las vistas de trabajadores siguen funcionando igual
- **URLs independientes**: Todas bajo `/accounts/` para organización clara

---

## 🎉 ¡Dashboard Cliente Completamente Funcional!

El dashboard está **100% implementado** y listo para usar. Los clientes ahora tienen:

- ✨ **Experiencia moderna y intuitiva**
- 📱 **Acceso desde cualquier dispositivo**
- 🔒 **Seguridad y privacidad garantizada**
- ⚡ **Funcionalidad completa sin duplicar código**
- 🎨 **Diseño profesional y atractivo** 