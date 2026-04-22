### PFE-RAG-Immo

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
