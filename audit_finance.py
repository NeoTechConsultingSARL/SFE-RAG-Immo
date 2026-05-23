import json
import requests
from datetime import datetime
from graph_queries import OrionGraphEngine
from neo4j import GraphDatabase
# ✅ Importation officielle compatible avec ton environnement v2.4.5
from mistralai.client import Mistral

# 1. RÉFÉRENTIEL COMPLET DU MARCHÉ IMMOBILIER MAROCAIN
REFERENTIEL_MARCHE = {
    "Casablanca": {
        "moyenne": {"Appartement": 12503, "Villa": 16457},
        "quartiers": {
            "Ain Diab": 31505, "Casablanca Finance City": 25283, "Derb Abdellah": 24321,
            "Gauthier": 22268, "Racine": 19535, "Marina": 19411, "El Manar": 19234,
            "Ferme Bretonne": 18683, "Triangle d'or": 18643, "Riviera": 18536, "Anfa": 19115
        }
    },
    "Rabat": {
        "moyenne": {"Appartement": 12392, "Villa": 13065},
        "quartiers": {
            "Souissi": 22461, "Haut Agdal": 21235, "Riyad": 18609, "Hay Riad": 17863,
            "Akkari": 16190, "Agdal": 15889, "Quartier Administratif": 15162,
            "Yacoub El Mansour": 14887, "Hassan": 14764, "Aviation-Mabella": 14370
        }
    },
    "Tanger": {
        "moyenne": {"Appartement": 8028, "Villa": 11762},
        "quartiers": {
            "Malabata": 14572, "Mghogha": 14531, "Quartier de la plage": 13845,
            "Boulevard Mohammed V": 13302, "Iberie": 13188, "Mnar": 11653,
            "Sania": 11376, "Administratif": 11137, "Rmilat": 10992, "Marchan": 10112
        }
    },
    "Marrakech": {
        "moyenne": {"Appartement": 8885, "Villa": 10138},
        "quartiers": {
            "Hivernage": 17465, "Tassoultante": 14340, "Agdal": 13853, "Masmoudi": 13136,
            "Gueliz": 12620, "Majorelle": 12602, "Camp Al Ghoul": 11982, 
            "Oliva": 11324, "Sidi Bou Amar": 11245, "Ouasis": 10698
        }
    },
    "Agadir": {
        "moyenne": {"Appartement": 7935, "Villa": 10092},
        "communes": {"Aourir": 10042, "Tamri": 10009, "Taghazout": 8326, "Drargua": 7059, "Agadir": 6857, "Founti": 18641 }
    },
    "Meknes": {
        "moyenne": {"Appartement": 6501, "Villa": 7336},
        "quartiers": {
            "Zahwa": 7283, "El Menzeh": 7235, "Avenue des FAR": 7151, "Reda": 7001,
            "Hamria": 6835, "Bel Air": 6745, "Essaadiyine": 6647, "El Bassatine": 6480
        }
    },
    "Fes": {
        "moyenne": {"Appartement": 6578, "Villa": 7667},
        "quartiers": {
            "Fes City Center": 8049, "Moulay El Kamel": 7712, "Bourmana": 7540,
            "Mourabitine": 7180, "Riad": 6911, "Nouvelle Ville": 6872, "Hay Jdid": 6405
        }
    },
    "Nador": {
        "moyenne": {"Appartement": 5901, "Villa": 7517},
        "quartiers": {
            "Wad Benouserdoune": 7560, "Hay Al Matar": 6261, "Al Boustane": 6181,
            "Nador": 6103, "Mediterranee": 5565
        }
    },
    "Oujda": {
        "moyenne": {"Appartement": 5776, "Villa": 7332},
        "quartiers": {
            "Hay Rabat": 8857, "Hay salam": 7353, "El Qods": 7119, "Lazaret": 6942,
            "Agdal": 6272, "Lamhalla": 6064, "Al Boustane": 5869, "Sidi Yahya": 5779
        }
    },
    "Sale": {
        "moyenne": {"Appartement": 8209, "Villa": 10351},
        "quartiers": {
            "Plage des nations": 16427, "Sale El Jadida": 9346, "Hssaine": 9123,
            "Al Mouahidine": 8910, "Said hajji": 8731, "Btana": 8705, "Hay Salam": 8669
        }
    },
    "Kenitra": {
        "moyenne": {"Appartement": 6590, "Villa": 9082},
        "quartiers": {
            "Bir Rami Est": 8419, "Lotissement Nouveau": 8312, "Maamora": 8249,
            "Mimosa": 8047, "Moutanabi": 8018, "Ville Haute": 7803, "Mehdia": 7237
        }
    },
    "Mohammadia": {
        "moyenne": {"Appartement": 7539, "Villa": 11226},
        "quartiers": {
            "Centre Ville": 14814, "Mannesmann": 14225, "Wafa": 13764,
            "Parc": 13078, "La Siesta": 11054, "Hay Salam": 10599
        }
    },
    "El_Jadida": {
        "moyenne": {"Appartement": 7101, "Villa": 9461},
        "quartiers": {
            "Al Boustane": 8438, "Haouzia": 8234, "Centre Ville": 8138,
            "Hay Riad": 7583, "Narjiss": 7143, "Sidi Moussa": 6829
        }
    },
    "Tetouan": {
        "moyenne": {"Appartement": 7742, "Villa": 9831},
        "quartiers": {
            "Hay Hamama": 9437, "Wilaya": 8449, "Touilaa": 8069, "Mahannech": 7455,
            "Oued Martil": 6808, "Hay Boussafou": 6346, "Coelma": 6245
        }
    }
}

