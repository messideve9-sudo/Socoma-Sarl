# create_database.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json

# Créer une application Flask temporaire
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'secret_key_for_db_creation'

db = SQLAlchemy(app)

# Modèle Creance (identique à app.py)
class Creance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    commercial = db.Column(db.String(100))
    client = db.Column(db.String(200))
    marche = db.Column(db.String(200))
    montant = db.Column(db.Float)
    versement = db.Column(db.Float, default=0)
    solde = db.Column(db.Float)
    date_echeance = db.Column(db.DateTime)
    situation_paiement = db.Column(db.String(50))
    jours_retard = db.Column(db.Integer)
    statut = db.Column(db.String(50))
    commentaires = db.Column(db.String(500))
    
    def calculer_champs(self):
        # Calculer le solde
        self.solde = self.montant - self.versement
        
        # Déterminer la situation
        aujourdhui = datetime.now().date()
        date_echeance_date = self.date_echeance.date()
        
        if self.solde <= 0:
            self.situation_paiement = "SOLDÉ"
        elif date_echeance_date > aujourdhui:
            self.situation_paiement = "NON ECHU"
        elif date_echeance_date == aujourdhui:
            self.situation_paiement = "ECHU"
        else:
            self.situation_paiement = "EN RETARD"
        
        # Calculer jours de retard
        if self.situation_paiement == "EN RETARD":
            self.jours_retard = (aujourdhui - date_echeance_date).days
        else:
            self.jours_retard = None
        
        # Déterminer statut
        if self.situation_paiement == "EN RETARD":
            self.statut = "A RELANCER"
        elif self.situation_paiement == "ECHU":
            self.statut = "AUJOURD'HUI"
        elif self.situation_paiement == "NON ECHU":
            self.statut = "A SURVEILLER"
        else:
            self.statut = "-"

