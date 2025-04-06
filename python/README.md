# Mantiks Job Scraper

Ce projet permet de récupérer automatiquement les offres d'emploi d'entreprises spécifiques en utilisant l'API Mantiks. Les données sont ensuite sauvegardées dans des fichiers JSON nommés d'après les entreprises ciblées.

## Fonctionnalités

- Récupération des offres d'emploi depuis l'API Mantiks
- Sauvegarde des données dans des fichiers JSON
- Extraction automatique du nom de l'entreprise depuis l'URL LinkedIn
- Filtrage des offres par mots-clés
- Limitation par âge des annonces

## Prérequis

- Python 3.6+
- Jupyter Notebook
- Une clé API Mantiks valide

## Installation

1. Clonez ce dépôt:
```
git clone <url-du-depot>
cd mantiks-job-scraper
```

2. Installez les dépendances:
```
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet (voir configuration)

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes:

```
MANTIKS_API_KEY=votre_cle_api_mantiks
DIRECTORY_PATH=/chemin/vers/dossier/de/sauvegarde
```

- `MANTIKS_API_KEY`: Votre clé API Mantiks (obligatoire)
- `DIRECTORY_PATH`: Le chemin vers le dossier où les fichiers JSON seront sauvegardés (optionnel - par défaut, les fichiers sont sauvegardés dans le répertoire courant)

## Utilisation

Ce projet est développé sous forme de Jupyter notebook, ce qui permet une utilisation interactive et une visualisation facile des résultats.

### Exécution du notebook

1. Assurez-vous que Jupyter est installé (inclus dans requirements.txt)
2. Lancez Jupyter:
```
jupyter notebook
```
3. Ouvrez le notebook principal depuis l'interface web de Jupyter

### Exemple de code

Voici un exemple de code similaire à celui contenu dans le notebook:

```python
# Import des fonctions depuis les cellules précédentes
# Dans le notebook, ces fonctions sont définies dans des cellules antérieures

# Paramètres de recherche
company_url = "https://fr.linkedin.com/company/google"
website_url = "https://about.google"
age_in_days = -2147483648  # Pas de limite d'âge
keyword = ""  # Pas de filtre par mot-clé
keyword_excluded = ""  # Pas de mots-clés exclus

# Extraction du nom de l'entreprise
company_name = extract_company_name_from_url(company_url)

# Récupération des offres
result = request_jobs(company_url, website_url, age_in_days, keyword, keyword_excluded)

# Sauvegarde des résultats
if result:
    print(f"Nombre d'offres trouvées: {len(result['jobs'])}")
    save_to_file(company_name, result)
    print(f"Crédits restants: {result['credits_remaining']}")
else:
    print("Aucune donnée récupérée.")
```

## Exemples

### Filtrer par mot-clé

```python
# Chercher uniquement les offres contenant "développeur" ou "engineer"
keyword = "développeur,engineer"
```

### Limiter par âge des offres

```python
# Récupérer uniquement les offres des 30 derniers jours
age_in_days = 30
```

### Exclure certains mots-clés

```python
# Exclure les offres contenant "stage" ou "stagiaire"
keyword_excluded = "stage,stagiaire"
```

## Structure des données

Les fichiers JSON générés contiennent les informations suivantes:

```json
{
    "credits_remaining": 4560,
    "jobs": [
        {
            "date_creation": "2023-06-14T00:41:30.644058",
            "last_seen": "2023-07-14T01:22:09.098543",
            "description": "...",
            "job_board": "indeed",
            "job_board_url": "https://www.indeed.com/viewjob?vjs=3&jk=9381c6dc1f1af9af",
            "job_title": "Critical Environment Program Manager",
            "location": "Paris (75)"
        },
        ...
    ],
    "nb_jobs": 2,
    "success": true
}
```

## Résolution des problèmes

- **Erreur 400 (Bad Request)**: Vérifiez le format des paramètres passés à l'API
- **Erreur 401 (Unauthorized)**: Vérifiez votre clé API dans le fichier `.env`
- **Clé API non trouvée**: Assurez-vous que le fichier `.env` est correctement formaté et situé à la racine du projet

## Limites

L'utilisation de l'API Mantiks est soumise à des quotas. Vérifiez régulièrement vos crédits restants (`credits_remaining` dans la réponse) pour vous assurer que vous ne dépassez pas vos limites d'utilisation.