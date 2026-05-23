import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from audit_finance import OrionAudit
from mistralai.client import Mistral # <--- Ajout de l'import Mistral officiel

class OrionRelance(OrionAudit):
    def ask_mistral_smart_simple(self, prompt):
        """
        Interroge le modèle Mistral en ligne via la clé API officielle.
        """
        # Utilisation de ta clé API Mistral valide
        api_key_en_ligne = "9Db8EUWJpZtPjvyczqYgWpsnAsssNlFv"
        
        try:
            client = Mistral(api_key=api_key_en_ligne)
            
            # Appel du modèle cloud (rapide et stable)
            response = client.chat.complete(
                model="open-mistral-7b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            texte_ia = response.choices[0].message.content
            if texte_ia and texte_ia.strip():
                return texte_ia
            return None
            
        except Exception as e:
            print(f"❌ Erreur avec Mistral en ligne : {e}")
            return None

    def envoyer_email_simulation(self, corps_email, nom_client, mon_email, mon_mot_de_passe, email_destination):
        """
        Gère la connexion SMTP SSL vers Gmail pour envoyer les relances.
        """
        msg = MIMEMultipart()
        msg['From'] = mon_email
        msg['To'] = email_destination
        msg['Subject'] = f"[RELANCE ORION] Rappel Paiement - Client: {nom_client}"

        msg.attach(MIMEText(corps_email, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(mon_email, mon_mot_de_passe)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email à {email_destination} : {e}")
            return False

    def executer_campagne_relance(self, mon_email, mon_mot_de_passe, email_destination=None, liste_emails_cochés=None):
        """
        Orchestre la campagne : récupère les données de l'audit Neo4j,
        distingue l'envoi unique de l'envoi ciblé par cases à cocher.
        """
        print("📊 Récupération des dossiers depuis l'audit...")
        all_data = self.get_audit_data()
        liste_a_traiter = []

        # --- CAS 1 : ENVOI UNIQUE (Saisie manuelle dans la zone bleue) ---
        if email_destination and not liste_emails_cochés:
            print(f"🎯 Traitement de l'adresse unique reçue : '{email_destination}'")
            client_data = None
            
            # On nettoie l'adresse saisie par l'utilisateur
            email_saisi_propre = str(email_destination).strip().lower()
            
            print(f"🔍 Parcours des {len(all_data)} dossiers récupérés par l'audit...")
            for d in all_data:
                # Extraction de toutes les clés d'email possibles dans ton dictionnaire d'audit
                email_1 = d.get('email')
                email_2 = d.get('email_client')
                
                # Affichage de débogage pour voir ce que Python lit réellement dans ton dictionnaire
                print(f"   -> Client inspecté : '{d.get('client')}' | email dans dict : '{email_1}' ou '{email_2}'")
                
                if email_1 and str(email_1).strip().lower() == email_saisi_propre:
                    client_data = d
                    break
                if email_2 and str(email_2).strip().lower() == email_saisi_propre:
                    client_data = d
                    break
            
            if client_data:
                print(f"✅ Correspondance parfaite trouvée pour : {client_data.get('client')}")
                client_data['destination_finale'] = email_destination
                liste_a_traiter = [client_data]
            else:
                print(f"❌ ERREUR CRITIQUE : L'adresse '{email_destination}' n'existe dans AUCUN dictionnaire généré par get_audit_data().")
                return {"status": "error", "message": f"L'adresse {email_destination} n'est pas reconnue dans les données de l'audit actuel."}

        # --- CAS 2 : ENVOI MULTIPLE (Sélection par cases à cocher dans le tableau) ---
        elif liste_emails_cochés:
            print(f"🗂️ Traitement des clients sélectionnés par case à cocher ({len(liste_emails_cochés)})...")
            for critere_coché in liste_emails_cochés:
                if not critere_coché:
                    continue
                critere_propre = str(critere_coché).strip().lower()
                
                for d in all_data:
                    nom_base = str(d.get('client') or "").strip().lower()
                    email_base = str(d.get('email') or d.get('email_client') or "").strip()
                    
                    # Correspondance stricte par le nom du client coché
                    if critere_propre == nom_base:
                        # SÉCURITÉ : Si l'email est absent ou invalide dans Neo4j, on lève une erreur explicite
                        if not email_base or email_base.lower() == "none" or "@" not in email_base:
                            print(f"⚠️ Erreur de configuration pour {d.get('client')} : Pas d'adresse e-mail valide.")
                            return {"status": "error", "message": f"Impossible d'envoyer la relance. Le client '{d.get('client')}' n'a pas d'adresse e-mail valide configurée dans la base de données."}
                        
                        d['destination_finale'] = email_base
                        liste_a_traiter.append(d)
                        print(f"🔗 Association réussie pour le tableau : {d.get('client')} -> {d['destination_finale']}")
                        break

        if not liste_a_traiter:
            return {"status": "error", "message": "Aucun client correspondant trouvé pour l'envoi."}

        succes_comptage = 0
        for client_data in liste_a_traiter:
            nom = client_data.get('client', 'Client Orion').replace('\r', '').replace('\n', ' ').strip()
            contrat = client_data.get('contrat', 'Non spécifié')
            dette = client_data.get('reste_a_payer', 0)
            retard = client_data.get('mois_passes', 0)
            dest_mail = client_data.get('destination_finale', mon_email)


            prompt = f"""
            [INST] Tu es Orion, l'expert IA d'Orion Immobilier.
            Rédige un e-mail de relance professionnel et chaleureux destiné au client suivant :
            CLIENT À RELANCER : {nom}
            CONTRAT : {contrat}
            DETTE : {dette} DH
            RETARD : {retard} mois.
            
            CONSIGNES OBLIGATOIRES :
            - Commence l'e-mail DIRECTEMENT par : "Bonjour {nom}," (N'écris JAMAIS "Madame, Monsieur").
            - Rédige TOUT le texte en texte brut 100% simple.
            - Interdiction absolue d'utiliser des symboles comme les étoiles double astérisques (**), des crochets ou des hashtags.
            - Signe à la fin avec exactement :
              Service Recouvrement Orion - Aya
              Téléphone : +212 5 36 11 90 00 (Nador)
              E-mail : ayaetsara2006@gmail.com
            - Langue : Français.
            [/INST]
            """
            
            print(f"🤖 Mistral Cloud génère le corps du message pour {nom}...")
            contenu_email = self.ask_mistral_smart_simple(prompt)
            if not contenu_email:
                print(f"❌ Échec de génération Mistral en ligne pour {nom}.")
                continue
            if contenu_email:
                contenu_email = contenu_email.replace("**", "")

            # Ensuite ton code continue normalement comme avant :
            if not os.path.exists("relances_generees"):
                os.makedirs("relances_generees")

            # Sauvegarde locale de secours
            if not os.path.exists("relances_generees"):
                os.makedirs("relances_generees")
            with open(f"relances_generees/relance_{nom.replace(' ', '_')}.txt", "w", encoding="utf-8") as f:
                f.write(contenu_email)

            # Envoi de l'e-mail réel vers ton adresse
            print(f"📩 Expédition du message à {dest_mail}...")
            if self.envoyer_email_simulation(contenu_email, nom, mon_email, mon_mot_de_passe, dest_mail):
                succes_comptage += 1

        return {"status": "success", "message": f"{succes_comptage} relance(s) générée(s) via Mistral AI avec succès !"}
