Description
1️⃣ Contexte / Problème

    Nous avons le style de code très varié dans le github, ce qui poserait le problème du Code Review.

    Nous avons plusieurs outils de qualité de code : Black, isort, Ruff, Autoflake.

    Chaque outil peut être exécuté séparément, mais cela prend du temps et peut être source d’erreurs.

    Difficulté à maintenir un style de code cohérent et à corriger automatiquement certaines erreurs.

2️⃣ Objectif

    Créer un script unique qui :

        Formate le code (Black, isort, Autoflake)

        Lint le code (Ruff)

        Supporte dry-run et mode rapide (fichiers modifiés uniquement)

        Peut être exécuté sur un fichier, un dossier ou tout le projet

        Supporte le Python versioning pour Black et isort

3️⃣ Fonctionnement du script
Étapes automatisées :

    Autoflake → supprime les imports et variables inutilisés

    Isort → trie les imports, compatible avec Black

    Black → applique le style de code officiel

    Ruff → corrige automatiquement ce qu’il peut, signale les autres problèmes

Options disponibles :

Option
	

Description

--dry
	

Dry-run, affiche les changements sans les appliquer

--fast <branch>
	

Formate seulement les fichiers modifiés par rapport à une branche

--py <version>
	

Spécifie la version Python cible pour Black / isort

filename(s)
	

Formate un ou plusieurs fichiers spécifiques
4️⃣ Avantages pour l’équipe

    ✅ Gain de temps : plus besoin d’exécuter chaque outil séparément

    ✅ Style de code cohérent : Black + isort + Ruff + Autoflake

    ✅ Réduction des erreurs humaines

    ✅ Facile à intégrer dans PyCharm (raccourci Shift + Alt + L)

    ✅ Prépare le projet pour un futur hook git pre-commit

5️⃣ Exemple d’utilisation
# Formate tout le projet
python format_code.py

# Dry-run
python format_code.py --dry

# Seulement les fichiers modifiés vs master
python format_code.py --fast master

# Formater un fichier spécifique
python format_code.py app/services/log_service.py
