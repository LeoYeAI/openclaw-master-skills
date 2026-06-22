# Odoo Manager - OpenClaw Skill

Un skill OpenClaw pour interagir avec **Odoo** via son **API externe XML-RPC** :  
connexion, sélection d’instance/base, et opérations génériques sur n’importe quel modèle (avec des exemples prêts à l’emploi pour `res.partner`).

---

## 🚀 Installation & Configuration

### 1. Variables d’Environnement Requises

Configure au minimum :

```bash
ODOO_URL=https://your-odoo-instance.odoo.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_login@example.com
ODOO_PASSWORD=your_password_or_api_key
```

Optionnel :

```bash
# À utiliser de préférence à la place de ODOO_PASSWORD
ODOO_API_KEY=your_api_key_here
```

> L’API externe Odoo est décrite ici :  
> https://www.odoo.com/documentation/18.0/fr/developer/reference/external_api.html

### 2. Mot de Passe vs Clé API

Deux façons de s’authentifier :

- **Mot de passe classique** Odoo (`ODOO_PASSWORD`)
- **Clé API** (`ODOO_API_KEY`) utilisée exactement comme un mot de passe

Pour créer une clé API :

1. Connecte-toi à Odoo avec ton compte.
2. Va dans **Préférences / Mon profil**.
3. Onglet **Sécurité du compte**.
4. Clique sur **Nouvelle clé API**, donne une description claire, puis copie la clé.
5. Place cette clé dans `ODOO_API_KEY` (ou `user_api_key` / `temporary_api_key` côté contexte).

> La clé API donne le **même niveau d’accès** que ton utilisateur. Protége-la comme un mot de passe.

---

## 🧠 Résolution du Contexte (URL, DB, Utilisateur)

Le skill applique une logique de **résolution hiérarchique** pour savoir quelle
instance et quelle base utiliser.

### 1. URL (instance Odoo)

Ordre de priorité :

1. `temporary_url` (pour une seule opération)
2. `user_url` (pour toute la session)
3. `ODOO_URL` (valeur par défaut, environnement)

### 2. Base de Données (db)

Ordre de priorité :

1. `temporary_db`
2. `user_db`
3. `ODOO_DB`

### 3. Identifiant & Secret

- Username : `temporary_username` → `user_username` → `ODOO_USERNAME`
- Secret (mot de passe ou clé API) :  
  `temporary_api_key` / `temporary_password` →  
  `user_api_key` / `user_password` →  
  `ODOO_API_KEY` (si présent) sinon `ODOO_PASSWORD`

En pratique, le skill travaille toujours avec :

- `resolved_url`
- `resolved_db`
- `resolved_username`
- `resolved_secret` (mot de passe ou clé API)

---

## 📖 Démarrage Rapide

Les exemples ci‑dessous montrent **l’intention utilisateur** (en français) et
le type d’appels XML‑RPC qui seront effectués.

### Exemple 1 : Vérifier la Connexion

```text
User: "Vérifie la connexion à Odoo"
```

Flux :

1. Résolution du contexte (`resolved_url`, `resolved_db`, `resolved_username`, `resolved_secret`).
2. Appel de `version()` sur `{{resolved_url}}/xmlrpc/2/common`.
3. Essai d’authentification :

   ```python
   uid = common.authenticate(resolved_db, resolved_username, resolved_secret, {})
   ```

4. Retour à l’utilisateur : version du serveur et UID obtenu (ou message d’erreur).

### Exemple 2 : Lister les Sociétés (res.partner)

```text
User: "Liste toutes les sociétés avec leur pays"
```

Flux :

1. Authentification via `common.authenticate`.
2. Appel générique ORM :

   ```python
   companies = models.execute_kw(
       resolved_db, uid, resolved_secret,
       "res.partner", "search_read",
       [[["is_company", "=", True]]],
       {"fields": ["name", "country_id", "comment"], "limit": 80}
   )
   ```

3. Le skill formate et affiche les résultats (nom, pays, commentaire).

### Exemple 3 : Créer un Partenaire

```text
User: "Crée un partenaire société nommé 'OpenClaw SARL'"
```

Flux :

```python
partner_id = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "create",
    [{
        "name": "OpenClaw SARL",
        "is_company": True
    }]
)
```

Le skill peut ensuite relire le partenaire créé avec `read` pour l’afficher.

### Exemple 4 : Afficher les Champs d’un Modèle