# Données des commerciaux
COMMERCIAUX = {
    'YAYA CAMARA': [
        {'prenom': 'ABDOULAYE', 'nom': 'TRAORE', 'marche': 'KONATEBOUGOU'},
        {'prenom': 'AMINATA', 'nom': 'BALLO', 'marche': 'FADJIGUILA'},
        {'prenom': 'BASSIDIKY', 'nom': 'FAMATA', 'marche': 'NGOLONINA'},
        {'prenom': 'BROULAYE', 'nom': 'DIARRA', 'marche': 'BANCONI-FARADA'},
        {'prenom': 'BA OUMAR', 'nom': 'SOUMOUNOU', 'marche': 'MEDINE'},
        {'prenom': 'DJIBRIL', 'nom': 'SIDIBE', 'marche': 'MEDINE'},
        {'prenom': 'FAH', 'nom': 'COULIBALY', 'marche': 'MARSEILLE'},
        {'prenom': 'FAMOUSSA', 'nom': 'DIAWARA', 'marche': 'NAFADJI'},
        {'prenom': 'FANTA', 'nom': 'DIARRA', 'marche': 'BAGADADJI'},
        {'prenom': 'ISSA', 'nom': 'DOLO', 'marche': 'MORIBABOUGOU'},
        {'prenom': 'MAHAMADOU', 'nom': 'DIAMOUTENE', 'marche': 'BOULKASSOBOUGOU'},
        {'prenom': 'MAMA', 'nom': 'TRAORE', 'marche': 'TITIBOUGOU'},
        {'prenom': 'MOUSSA', 'nom': 'CISSE', 'marche': 'DIALAKORODJI'},
        {'prenom': 'SALIF', 'nom': 'DJOURTE', 'marche': 'MEDINE'},
        {'prenom': 'SOULEYMANE', 'nom': 'TRAORE', 'marche': 'BANCONI-FLABOUGOU'},
        {'prenom': 'YAYA', 'nom': 'SOUKOULE', 'marche': 'DJELIBOUGOU'}
    ],
    'DIDIER DEMBELE': [
        {'prenom': 'ABDOUL', 'nom': 'TOURE', 'marche': 'HAMDALAYE'},
        {'prenom': 'ISSA', 'nom': 'DIALLO', 'marche': 'HAMDALAYE'},
        {'prenom': 'GOURO', 'nom': 'MAIGA', 'marche': 'NTOMINKOROBOUGOU'},
        {'prenom': 'FATOUMATA', 'nom': 'BAGAYOKO', 'marche': 'WOLOFOBOUGOU'},
        {'prenom': 'ALOU', 'nom': 'SIDIBE', 'marche': 'DIBIDANI'},
        {'prenom': 'DJENABA', 'nom': 'DIARRA', 'marche': 'KATI'},
        {'prenom': 'BEDY', 'nom': 'KEITA', 'marche': 'LAFIABOUGOU-TALIKO'},
        {'prenom': 'SOUMAILA', 'nom': 'THIERO', 'marche': 'LAFIABOUGOU2'},
        {'prenom': 'MOUSSA', 'nom': 'TRAORE', 'marche': 'KANADJIGUILA'},
        {'prenom': 'IDRISSA', 'nom': 'KEITA', 'marche': 'KANADJIGUILA'},
        {'prenom': 'OUMOU', 'nom': 'SIDIBE', 'marche': 'DJICORONI-PARA1'},
        {'prenom': 'AMIDOU', 'nom': 'KANTE', 'marche': 'SEBENICORO'},
        {'prenom': 'DJELIKA', 'nom': 'KEITA', 'marche': 'DJICORONI-PARA1'},
        {'prenom': 'MAH', 'nom': 'KONATE', 'marche': 'LAFIABOUGOU1'},
        {'prenom': 'DJIBRIL', 'nom': 'SIDIBE', 'marche': 'LAFIABOUGOU1'}
    ],
    'ISSA DIAKITE': [
        {'prenom': 'ABOU', 'nom': 'SAMAKE', 'marche': 'KALABAN-ECHANGEUR'},
        {'prenom': 'ABDOULAYE', 'nom': 'DICKO', 'marche': 'SIRAKORO'},
        {'prenom': 'ADAMA', 'nom': 'DIARRA', 'marche': 'KALABAN-ECHANGEUR'},
        {'prenom': 'ADAMA', 'nom': 'DIARRA', 'marche': 'MOUSSABOUGOU'},
        {'prenom': 'AMIDOU', 'nom': 'COULIBALY', 'marche': 'KALABAN-KOULOUBLENI'},
        {'prenom': 'AMIDOU', 'nom': 'KODIO', 'marche': 'DAOUDABOUGOU'},
        {'prenom': 'AMINATA', 'nom': 'TRAORE', 'marche': 'KALABAN-CORO'},
        {'prenom': 'BAMOULAYE', 'nom': 'TRAORE', 'marche': 'YIRIMADIO'},
        {'prenom': 'BINTOU', 'nom': 'DIALLO', 'marche': 'MAGNAMBOUGOU'},
        {'prenom': 'CHAKA', 'nom': 'DOUMBIA', 'marche': 'BACODJICORONI'},
        {'prenom': 'DJIBRYL', 'nom': 'SYLLA', 'marche': 'SOKORODJI'},
        {'prenom': 'DRAMANE', 'nom': 'OUATARRA', 'marche': 'SENOU'},
        {'prenom': 'FAMOUGOURY', 'nom': 'SAMAKE', 'marche': 'BANANKABOUGOU'},
        {'prenom': 'FATOUMATA', 'nom': 'CISSE', 'marche': 'ATTBOUGOU'},
        {'prenom': 'FATOUMATA', 'nom': 'DIAKITE', 'marche': 'SABALIBOUGOU'},
        {'prenom': 'HAMA', 'nom': 'NANTOUME', 'marche': 'NIAMAKORO-CHIEBOUGOUNI'},
        {'prenom': 'HAMADOUNE', 'nom': 'BAH', 'marche': 'SOGONIKO'},
        {'prenom': 'ISAC', 'nom': 'BERTHE', 'marche': 'NIAMAKORO-SUGU-COURA'},
        {'prenom': 'ISSA', 'nom': 'SAGARA', 'marche': 'ZERNI'},
        {'prenom': 'KADER', 'nom': 'TRAORE', 'marche': 'BACODJICORONI-ACI'},
        {'prenom': 'KAROUNGA', 'nom': 'DIARRA', 'marche': 'OLYMPE'},
        {'prenom': 'LASSINE', 'nom': 'TRAORE', 'marche': 'GUOANA'},
        {'prenom': 'MAMADOU', 'nom': 'DIABATE', 'marche': 'BADALABOUGOU'},
        {'prenom': 'MARIAM', 'nom': 'SANOGO', 'marche': 'KABALA'},
        {'prenom': 'MOHAMED', 'nom': 'TRAORE', 'marche': 'TOROKOROBOUGOU'},
        {'prenom': 'MOUMINE', 'nom': 'DIAKITE', 'marche': 'NIAMAKORO-SUGU-KORO'},
        {'prenom': 'MOUSSA', 'nom': 'GACKOU', 'marche': 'KALABAN-PRINCIPAL'},
        {'prenom': 'MOUSSA', 'nom': 'KEITA', 'marche': 'SABALIBOUGOU-COURANI'},
        {'prenom': 'MOUSSA', 'nom': 'KONE', 'marche': 'KALABAN-ACI'},
        {'prenom': 'NOUHOUM', 'nom': 'TRAORE', 'marche': 'NIAMAKORO-COURANI'},
        {'prenom': 'SEYDOU', 'nom': 'DOUGNON', 'marche': 'KALABAN-KOULOUBA'},
        {'prenom': 'SOULEYMANE', 'nom': 'GUINDO', 'marche': 'ALAMINE-SUGU'},
        {'prenom': 'THIEMOKO', 'nom': 'SIDIBE', 'marche': 'GARANTIBOUGOU'},
        {'prenom': 'TOGOLAIS', 'nom': 'YAO', 'marche': 'NIAMANA'}
    ]
}

