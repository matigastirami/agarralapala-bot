COMMAND_USE_GUIDES = {
    "SET_ROLE": "'/setrole [YOUR_ROLE]'\nExample: /setrole backend engineer\n",
    "SET_LOCATION": "'/setlocation [YOUR_LOCATION]'\nExample: /setlocation Argentina\n",
    "SET_STACK": "'/setstack [TECH_1,TECH_2, etc]'\nExample: /setstack python,nodejs\n",
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
            "- `/myinfo` → Ver tu rol, ubicación y alertas actuales.\n"
            "- `/guardar` → Guardar una oferta que te envié.\n"
            "- `/help` → Muestra este mensaje de ayuda.\n\n"
            "💡 *Tip:* Cuanto más específico seas con tu rol y ubicación, mejores serán las coincidencias."
        )
    }
}