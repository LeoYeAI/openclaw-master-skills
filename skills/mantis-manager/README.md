# Mantis BT Manager - OpenClaw Skill

Un skill OpenClaw complet pour gérer Mantis Bug Tracker via son API REST officielle.

## 🚀 Installation et Configuration

### Variables d'Environnement Requises

```bash
MANTIS_BASE_URL=https://your-mantis-instance.com/api/rest
MANTIS_API_TOKEN=your_api_token_here
```

### Génération du Token API

1. Connectez-vous à votre instance Mantis BT
2. Allez dans **Mon Compte** → **Tokens API**
3. Cliquez sur **Créer un Token API**
4. Copiez le token généré dans votre variable d'environnement

## 📖 Guide de Démarrage Rapide

### Exemple 1 : Lister tous les tickets
```
User: "Liste tous les tickets"
→ GET /issues
```

### Exemple 2 : Créer un ticket
```
User: "Crée un ticket avec le titre 'Bug de connexion' et la description 'Impossible de se connecter'"
→ POST /issues
{
  "summary": "Bug de connexion",
  "description": "Impossible de se connecter",
  "project": {"id": 1},
  "category": {"name": "General"}
}
```

### Exemple 3 : Lister les projets
```
User: "Affiche tous les projets"
→ GET /projects
```

## 🔄 Gestion Multi-Instances

### Basculer Entre Instances

Ce skill supporte **plusieurs instances Mantis** grâce à un système de résolution contextuelle.

#### Utilisation Temporaire (Une Seule Opération)
```
User: "Utilise https://staging.mantis.com/api/rest pour cette requête"
→ Set temporary_base_url = "https://staging.mantis.com/api/rest"
→ Perform operation
→ Clear temporary_base_url
```

#### Utilisation Session (Plusieurs Opérations)
```
User: "Connecte-toi à l'instance du client ABC"
→ Set user_base_url = "https://client-abc.mantis.com/api/rest"
→ Set user_token = "client_abc_token"
→ All subsequent operations use this instance
```

#### Retour aux Valeurs Par Défaut
```
User: "Reviens à l'instance par défaut"
→ Clear user_base_url
→ Clear user_token
```

### Ordre de Précédence

#### Base URL
1. `temporary_base_url` (priorité la plus haute)
2. `user_base_url`
3. `MANTIS_BASE_URL` (env)

#### Token
1. `temporary_token` (priorité la plus haute)
2. `user_token`
3. `MANTIS_API_TOKEN` (env)

## 📋 Exemples de Cas d'Usage

### Cas 1 : Gestion de Tickets

```
# Créer un ticket
User: "Crée un ticket prioritaire avec le titre 'Erreur serveur 500'"

# Ajouter une note
User: "Ajoute une note au ticket 123 : 'Problème résolu après redémarrage'"

# Assigner à un utilisateur
User: "Assigne le ticket 123 à l'utilisateur 5"

# Monitorer le ticket
User: "Je veux suivre le ticket 123"

# Ajouter un tag
User: "Ajoute le tag 'critique' au ticket 123"
```

### Cas 2 : Gestion de Projets

```
# Créer un projet
User: "Crée un projet nommé 'Site Web E-commerce'"

# Ajouter une version
User: "Crée la version 1.0 pour le projet 5"

# Ajouter un utilisateur
User: "Ajoute l'utilisateur 10 au projet 5 comme développeur"

# Lister les sous-projets
User: "Affiche les sous-projets du projet 5"
```

### Cas 3 : Gestion des Utilisateurs

```
# Créer un utilisateur
User: "Crée un utilisateur 'john.doe' avec l'email 'john@example.com'"

# Voir mes infos
User: "Affiche mes informations utilisateur"

# Réinitialiser mot de passe
User: "Réinitialise le mot de passe de l'utilisateur 10"

# Générer un token API
User: "Crée un token API pour moi"
```

### Cas 4 : Multi-Instances (Avancé)

```
# Comparer un ticket entre prod et staging
User: "Compare le ticket 123 entre production et staging"
→ Action 1:
  Set temporary_base_url = "https://prod.mantis.com/api/rest"
  GET /issues/123
  Save result as "prod_issue"

→ Action 2:
  Set temporary_base_url = "https://staging.mantis.com/api/rest"
  GET /issues/123
  Save result as "staging_issue"

→ Compare prod_issue vs staging_issue

# Gérer plusieurs clients
User: "Génère un rapport quotidien pour tous mes clients"
→ For each client (A, B, C):
    Set user_base_url = client.mantis_url
    Set user_token = client.token
    GET /issues?filter_id=daily_filter
    Collect stats
    Clear context
→ Generate consolidated report
```

### Cas 5 : Filtres et Recherches Avancées

```
# Lister les tickets d'un filtre
User: "Affiche les tickets du filtre 10"
→ GET /issues?filter_id=10

# Tickets assignés à moi
User: "Montre mes tickets assignés"
→ GET /issues (avec filtre handler_id = me)

# Tickets non assignés
User: "Liste les tickets sans assignation"
→ GET /issues (avec filtre unassigned)

# Pagination
User: "Affiche les 100 premiers tickets du projet 5"
→ GET /projects/5/issues?page_size=100&page=1
```

### Cas 6 : Notes et Time Tracking

```
# Ajouter une note avec temps
User: "Ajoute une note au ticket 123 : 'Travail effectué' avec 2h30 de temps"
→ POST /issues/123/notes
{
  "text": "Travail effectué",
  "time_tracking": "PT2H30M"
}

# Ajouter une note privée
User: "Ajoute une note privée au ticket 123"
→ POST /issues/123/notes
{
  "text": "Note confidentielle",
  "view_state": {"name": "private"}
}

# Ajouter une note avec pièce jointe
User: "Ajoute une note avec un fichier log au ticket 123"
→ POST /issues/123/notes
{
  "text": "Voir fichier log joint",
  "files": [{"name": "error.log", "content": "base64..."}]
}
```