def creer_donnees_exemple():
    """Créer des données d'exemple réalistes"""
    creances_exemple = []
    
    # Dates de référence
    aujourdhui = datetime.now()
    
    # Exemples pour YAYA CAMARA
    dates_yaya = [
        aujourdhui - timedelta(days=20),  # En retard
        aujourdhui - timedelta(days=5),   # Échéance proche
        aujourdhui + timedelta(days=5),   # Non échu
        aujourdhui + timedelta(days=15),  # Non échu lointain
    ]
    
    for i, (commercial, clients) in enumerate(COMMERCIAUX.items()):
        for j, client in enumerate(clients[:4]):  # 4 clients par commercial
            nom_client = f"{client['prenom']} {client['nom']}"
            
            # Choisir une date selon l'index
            date_idx = j % len(dates_yaya)
            date_facturation = dates_yaya[date_idx]
            date_echeance = date_facturation + timedelta(days=10)
            
            # Montants réalistes (multiples de 50)
            montant_base = [3625000, 3910000, 4755000, 7095000, 3190000]
            montant = montant_base[j % len(montant_base)]
            
            # Pourcentage de paiement selon le statut
            if date_echeance < aujourdhui:  # En retard
                versement = montant * 0.2  # 20% payé
            elif date_echeance == aujourdhui:  # Échu aujourd'hui
                versement = montant * 0.5  # 50% payé
            else:  # Non échu
                versement = montant * 0.7  # 70% payé
            
            # Arrondir au multiple de 50
            montant = round(montant / 50) * 50
            versement = round(versement / 50) * 50
            
            creance = Creance(
                commercial=commercial,
                client=nom_client,
                marche=client['marche'],
                montant=montant,
                versement=versement,
                date_echeance=date_echeance,
                commentaires=f"Créance {j+1} - Client {client['prenom']} {client['nom']}"
            )
            
            creance.calculer_champs()
            creances_exemple.append(creance)
    
    return creances_exemple