class OrionAudit(OrionGraphEngine):
    def __init__(self, uri, user, password, mistral_api_key=None):
        # ✅ Initialisation propre de la classe mère pour partager la même logique de pilote Neo4j
        super().__init__(uri, user, password)
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # ✅ Clé API dynamique passée par le Chatbot ou valeur par défaut pour les tests isolés
        if mistral_api_key is None:
            self.client = Mistral(api_key="9Db8EUWJpZtPjvyczqYgWpsnAsssNlFv")
        else:
            self.client = Mistral(api_key=mistral_api_key)

    def close(self):
        self.driver.close()

    def executer_audit(self):
        with self.driver.session() as session:
            query = """
            MATCH (c:Client)-[:SIGNE]->(con:Contrat)-[:CONCERNE]->(b:Bien)
            MATCH (b)-[:FAIT_PARTIE_DE]->(p:Projet)
            RETURN 
                con.id_tech AS id, 
                c.nom AS client_nom,
                p.ville AS ville_projet, 
                p.adresse AS quartier_projet, 
                p.nom AS nom_projet,
                b.designation AS designation,
                toFloat(con.prixVente) AS prix_total,
                toFloat(b.superficie) AS surface
            """
            resultats = session.run(query)
            rapport_anomalies = []

            for record in resultats:
                anomalies = []
                surface = record["surface"] if record["surface"] > 0 else 1
                prix_m2 = record["prix_total"] / surface
                type_bien = "Villa" if "Villa" in record["designation"] else "Appartement"
                ville = record["ville_projet"]
                quartier = record["quartier_projet"]

                if ville in REFERENTIEL_MARCHE:
                    data = REFERENTIEL_MARCHE[ville]
                    prix_ref = data.get("quartiers", {}).get(quartier, data["moyenne"].get(type_bien, 8000))
                    seuil_alerte = prix_ref * 0.7
                    if prix_m2 < seuil_alerte:
                        anomalies.append(f"🚩 MARCHÉ : Prix suspect ({int(prix_m2)} DH/m² < Seuil {int(seuil_alerte)})")

                if type_bien == "Appartement" and (surface < 20 or surface > 350):
                    anomalies.append(f"⚠️ SAISIE : Surface hors normes ({surface} m²)")

                SEUIL_COUT_REVIENT = 3500 
                if prix_m2 < SEUIL_COUT_REVIENT:
                    anomalies.append(f"⚖️ TECHNIQUE : Prix inférieur au coût de construction ({int(prix_m2)} DH/m²)")

                if anomalies:
                    rapport_anomalies.append({
                        "id": record["id"],
                        "nom": record["client_nom"],
                        "projet": record["nom_projet"],
                        "ville": ville if ville else "Inconnue",
                        "alertes": anomalies
                    })
            return rapport_anomalies

    def calculer_score_ia(self, nom_client):
        with self.driver.session() as session:
            query = """
            MATCH (c:Client {nom: $nom})-[:SIGNE]->(con:Contrat)
            RETURN collect(DISTINCT con.statut_audit) AS statuts
            """
            result = session.run(query, nom=nom_client).single()
            statuts = result["statuts"] if result and result["statuts"] else []

            if not statuts:
                return "Nouveau Prospect (Pas d'historique)", 0
            if statuts == ["À VÉRIFIER"]:
                return "1/5 - Risque Critique (Impayés uniquement)", 1
            if "À VÉRIFIER" in statuts:
                return "2/5 - Vigilance (Mixte avec incidents)", 2
            if statuts == ["EN COURS"]:
                return "3/5 - Client Standard (En cours)", 3
            if "SOLDÉ" in statuts and "EN COURS" in statuts:
                return "4/5 - Client Fidèle (Historique positif)", 4
            if statuts == ["SOLDÉ"]:
                return "5/5 - Client Ambassadeur (Tout est payé)", 5

            return "Score non défini", 0

    def get_audit_data(self):
        query = """
        MATCH (c:Client)-[:SIGNE]->(con:Contrat)
        OPTIONAL MATCH (con)-[:EST_LIÉ_À]->(reg:Reglement)
        OPTIONAL MATCH (con)-[:A_GÉNÉRÉ]->(op:Operation)
        
        WITH c, con, reg,
             sum(DISTINCT toFloat(op.montant)) AS total_paye_reel, 
             date(con.date) AS date_debut,
             toFloat(reg.mensualite) AS mensualite_val,
             toFloat(con.prixVente) AS prix_total,
             toFloat(con.avance) AS avance_con
        
        WHERE prix_total > 0
        
        WITH *, round(prix_total - total_paye_reel, 2) AS reste_a_payer
        
        WITH *, 
             CASE 
                WHEN mensualite_val > 0 THEN ceil((prix_total - avance_con) / mensualite_val)
                ELSE 1 
             END AS calcul_brut
        WITH *, 
             CASE 
                WHEN reste_a_payer <= 10 THEN 1
                WHEN calcul_brut < 12 THEN 12 
                WHEN calcul_brut > 60 THEN 60 
                ELSE calcul_brut 
             END AS duree_prevue_mois
        
        WITH *, duration.inMonths(date_debut, date()).months AS mois_passes
        
        WITH *, 
             CASE 
                WHEN reste_a_payer <= 10 THEN 'SOLDÉ'
                WHEN mois_passes < duree_prevue_mois THEN 'EN COURS'
                ELSE 'À VÉRIFIER'
             END AS statut
        
        RETURN 
            c.nom AS client,
            con.id_tech AS contrat,
            statut,
            date_debut AS date_signature,
            duree_prevue_mois,
            mois_passes,
            round(prix_total, 2) AS prix_vente,
            round(total_paye_reel, 2) AS deja_paye,
            reste_a_payer,
            c.email AS email
        ORDER BY reste_a_payer DESC
        """
        return self.execute_cypher(query)

    def trier_par_nom(self, liste_donnees):
        """Trie proprement par le nom du client (A-Z)."""
        # Utilise 'client' qui est la clé uniforme envoyée par l'API
        return sorted(
            liste_donnees, 
            key=lambda x: str(x.get('client', '')).lower().strip()
        )

    def trier_par_reste_a_payer(self, liste_donnees):
        """Trie par reste à payer décroissant."""
        # Sécurise la conversion en float directement sur la clé de l'API
        return sorted(
            liste_donnees, 
            key=lambda x: float(x.get('reste_a_payer') or 0.0), 
            reverse=True
        )
    
    def enregistrer_statuts_dans_neo4j(self, data):
        query = """
        UNWIND $liste_contrats AS item
        MATCH (con:Contrat {id_tech: item.id})
        SET con.statut_audit = item.statut
        """
        params = [{"id": d['contrat'], "statut": d['statut']} for d in data]
        self.execute_cypher(query, {"liste_contrats": params})
        print("✅ Statuts enregistrés avec succès dans Neo4j.")

    def ask_mistral_smart(self, retards, normaux, stats_dict):
        prompt = f"""
        [INST] Tu es Orion, l'expert IA de cet audit financier immobilier au Maroc.
        
        STATISTIQUES GLOBALES :
        - Total dossiers : {stats_dict['total']}
        - Soldés : {stats_dict['soldes']}
        - En Retard : {stats_dict['retards']}
        - En Cours : {stats_dict['normaux']}
        
        VOICI LES DOSSIERS EN RETARD (Statut: À VÉRIFIER) :
        {json.dumps(retards, indent=2)}

        VOICI LES DOSSIERS NORMAUX (Statut: EN COURS) :
        {json.dumps(normaux, indent=2)}

        CONSIGNES :
        1. Rédige un rapport pro.
        2. Ne mélange JAMAIS les deux listes.
        3. Montant global à recouvrer : {stats_dict['montant_global_restant']}.
        [/INST]
        """
        try:
            response = self.client.chat.complete(
                model="open-mistral-7b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Erreur Cloud Mistral : {str(e)}"


# --- TESTS EN MODE LOCAL TERMINAL ---
if __name__ == "__main__":
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "admin123"
    MISTRAL_KEY = "9Db8EUWJpZtPjvyczqYgWpsnAsssNlFv"

    audit = OrionAudit(URI, USER, PASSWORD, MISTRAL_KEY)
    
    print("\n🔍 ANALYSE FINANCIÈRE GLOBALE (500 CONTRATS)...")
    all_data = audit.get_audit_data()
    
    if all_data:
        audit.enregistrer_statuts_dans_neo4j(all_data)
        for item in all_data:
            if hasattr(item.get('date_signature'), 'isoformat'):
                item['date_signature'] = item['date_signature'].isoformat()

        termines = [d for d in all_data if d['statut'] == 'SOLDÉ']
        a_verifier = [d for d in all_data if d['statut'] == 'À VÉRIFIER']
        en_cours = [d for d in all_data if d['statut'] == 'EN COURS']

        stats = {
            "total": len(all_data),
            "soldes": len(termines),
            "retards": len(a_verifier),
            "normaux": len(en_cours),
            "montant_global_restant": f"{sum(d['reste_a_payer'] for d in all_data):,.2f} DH"
        }

        print(f"✅ Analyse terminée : {stats['total']} dossiers traités.")
        print(f"📊 {stats['soldes']} terminés, {stats['retards']} en retard, {stats['normaux']} en cours.")

        print("\n🤖 Rédaction du rapport par Mistral Cloud (Chargement Global)...")
        rapport = audit.ask_mistral_smart(a_verifier[:3], en_cours[:2], stats)
        
        print("\n" + "="*75)
        print("RAPPORT D'AUDIT FINANCIER ORION")
        print("="*75)
        print(rapport)
        print("="*75)
    
    audit.close()