from neo4j import GraphDatabase

class OrionAudit:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def calculer_score_ia(self, nom_client):
        with self.driver.session() as session:
            # On récupère les statuts des contrats du client
            # Note : Assure-toi que la propriété 'statut_audit' existe dans Neo4j
            query = """
            MATCH (c:Client {nom: $nom})-[:SIGNE]->(con:Contrat)
            RETURN collect(DISTINCT con.statut_audit) AS statuts
            """
            result = session.run(query, nom=nom_client).single()
            statuts = result["statuts"] if result and result["statuts"] else []

            # Ta logique de Score :
            if not statuts:
                return "Nouveau Prospect (Pas d'historique)", 0
            
            # 1. Uniquement des retards
            if statuts == ["À VÉRIFIER"]:
                return "1/5 - Risque Critique (Impayés uniquement)", 1
                
            # 2. Mixte avec au moins un retard
            if "À VÉRIFIER" in statuts:
                return "2/5 - Vigilance (Mixte avec incidents)", 2
                
            # 3. Uniquement en cours
            if statuts == ["EN COURS"]:
                return "3/5 - Client Standard (En cours)", 3
                
            # 4. Mixte positif (Soldé + En cours)
            if "SOLDÉ" in statuts and "EN COURS" in statuts:
                return "4/5 - Client Fidèle (Historique positif)", 4
                
            # 5. Parfait (Uniquement du Soldé)
            if statuts == ["SOLDÉ"]:
                return "5/5 - Client Ambassadeur (Tout est payé)", 5

            return "Score non défini", 0

# --- LE BLOC DE TEST ---
if __name__ == "__main__":
    # Vérifie bien ton mot de passe ici (admin123 ?)
    audit = OrionAudit("bolt://localhost:7687", "neo4j", "admin123")
    
    # Liste de test (Vérifie que ces noms existent exactement comme ça dans Neo4j)
    clients_a_tester = ["GHITA BERRADA", "BACHIR SKALLI", "FAIZA EL JOUNDI"]
    
    print("\n" + "="*50)
    print("🛡️ SYSTÈME D'ANALYSE DE RISQUE ORION AI")
    print("="*50)

    for nom in clients_a_tester:
        resultat, score_num = audit.calculer_score_ia(nom)
        
        # Affichage des étoiles
        stars = "⭐" * score_num if score_num > 0 else "❌"

        print(f"👤 Client : {nom}")
        print(f"📊 Statut : {resultat}")
        print(f"🛡️ Note   : {stars} ({score_num}/5)")
        print("-" * 30)

    audit.close()