def creer_base_de_donnees():
    """Créer la base de données SQLite avec des données d'exemple"""
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists('data.db'):
        print("Suppression de l'ancienne base de données...")
        os.remove('data.db')
    
    # Créer l'application context
    with app.app_context():
        # Créer toutes les tables
        print("Création des tables...")
        db.create_all()
        
        # Créer les données d'exemple
        print("Création des données d'exemple...")
        creances = creer_donnees_exemple()
        
        # Ajouter à la base de données
        db.session.add_all(creances)
        db.session.commit()
        
        print(f"✅ Base de données créée avec succès!")
        print(f"📊 {len(creances)} créances ajoutées")
        
        # Afficher les statistiques
        afficher_statistiques()

def afficher_statistiques():
    """Afficher les statistiques de la base de données"""
    with app.app_context():
        total_creances = Creance.query.count()
        total_montant = db.session.query(db.func.sum(Creance.montant)).scalar() or 0
        total_versement = db.session.query(db.func.sum(Creance.versement)).scalar() or 0
        total_solde = total_montant - total_versement
        
        # Compter par statut
        creances_retard = Creance.query.filter_by(situation_paiement="EN RETARD").count()
        creances_echu = Creance.query.filter_by(situation_paiement="ECHU").count()
        creances_non_echu = Creance.query.filter_by(situation_paiement="NON ECHU").count()
        creances_solde = Creance.query.filter_by(situation_paiement="SOLDÉ").count()
        
        print("\n📈 STATISTIQUES DE LA BASE:")
        print("=" * 40)
        print(f"Total créances: {total_creances}")
        print(f"Montant total facturé: {total_montant:,.0f} FCFA")
        print(f"Versements totaux: {total_versement:,.0f} FCFA")
        print(f"Solde à recouvrer: {total_solde:,.0f} FCFA")
        print(f"Taux de recouvrement: {(total_versement/total_montant*100):.1f}%")
        
        print("\n📊 PAR SITUATION:")
        print(f"  En retard: {creances_retard} créances")
        print(f"  Échues: {creances_echu} créances")
        print(f"  Non échues: {creances_non_echu} créances")
        print(f"  Soldées: {creances_solde} créances")
        
        print("\n👥 PAR COMMERCIAL:")
        for commercial in COMMERCIAUX.keys():
            creances_com = Creance.query.filter_by(commercial=commercial).count()
            montant_com = db.session.query(db.func.sum(Creance.montant)).filter_by(commercial=commercial).scalar() or 0
            if creances_com > 0:
                print(f"  {commercial}: {creances_com} créances, {montant_com:,.0f} FCFA")

def exporter_json():
    """Exporter les données en JSON pour vérification"""
    with app.app_context():
        creances = Creance.query.all()
        data = []
        
        for c in creances:
            data.append({
                'id': c.id,
                'commercial': c.commercial,
                'client': c.client,
                'marche': c.marche,
                'montant': c.montant,
                'versement': c.versement,
                'solde': c.solde,
                'date_echeance': c.date_echeance.strftime('%Y-%m-%d'),
                'situation_paiement': c.situation_paiement,
                'jours_retard': c.jours_retard,
                'statut': c.statut,
                'commentaires': c.commentaires
            })
        
        with open('data_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n📁 Export JSON créé: data_export.json")

if __name__ == '__main__':
    print("🛠️  CRÉATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        creer_base_de_donnees()
        exporter_json()
        
        print("\n" + "=" * 50)
        print("✅ BASE DE DONNÉES PRÊTE!")
        print("\nProchaines étapes:")
        print("1. Lancez l'application: python app.py")
        print("2. Accédez à: http://localhost:5000")
        print("3. Identifiant de test: commercial YAYA CAMARA")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
