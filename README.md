### RAG-Immo

### Conception et Implémentation d'un Système GraphRAG pour l'Audit Intelligent et la Conformité Automatisée des Contrats Immobiliers.

### Présentation du Projet

Ce projet de fin d'études porte sur la conception et le développement d'un moteur de Graph Retrieval-Augmented Generation (GraphRAG). L'enjeu principal est l'unification des données structurées provenant de l'ERP ImmoERP et des données non structurées issues des contrats PDF. Le système permet d'automatiser l'audit de conformité en confrontant les transactions financières enregistrées en base SQL avec les obligations contractuelles, puis d'initier des actions correctives automatisées via une intégration de messagerie.

### Environnement Technique (Ticket SCRUM-7)
La solution repose sur une architecture robuste exploitant les technologies suivantes :
#### Composants IA et Orchestration 
Utilisation des frameworks LangChain et LlamaIndex pour la gestion des pipelines RAG. Le moteur de compréhension est basé sur le modèle Mistral-7B-v0.3, sélectionné pour ses capacités de raisonnement logique et d'extraction d'entités.
#### Gestion et Stockage des Données 
Le stockage des relations complexes entre les entités est assuré par la base de données orientée graphe Neo4j. La recherche sémantique est opérée via Supabase avec l'extension pgvector pour la gestion des vecteurs d'embeddings.
#### Automatisations et Notifications 
Intégration de l'API Gmail pour l'envoi automatisé de rapports d'audit et de notifications de relance en cas de non-conformité détectée. Utilisation de bibliothèques de messagerie sécurisées pour garantir la confidentialité des échanges.
#### Développement et Extraction 
Développement sous Python 3.10+, utilisant Pandas pour le traitement de données. L'extraction textuelle des documents PDF est effectuée par PyMuPDF, avec une couche de post-traitement pour assurer la qualité des données extraites.
#### Interface de Démonstration 
L'interface utilisateur est développée sous Streamlit, offrant un tableau de bord interactif pour visualiser les écarts de conformité et piloter les envois de notifications.

### Méthodologie et Innovation
Le projet introduit des techniques avancées pour optimiser la précision du système :
#### Reconnaissance d'Entités et de Relations (NER) 
Application du LLM pour identifier les correspondances sémantiques entre les schémas SQL et les clauses juridiques contractuelles.
#### Audit de Conformité et Boucle d'Action 
Mise en œuvre d'agents intelligents capables d'opérer une comparaison analytique entre les données prévisionnelles et réelles, générant automatiquement des brouillons de communication personnalisés selon la gravité des anomalies détectées.

### Tâche 1 : Analyse du dictionnaire de données et conception du schéma Neo4j
##### Mapping du dictionnaire de données (SQL vers PDF)
Voici la structure de correspondance entre les données métiers et la base de données SQL pour l'intégration Neo4j :

•	 Vendeur (t_company)

      •	Propriétés : Nom, Adresse
•	 Client (t_client)

      •	Propriétés : Nom, CIN, ID
•	 Projet (t_projet)

      •	Propriétés : Nom
      
•	 Bien (t_appartement)

      •	Propriétés : Nom, Prix, ID_Projet
•	 Contrat (t_contrat)

      •	Propriétés : Prix de vente, Avance, ID_Client, ID_Bien
      
•	 Échéancier (t_reglementprevu)

      •	Propriétés : Date prévue, Montant, ID_Contrat
      
•	 Paiements Réels (t_operation)

      •	Propriétés : Montant, Date de règlement, ID_Contrat
##### Modélisation du Graphe de Connaissances (Relations)
Le schéma Neo4j repose sur les relations logiques suivantes pour permettre le "Reasoning" de l'IA :

•	(Client) —[:SIGNE]—> (Contrat) : Lie l'acheteur à son engagement juridique.

•	(Contrat) —[:CONCERNE]—> (Bien) : Identifie l'unité (Appartement/Local) vendue.

•	(Bien) —[:APPARTIENT_À]—> (Projet) : Rattache le bien à son programme immobilier.

•	(Contrat) —[:A_GÉNÉRÉ]—> (Opération) : Suivi des flux financiers réels (4 360 transactions).

•	(Contrat) —[:DOIT_PAYER]—> (Règlement Prévu) : Comparaison avec l'échéancier théorique.

•	(Projet) —[:GÉRÉ_PAR]—> (Vendeur) : Identification du promoteur responsable.

### Tâche 2 : Développement du module d'extraction de texte et d'anonymisation des PDF
Mise en place du pipeline de traitement des documents non structurés.

Extraction : Utilisation de PyMuPDF pour transformer les 64 contrats PDF en texte brut.

Nettoyage : Suppression des sauts de ligne et espaces superflus via Regex.

Anonymisation : Protection des données personnelles par masquage automatique (Regex) des CIN, numéros de téléphone et emails.

### Tâche 3 : Implémentation de la reconnaissance d'entités avec Mistral-7B et LangChain
Cette étape transforme le texte brut anonymisé en données structurées prêtes pour l'injection dans un graphe Neo4j.

Architecture technique : Utilisation du LLM Mistral-7B (via Ollama) orchestré par LangChain pour une extraction locale et sécurisée.

Stratégie d'extraction (Prompt Engineering) :

Conception de prompts spécialisés pour extraire : Client, CIN (Masqué), Désignation, Prix, Avance, Date et Ville.

Optimisation spécifique pour la détection des dates de signature souvent situées en fin de contrat.

Traitement des anomalies : Développement d'un pipeline de reprise (final_extraction.py) pour traiter les contrats complexes présentant des structures non standards.

Normalisation des données :

Conversion des prix en format numérique pour les futurs calculs dans le graphe.

Standardisation des entités géographiques (ex: Normalisation sur "Nador").

Validation finale de l'anonymisation (champ CIN mis à "Masqué").