## 🎯 Fonctionnalités Principales

### Issues (Tickets)
- ✅ CRUD complet (Create, Read, Update, Delete)
- ✅ Monitoring/unmonitoring
- ✅ Gestion des tags
- ✅ Relations entre tickets
- ✅ Pièces jointes
- ✅ Notes avec time tracking
- ✅ Filtres et recherches avancées

### Projects
- ✅ CRUD complet
- ✅ Sous-projets
- ✅ Versions/releases
- ✅ Gestion des membres avec niveaux d'accès

### Users
- ✅ CRUD complet
- ✅ Réinitialisation de mot de passe
- ✅ Génération de tokens API
- ✅ Gestion des permissions

### Configuration
- ✅ Lecture/modification des options
- ✅ Localisation multilingue
- ✅ Impersonation d'utilisateur

### Multi-Instances
- ✅ Basculement dynamique entre instances
- ✅ Gestion de contexte (temporary/session/env)
- ✅ Support de plusieurs clients/environnements
- ✅ Comparaison et synchronisation cross-instance

## 📊 Structure des Données

### Statuts d'Issues
- `new` (10) - Nouveau
- `feedback` (20) - Feedback demandé
- `acknowledged` (30) - Reconnu
- `confirmed` (40) - Confirmé
- `assigned` (50) - Assigné
- `resolved` (80) - Résolu
- `closed` (90) - Fermé

### Priorités
- `none` (10) - Aucune
- `low` (20) - Basse
- `normal` (30) - Normale
- `high` (40) - Haute
- `urgent` (50) - Urgente
- `immediate` (60) - Immédiate

### Severités
- `feature` (10) - Fonctionnalité
- `trivial` (20) - Triviale
- `text` (30) - Texte
- `tweak` (40) - Ajustement
- `minor` (50) - Mineure
- `major` (60) - Majeure
- `crash` (70) - Crash
- `block` (80) - Bloquante

### Niveaux d'Accès
- `viewer` (10) - Lecteur
- `reporter` (25) - Rapporteur
- `updater` (40) - Modificateur
- `developer` (55) - Développeur
- `manager` (70) - Manager
- `administrator` (90) - Administrateur

## ⚠️ Gestion des Erreurs

Le skill gère automatiquement les erreurs HTTP :

- **401 Unauthorized** - Token invalide ou expiré
- **403 Forbidden** - Permissions insuffisantes
- **404 Not Found** - Ressource non trouvée
- **422 Unprocessable Entity** - Erreur de validation
- **500 Internal Server Error** - Erreur serveur

## 🔒 Sécurité

### Bonnes Pratiques
1. **Ne jamais commit les tokens** - Utilisez des variables d'environnement
2. **Tokens à durée limitée** - Définissez une date d'expiration
3. **Permissions minimales** - Utilisez le niveau d'accès minimum requis
4. **Rotation des tokens** - Changez régulièrement vos tokens API

### Impersonation
Pour les administrateurs, l'impersonation permet d'agir au nom d'un autre utilisateur :
```
User: "Agis comme john.doe pour cette opération"
→ Add header: X-Impersonate-User: john.doe
→ Perform operation
```

## 📖 Ressources Supplémentaires

- **Documentation API** : `https://your-mantis-instance.com/api/rest/swagger.yaml`
- **GitHub Mantis BT** : https://github.com/mantisbt/mantisbt
- **Documentation Mantis BT** : https://mantisbt.org/documentation.php
- **Postman Collection** : Contactez votre administrateur Mantis

## 🆘 Support et Dépannage

### Problème : Token invalide (401)
**Solution :** Vérifiez que `MANTIS_API_TOKEN` est correctement défini et que le token n'a pas expiré.

### Problème : Permissions insuffisantes (403)
**Solution :** Vérifiez votre niveau d'accès. Certaines opérations nécessitent des permissions spéciales.

### Problème : Ressource non trouvée (404)
**Solution :** Vérifiez que l'ID de la ressource existe et que vous avez accès au projet concerné.

### Problème : Erreur de validation (422)
**Solution :** Vérifiez la structure des données envoyées. Consultez les exemples dans SKILL.md.

### Problème : Instance non accessible
**Solution :** 
1. Vérifiez `MANTIS_BASE_URL` (doit se terminer par `/api/rest`)
2. Testez l'accès avec curl : `curl -H "Authorization: Bearer YOUR_TOKEN" YOUR_BASE_URL/users/me`
3. Vérifiez les pare-feu et restrictions réseau

## 🔍 Vérification de la Connexion

Pour tester votre configuration :
```
User: "Affiche mes informations utilisateur"
→ GET /users/me
```

Si cela fonctionne, votre configuration est correcte ! ✅

## 📝 Notes de Version

### v1.0 - Février 2026
- ✅ Support complet de l'API REST Mantis BT
- ✅ Gestion multi-instances avec résolution contextuelle
- ✅ 60+ endpoints documentés
- ✅ Exemples complets pour tous les cas d'usage
- ✅ Gestion robuste des erreurs
- ✅ Documentation exhaustive

---

**Auteur** : OpenClaw Skill  
**Licence** : À définir selon votre projet  
**Contribution** : Les contributions sont les bienvenues !

Pour plus de détails, consultez **SKILL.md** pour la documentation complète de l'API.