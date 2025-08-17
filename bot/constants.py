COMMAND_USE_GUIDES = {
    "SET_ROLE": "'/setrole [YOUR_ROLE]'\nExample: /setrole backend engineer\n",
    "SET_LOCATION": "'/setlocation [YOUR_LOCATION]'\nExample: /setlocation Argentina\n",
    "SET_STACK": "'/setstack [TECH_1,TECH_2, etc]'\nExample: /setstack python,nodejs\n",
    "MATCHES": "'/matches [optional: search query]'\nExample: /matches python\nExample: /matches remote\nExample: /matches startup\n",
}

MESSAGES = {
    "welcome": {
        "en": (
            "👋 **Welcome to AgarralapalaBot!**\n\n"
            "I’ll help you find tech jobs faster than a *Python script* 🐍.\n"
            "To get started, tell me your role and location.\n\n"
            "📌 *Useful commands:*\n"
            "- `/setrole <role>` → e.g. `/setrole Backend Developer`\n"
            "- `/setlocation <location>` → e.g. `/setlocation Buenos Aires`\n"
            "- `/matches [query]` → View your current job matches\n"
            "- `/matcheshelp` → Learn how to filter matches\n"
            "- `/myinfo` → View your current setup\n\n"
            "💡 *Tip:* The more specific you are, the better the matches I’ll send you."
        ),
        "es": (
            "👋 **¡Bienvenido a AgarralapalaBot!**\n\n"
            "Te ayudo a encontrar trabajos tech más rápido que un *script en Python* 🐍.\n"
            "Para comenzar, dime qué rol buscas y tu ubicación.\n\n"
            "📌 *Comandos útiles:*\n"
            "- `/setrole <rol>` → Ej: `/setrole Backend Developer`\n"
            "- `/setlocation <ubicación>` → Ej: `/setlocation Buenos Aires`\n"
            "- `/matches [consulta]` → Ver tus coincidencias de trabajo actuales\n"
            "- `/matcheshelp` → Aprende cómo filtrar coincidencias\n"
            "- `/myinfo` → Ver tu configuración actual\n\n"
            "💡 *Tip:* Cuanto más específico seas, mejor serán las coincidencias que te enviaré."
        )
    },

    "role_saved": {
        "en": (
            "✅ **Role updated**\n"
            "Your role is now set to: `{role}`\n\n"
            "Next, you can set your location with:\n"
            "`/setlocation <location>`\n\n"
            "💡 *Tip:* You can change your role anytime by running the command again."
        ),
        "es": (
            "✅ **Rol actualizado**\n"
            "Has configurado tu rol como: `{role}`\n\n"
            "Ahora puedes configurar tu ubicación con:\n"
            "`/setlocation <ubicación>`\n\n"
            "💡 *Tip:* Puedes cambiar tu rol en cualquier momento repitiendo el comando."
        )
    },

    "location_saved": {
        "en": (
            "📍 **Location updated**\n"
            "Your location is now set to: `{location}`\n\n"
            "I’ll now search jobs in that area.\n"
            "To change your role, use:\n"
            "`/setrole <role>`"
        ),
        "es": (
            "📍 **Ubicación actualizada**\n"
            "Has configurado tu ubicación como: `{location}`\n\n"
            "Ahora buscaré trabajos para ti en esa zona.\n"
            "Para cambiar tu rol usa:\n"
            "`/setrole <rol>`"
        )
    },

    "stack_saved": {
        "en": (
            "🛠 **Tech stack updated**\n"
            "Your preferred stack is now set to: `{stack}`\n\n"
            "💡 *Tip:* You can update your stack anytime by running the command again."
        ),
        "es": (
            "🛠 **Stack tecnológico actualizado**\n"
            "Has configurado tu stack preferido como: `{stack}`\n\n"
            "💡 *Tip:* Puedes actualizar tu stack en cualquier momento repitiendo el comando."
        )
    },

    "no_role_error": {
        "en": (
            "⚠️ **Role not set**\n"
            "I need to know your role before continuing.\n"
            "Use the command:\n"
            "`/setrole <role>`\n\n"
            "Example:\n"
            "`/setrole Backend Developer`"
        ),
        "es": (
            "⚠️ **Rol no configurado**\n"
            "Necesito saber tu rol antes de continuar.\n"
            "Usa el comando:\n"
            "`/setrole <rol>`\n\n"
            "Ejemplo:\n"
            "`/setrole Backend Developer`"
        )
    },

    "my_info": {
        "en": (
            "📝 **Your current setup**\n"
            "- Role: `{role}`\n"
            "- Location: `{location}`\n"
            "- Job alerts: {alerts_status}\n\n"
            "You can update any value with:\n"
            "- `/setrole`\n"
            "- `/setlocation`"
        ),
        "es": (
            "📝 **Tu configuración actual**\n"
            "- Rol: `{role}`\n"
            "- Ubicación: `{location}`\n"
            "- Alertas de empleo: {alerts_status}\n\n"
            "Puedes cambiar cualquier valor con:\n"
            "- `/setrole`\n"
            "- `/setlocation`"
        )
    },

    "job_found": {
        "en": (
            "💼 **New job found for you**\n\n"
            "**Title:** {title}\n"
            "**Company:** {company}\n"
            "**Location:** {location}\n"
            "**Salary:** {salary}\n"
            "**Link:** [View job]({link})\n\n"
            "📌 *Tip:* Reply with `/save` to add it to your saved list."
        ),
        "es": (
            "💼 **Nuevo trabajo encontrado para ti**\n\n"
            "**Título:** {title}\n"
            "**Empresa:** {company}\n"
            "**Ubicación:** {location}\n"
            "**Salario:** {salary}\n"
            "**Link:** [Ver oferta]({link})\n\n"
            "📌 *Tip:* Responde con `/guardar` para añadirlo a tu lista."
        )
    },

    "help": {
        "en": (
            "❓ **How to use AgarralapalaBot**\n\n"
            "Here are the main commands:\n"
            "- `/setrole <role>` → Set your desired job role.\n"
            "  e.g. `/setrole Backend Developer`\n"
            "- `/setlocation <location>` → Set your preferred location.\n"
            "  e.g. `/setlocation Buenos Aires`\n"
            "- `/matches [query]` → View your current job matches.\n"
            "  e.g. `/matches python` or `/matches remote`\n"
            "- `/matcheshelp` → Learn how to filter your matches.\n"
            "- `/myinfo` → View your current role, location, and alerts.\n"
            "- `/save` → Save a job I sent you.\n"
            "- `/help` → Show this help message.\n\n"
            "💡 *Tip:* The more specific your role and location, the better the job matches you'll get."
        ),
        "es": (
            "❓ **Cómo usar AgarralapalaBot**\n\n"
            "Estos son los comandos principales:\n"
            "- `/setrole <rol>` → Configura el rol que buscas.\n"
            "  Ej: `/setrole Backend Developer`\n"
            "- `/setlocation <ubicación>` → Configura tu ubicación preferida.\n"
            "  Ej: `/setlocation Buenos Aires`\n"
            "- `/matches [consulta]` → Ver tus coincidencias de trabajo actuales.\n"
            "  Ej: `/matches python` o `/matches remoto`\n"
            "- `/matcheshelp` → Aprende cómo filtrar tus coincidencias.\n"
            "- `/myinfo` → Ver tu rol, ubicación y alertas actuales.\n"
            "- `/guardar` → Guardar una oferta que te envié.\n"
            "- `/help` → Muestra este mensaje de ayuda.\n\n"
            "💡 *Tip:* Cuanto más específico seas con tu rol y ubicación, mejores serán las coincidencias."
        )
    },

    "candidate_not_found": {
        "en": (
            "❌ **Candidate not found**\n"
            "It seems you haven't set up your profile yet.\n"
            "Please use `/setrole` and `/setlocation` first to get started."
        ),
        "es": (
            "❌ **Candidato no encontrado**\n"
            "Parece que aún no has configurado tu perfil.\n"
            "Por favor usa `/setrole` y `/setlocation` primero para comenzar."
        )
    },

    "no_matches_found": {
        "en": (
            "🔍 **No matches found**\n"
            "We haven't found any job matches for you yet.\n"
            "Don't worry! We'll keep searching and notify you when we find something."
        ),
        "es": (
            "🔍 **No se encontraron coincidencias**\n"
            "Aún no hemos encontrado ofertas de trabajo que coincidan contigo.\n"
            "¡No te preocupes! Seguiremos buscando y te notificaremos cuando encontremos algo."
        )
    },

    "error_occurred": {
        "en": (
            "⚠️ **An error occurred**\n"
            "Sorry, something went wrong while fetching your matches.\n"
            "Please try again later or contact support if the problem persists."
        ),
        "es": (
            "⚠️ **Ocurrió un error**\n"
            "Lo sentimos, algo salió mal al buscar tus coincidencias.\n"
            "Por favor intenta de nuevo más tarde o contacta soporte si el problema persiste."
        )
    },

    "matches_filter_help": {
        "en": (
            "🔍 **Matches Filtering**\n\n"
            "You can filter your matches by searching across:\n"
            "• Job titles\n"
            "• Company names\n"
            "• Job descriptions\n"
            "• Tech stack requirements\n"
            "• Industry/company type\n\n"
            "Examples:\n"
            "• `/matches python` → Python jobs\n"
            "• `/matches remote` → Remote positions\n"
            "• `/matches startup` → Startup companies\n"
            "• `/matches backend` → Backend roles\n\n"
            "💡 *Tip:* Use `/matches` without a query to see all your matches."
        ),
        "es": (
            "🔍 **Filtrado de Coincidencias**\n\n"
            "Puedes filtrar tus coincidencias buscando en:\n"
            "• Títulos de trabajo\n"
            "• Nombres de empresas\n"
            "• Descripciones de trabajo\n"
            "• Requisitos de stack tecnológico\n"
            "• Industria/tipo de empresa\n\n"
            "Ejemplos:\n"
            "• `/matches python` → Trabajos con Python\n"
            "• `/matches remoto` → Posiciones remotas\n"
            "• `/matches startup` → Empresas startup\n"
            "• `/matches backend` → Roles de backend\n\n"
            "💡 *Tip:* Usa `/matches` sin consulta para ver todas tus coincidencias."
        )
    }
}