```text
User: "Montre les champs du modèle res.partner"
```

Flux :

```python
fields = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "fields_get",
    [],
    {"attributes": ["string", "help", "type"]}
)
```

Le skill résume les champs (nom technique, label, type, aide).

---

## 🔄 Multi‑Instances & Multi‑Bases

Comme pour le skill MantisBT Manager, Odoo Manager permet de gérer
**plusieurs instances Odoo** et **plusieurs bases** en parallèle, via le contexte.

### Contexte Temporaire (une seule opération)

```text
User: "Pour cette requête, utilise l’instance de staging"
```

Interprétation possible :

```text
Set temporary_url = "https://staging.mycompany.odoo.com"
Set temporary_db  = "staging_db"
→ Exécuter l’opération demandée
→ Clear temporary_url, temporary_db
```

Utile pour :

- Comparer une donnée entre production et staging
- Tester une modification sur une base de test

### Contexte de Session

```text
User: "Travaille sur l’instance du client ABC avec la base clientabc_prod"
```

Interprétation :

```text
Set user_url = "https://client-abc.odoo.com"
Set user_db  = "clientabc_prod"
Set user_username = "integration_bot"
Set user_api_key  = "clé_api_client_abc"
```

Toutes les opérations suivantes utilisent ce contexte, jusqu’à réinitialisation.

### Retour aux Valeurs par Défaut

```text
User: "Reviens à l’instance Odoo par défaut"
```

→ Clear `user_url`, `user_db`, `user_username`, `user_password`, `user_api_key`  
→ Utilisation de `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` / `ODOO_API_KEY`

---

## 🎯 Cas d’Usage Typiques

### 1. Gestion des Contacts (res.partner)

- Lister les sociétés / contacts.
- Créer un partenaire (client, fournisseur, contact interne).
- Mettre à jour les coordonnées, emails, téléphones.
- Supprimer des partenaires de test.

### 2. Inspection & Découverte du Modèle

- Lister les modèles disponibles (`ir.model`).
- Lister les champs d’un modèle (`fields_get`, `ir.model.fields`).
- Préparer des intégrations en comprenant la structure des données.

### 3. Travail sur Plusieurs Bases

- Comparer un contact ou une commande entre deux bases.
- Effectuer des vérifications ponctuelles sur une base de test.
- Gérer plusieurs clients ayant chacun leur propre base Odoo.

### 4. Automatisations Génériques

- Exécuter `search` / `search_read` sur n’importe quel modèle métier
  (`crm.lead`, `project.task`, `sale.order`, etc.).
- Mettre à jour en masse des enregistrements (par lots raisonnables).

---

## ⚠️ Gestion des Erreurs & Dépannage

### Problèmes Courants

- **Échec de connexion** : mauvaise URL (`ODOO_URL`) ou serveur injoignable.
- **Échec d’authentification** : mauvais `db`, login, mot de passe ou clé API.
- **Droits insuffisants** : l’utilisateur n’a pas accès au modèle ou à l’action.
- **Erreurs de validation** : champs obligatoires manquants, contraintes Odoo.

### Recommandations

- Vérifier que tu utilises la **bonne base** (`ODOO_DB` ou overrides contextuels).
- Pour Odoo Online, t’assurer que l’utilisateur possède bien un **mot de passe local**
  ou une clé API (voir la doc Odoo).
- En cas d’erreur sur un modèle/champ, afficher les détails de l’exception pour
  savoir quel champ ou quelle contrainte pose problème.

---

## 🔒 Sécurité & Bonnes Pratiques

- **Ne jamais commiter** `ODOO_PASSWORD` ni `ODOO_API_KEY` dans un dépôt.
- Utiliser exclusivement des **variables d’environnement** ou un coffre-fort
  de secrets.
- Donner au compte utilisé les **droits minimum nécessaires** (principe du moindre privilège).
- Changer régulièrement les mots de passe / clés API en production.

> L’accès à l’API externe Odoo est réservé aux offres **Custom**.  
> Il n’est pas disponible sur les offres **One App Free** ou **Standard**.

---

## 📚 Référence Complète du Skill

La spécification détaillée du skill (résolution de contexte, opérations génériques
ORM, exemples `res.partner`, introspection, etc.) se trouve dans :

- `Odoo Manager/SKILL.md`

Consulte ce fichier pour voir tous les détails des appels `execute_kw` et
des modèles pris en charge de manière générique.

