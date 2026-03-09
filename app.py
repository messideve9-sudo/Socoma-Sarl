import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from io import BytesIO
import json
import traceback

# ==================== FORCER LA CRÉATION DE LA BASE DE DONNÉES ====================
print("🔧 Démarrage de l'application SOCOMA...")

app = Flask(__name__)
# CONFIGURATION INTELLIGENTE POUR RENDER
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'socoma-creances-2024-secret-key')

# ==================== CONFIGURATION BASE DE DONNÉES INTELLIGENTE ====================
# RENDER : Si DATABASE_URL existe, utiliser PostgreSQL
# LOCAL : Sinon, utiliser SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL sur Render
    # Correction du format si nécessaire
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print(f"✅ PostgreSQL Render détecté")
else:
    # SQLite pour développement local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///creances.db'
    print("💻 SQLite local (mode développement)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ==============================================================================

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'

# ==================== DONNÉES DES COMMERCIAUX ====================
COMMERCIAUX_DATA = {
    'YAYA CAMARA': {
        'clients': [
            {'prenom': 'FANTA', 'nom': 'DIARRA', 'marche': 'BAGADADJI', 'contact': '76 42 79 10'},
            {'prenom': 'BROULAYE', 'nom': 'DIARRA', 'marche': 'BANCON FARADA', 'contact': '92 69 61 41'},
            {'prenom': 'SOULEYMANE', 'nom': 'TRAORE', 'marche': 'BANCONI FLABOUGOU', 'contact': '76 21 48 06'},
            {'prenom': 'MAHAMADOU', 'nom': 'DIAMOUTENE', 'marche': 'BOULKASSOUMBOUGOU', 'contact': '79 26 07 75'},
            {'prenom': 'MOUSSA', 'nom': 'CISSE', 'marche': 'DJALAKORODJI', 'contact': '72 61 29 81'},
            {'prenom': 'YAYA', 'nom': 'SOUKOULE', 'marche': 'DJELIBOUGOU', 'contact': '76 21 74 82'},
            {'prenom': 'AMINATA', 'nom': 'BALLO', 'marche': 'FADJIGUILA', 'contact': '77 71 70 06'},
            {'prenom': 'ABDOULAYE', 'nom': 'TRAORE', 'marche': 'KONATEBOUGOU', 'contact': '74 48 79 03'},
            {'prenom': 'FAH', 'nom': 'COULIBALY', 'marche': 'MARSEILLE', 'contact': '83 37 37 28'},
            {'prenom': 'DJIBRIL', 'nom': 'SIDIBE', 'marche': 'MEDINE', 'contact': '76 15 93 15'},
            {'prenom': 'SALIF', 'nom': 'DJOURTE', 'marche': 'MEDINE', 'contact': '76 19 26 65'},
            {'prenom': 'BA OUMAR', 'nom': 'SOUMOUNOU', 'marche': 'MEDINE', 'contact': '76 08 97 21'},
            {'prenom': 'ISSA', 'nom': 'DOLO', 'marche': 'MORIBABOUGOU', 'contact': '66 69 66 81'},
            {'prenom': 'FAMOUSSA', 'nom': 'DIAWARA', 'marche': 'NAFADJI', 'contact': '76 24 05 56'},
            {'prenom': 'BASSIDIKY', 'nom': 'FAMATA', 'marche': 'NGOLONINA', 'contact': '76 41 99 39'},
            {'prenom': 'MAMA', 'nom': 'TRAORE', 'marche': 'TITIBOUGOU', 'contact': '65 38 80 87'}
        ]
    },
    'BADRA KEITA': {
        'clients': [
            {'prenom': 'ALOU', 'nom': 'SIDIBE', 'marche': 'DIBIDANI', 'contact': '76 17 43 43'},
            {'prenom': 'DJELIKA', 'nom': 'KEITA', 'marche': 'DJICORONI PARA 1', 'contact': '66 87 40 20'},
            {'prenom': 'OUMOU', 'nom': 'SIDIBE', 'marche': 'DJICORONI PARA 2', 'contact': '76 06 11 40'},
            {'prenom': 'ABDOUL', 'nom': 'TOURE', 'marche': 'HAMDALAYE', 'contact': '75 33 89 43'},
            {'prenom': 'ISSA', 'nom': 'DIALLO', 'marche': 'HAMDALAYE', 'contact': '76 77 03 04'},
            {'prenom': 'MOUSSA', 'nom': 'TRAORE', 'marche': 'KANADJIGUILA', 'contact': '67 82 64 84'},
            {'prenom': 'IDRISSA', 'nom': 'KEITA', 'marche': 'KANADJIGUILA', 'contact': '66 83 10 40'},
            {'prenom': 'DJENABA', 'nom': 'DIARRA', 'marche': 'KATI CENTRAL', 'contact': '78 65 89 12'},
            {'prenom': 'SOUMAILA', 'nom': 'THIERO', 'marche': 'LAFIA BOUGOU 2 TRM', 'contact': '77 29 38 08'},
            {'prenom': 'BEDY', 'nom': 'KEITA', 'marche': 'LAFIA BOUGOU TALIKO', 'contact': '75 28 24 92'},
            {'prenom': 'MAH', 'nom': 'KONATE', 'marche': 'LAFIABOUGOU 1', 'contact': '74 05 15 45'},
            {'prenom': 'AROUNA DJIBRIL', 'nom': 'SIDIBE', 'marche': 'LAFIABOUGOU 2', 'contact': '74 67 72 13'},
            {'prenom': 'GOURO', 'nom': 'MAIGA', 'marche': 'NTOMIKOROBOUGOU', 'contact': '95 95 35 35'},
            {'prenom': 'AMIDOU', 'nom': 'KANTE', 'marche': 'SEBENICORO', 'contact': '76 15 36 71'},
            {'prenom': 'FATOUMATA', 'nom': 'BAGAYOKO', 'marche': 'WOLOFOBOUGOU', 'contact': '76 30 04 47'}
        ]
    },
    'ISSA DIAKITE': {
        'clients': [
            {'prenom': 'KADER', 'nom': 'TRAORE', 'marche': 'BACODJICORO ACI', 'contact': '65 14 66 80'},
            {'prenom': 'CHAKA', 'nom': 'DOUMBIA', 'marche': 'BACODJICORONI', 'contact': '74 10 62 67'},
            {'prenom': 'VIEUX', 'nom': 'DIABATE', 'marche': 'BADALABOUGOU', 'contact': '66 82 48 30'},
            {'prenom': 'AMIDOU', 'nom': 'KODIO', 'marche': 'DAOUDABOUGOU', 'contact': '76 38 66 41'},
            {'prenom': 'THIEMOKO', 'nom': 'SIDIBE', 'marche': 'GARANTIBOUGOU', 'contact': '76 62 23 39'},
            {'prenom': 'LASSINE', 'nom': 'TRAORE', 'marche': 'GOUANA', 'contact': '65 52 85 08'},
            {'prenom': 'MARIAM', 'nom': 'SANOGO', 'marche': 'KABALA', 'contact': '82 92 32 94'},
            {'prenom': 'MOUSSA', 'nom': 'KONE', 'marche': 'KALABAN ACI', 'contact': '70 88 61 49'},
            {'prenom': 'ABOU', 'nom': 'SAMAKE', 'marche': 'KALABAN ECHANGEUR', 'contact': '76 31 72 32'},
            {'prenom': 'ADAMA', 'nom': 'DIARRA', 'marche': 'KALABAN ECHANGEUR', 'contact': '70 93 37 25'},
            {'prenom': 'AMIDOU', 'nom': 'COULIBALY', 'marche': 'KALABAN KLOUBLENI', 'contact': '76 29 57 79'},
            {'prenom': 'AMINATA', 'nom': 'TRAORE', 'marche': 'KALABAN KORO', 'contact': '74 02 18 08'},
            {'prenom': 'SEYDOU', 'nom': 'DOUGNON', 'marche': 'KALABAN KOULOUBA', 'contact': '79 15 88 11'},
            {'prenom': 'MOUSSA', 'nom': 'GACKOU', 'marche': 'KALABAN PRINCIPAL', 'contact': '79 06 13 22'},
            {'prenom': 'NOUHOUM', 'nom': 'TRAORE', 'marche': 'NIAMAKORO KOURANI', 'contact': '66 41 55 31'},
            {'prenom': 'KAROUNGA', 'nom': 'DIARRA', 'marche': 'OLYMPE', 'contact': '78 11 92 59'},
            {'prenom': 'MOHAMED', 'nom': 'TRAORE', 'marche': 'TOROKOROBOUGOU', 'contact': '76 18 42 12'},
            {'prenom': 'FATOUMATA', 'nom': 'DIAKITE', 'marche': 'SABALIBOUGOU', 'contact': '83 91 54 47'}
        ]
    },
    'DIDIER DEMBELE': {
        'clients': [
            {'prenom': 'SOULEYMANE', 'nom': 'GUINDO', 'marche': 'ALAMNA SOUGOU', 'contact': '70 51 95 77'},
            {'prenom': 'FATOUMATA', 'nom': 'CISSE', 'marche': 'ATT BOUGOU', 'contact': '60 16 20 83'},
            {'prenom': 'FAMOUGOURY', 'nom': 'SAMAKE', 'marche': 'BANANKABOUGOU', 'contact': '76 02 84 51'},
            {'prenom': 'BINTOU', 'nom': 'DIALLO', 'marche': 'MAGNAMBOUGOU', 'contact': '74 45 25 66'},
            {'prenom': 'ADAMA', 'nom': 'DIARRA', 'marche': 'MOUSSABOUGOU', 'contact': '78 20 10 20'},
            {'prenom': 'HAMA', 'nom': 'NANTOUME', 'marche': 'NIAMAKORO CHEZ BOUGOUNI', 'contact': '76 76 99 61'},
            {'prenom': 'MOUMINE', 'nom': 'DIAKITE', 'marche': 'NIAMAKORO SOUGOUKORO', 'contact': '76 44 19 38'},
            {'prenom': 'ISAC', 'nom': 'BERTHE', 'marche': 'NIAMAKORO SOUGOUKOURA', 'contact': '72 55 60 60'},
            {'prenom': 'TOGOLAIS', 'nom': 'YAO', 'marche': 'NIAMANA', 'contact': '70 89 66 17'},
            {'prenom': 'MOUSSA', 'nom': 'KEITA', 'marche': 'SABALIBOUGOU KOURANI', 'contact': '69 75 55 13'},
            {'prenom': 'DRAMANE', 'nom': 'OUATARRA', 'marche': 'SENOU', 'contact': '79 31 67 76'},
            {'prenom': 'ABDOULAYE', 'nom': 'DICKO', 'marche': 'SIRAKORO', 'contact': '76 44 42 87'},
            {'prenom': 'HAMADOUNE', 'nom': 'BAH', 'marche': 'SOGONIKO', 'contact': '72 01 12 73'},
            {'prenom': 'DJIBRYL', 'nom': 'SYLLA', 'marche': 'SOKORODJI', 'contact': '78 50 55 66'},
            {'prenom': 'BAMOULAYE', 'nom': 'TRAORE', 'marche': 'YIRIMADJO', 'contact': '76 19 45 67'},
            {'prenom': 'ISSA', 'nom': 'SAGARA', 'marche': 'ZERNI', 'contact': '76 25 18 81'}
        ]
    }
}

# ==================== MODÈLES DE BASE DE DONNÉES ====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    commercial = db.Column(db.String(100), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Creance(db.Model):
    __tablename__ = 'creances'
    
    id = db.Column(db.Integer, primary_key=True)
    commercial = db.Column(db.String(100), nullable=False)
    client = db.Column(db.String(200), nullable=False)
    marche = db.Column(db.String(200), nullable=True)
    montant = db.Column(db.Float, nullable=False)
    versement = db.Column(db.Float, default=0)
    solde = db.Column(db.Float, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    date_facturation = db.Column(db.Date, nullable=False)
    date_echeance = db.Column(db.Date, nullable=True)
    jours_retard = db.Column(db.Integer, default=0)
    statut = db.Column(db.String(50), default='À RELANCER')
    situation_paiement = db.Column(db.String(50), default='EN COURS')
    commentaires = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(80), nullable=True)
    
    def update_statut(self):
        today = datetime.now().date()
        
        if self.solde <= 0:
            self.statut = 'PAYE'
            self.situation_paiement = 'SOLDE'
            self.jours_retard = 0
        elif self.date_echeance:
            if today > self.date_echeance:
                jours = (today - self.date_echeance).days
                self.jours_retard = jours
                if jours <= 3:
                    self.statut = 'À SURVEILLER'
                else:
                    self.statut = 'EN RETARD'
                self.situation_paiement = 'EN RETARD'
            elif today == self.date_echeance:
                self.statut = "AUJOURD'HUI"
                self.situation_paiement = 'À ÉCHÉANCE'
                self.jours_retard = 0
            elif (self.date_echeance - today).days <= 3:
                self.statut = 'À SURVEILLER'
                self.situation_paiement = 'À ÉCHÉANCE'
                self.jours_retard = 0
            else:
                self.statut = 'À RELANCER'
                self.situation_paiement = 'EN COURS'
                self.jours_retard = 0
        else:
            self.statut = 'À RELANCER'
            self.situation_paiement = 'EN COURS'
            self.jours_retard = 0

# ==================== INITIALISATION FORCÉE DE LA BASE ====================
print("📦 Initialisation de la base de données...")
with app.app_context():
    try:
        # Créer les tables
        db.create_all()
        print("✅ Tables de base de données créées")
        
        # Créer les utilisateurs par défaut si nécessaire
        if not User.query.filter_by(username='admin').first():
            admin = User(username='DAOUDA CISSE', role='admin')
            admin.set_password('Csol2102@!*')
            db.session.add(admin)
            
            commercial = User(username='CAMARA YAYA', role='commercial', commercial='YAYA CAMARA')
            commercial.set_password('Socoma2030@')
            db.session.add(commercial)
            
            user = User(username='BDM', role='user')
            user.set_password('Diallobdm2026@')
            db.session.add(user)
            
            db.session.commit()
            print("✅ Utilisateurs par défaut créés:")
            print("   - DAOUDA CISSE / Csol2102@!*")
            print("   - CAMARA YAYA / Socoma2030@")
            print("   - BDM / Diallobdm2026@")
        else:
            print("✅ Utilisateurs existent déjà")
            
        # Vérifier le nombre de créances existantes
        creances_count = Creance.query.count()
        print(f"📊 Créances dans la base: {creances_count}")
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation: {str(e)}")

# ==================== CONFIGURATION LOGIN ====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== FILTRES JINJA2 ====================
@app.template_filter('format_money')
def format_money_filter(value):
    if value is None:
        return "0 FCFA"
    try:
        return f"{int(value):,} FCFA".replace(",", " ")
    except:
        return str(value)

@app.template_filter('format_date')
def format_date_filter(value):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            return value
    return value.strftime('%d/%m/%Y')

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# ==================== TOUTES LES ROUTES ====================

# Routes principales
@app.route('/')
@login_required
def accueil():
    # Récupérer toutes les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    # Calcul des statistiques
    total_creances = sum(c.montant for c in creances) if creances else 0
    total_versement = sum(c.versement for c in creances) if creances else 0
    total_solde = sum(c.solde for c in creances) if creances else 0
    
    creances_retard = [c for c in creances if c.situation_paiement == 'EN RETARD']
    montant_retard = sum(c.solde for c in creances_retard) if creances_retard else 0
    
    tpar = (montant_retard / total_creances * 100) if total_creances > 0 else 0
    
    montant_a_solder = total_solde
    
    # Statistiques par commercial
    stats_commerciaux = {}
    commerciaux_list = [current_user.commercial] if current_user.role == 'commercial' else COMMERCIAUX_DATA.keys()
    
    for commercial in commerciaux_list:
        if commercial:
            comm_creances = [c for c in creances if c.commercial == commercial]
            total_comm = sum(c.montant for c in comm_creances)
            retard_comm = sum(c.solde for c in comm_creances if c.situation_paiement == 'EN RETARD')
            solde_comm = sum(c.solde for c in comm_creances)
            
            stats_commerciaux[commercial] = {
                'count': len(comm_creances),
                'total': total_comm,
                'retard': retard_comm,
                'solde': solde_comm,
                'clients': len(set(c.client for c in comm_creances))
            }
    
    return render_template('accueil.html',
                         total_creances=total_creances,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         montant_retard=montant_retard,
                         montant_a_solder=montant_a_solder,
                         tpar=tpar,
                         creances_retard=creances_retard[:5],
                         stats_commerciaux=stats_commerciaux,
                         total_creances_en_cours=len([c for c in creances if c.solde > 0]))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.now()
            db.session.commit()
            login_user(user, remember=remember)
            flash(f'Bienvenue {username} !', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('login'))

# Routes créances
@app.route('/creances')
@login_required
def liste_creances():
    query = Creance.query
    
    if current_user.role == 'commercial' and current_user.commercial:
        query = query.filter_by(commercial=current_user.commercial)
    
    commercial_filter = request.args.get('commercial')
    statut_filter = request.args.get('statut')
    client_filter = request.args.get('client')
    
    if commercial_filter:
        query = query.filter_by(commercial=commercial_filter)
    if statut_filter:
        query = query.filter_by(statut=statut_filter)
    if client_filter:
        query = query.filter(Creance.client.contains(client_filter))
    
    creances = query.order_by(Creance.date_creation.desc()).all()
    
    if current_user.role == 'commercial' and current_user.commercial:
        commerciaux_list = [current_user.commercial]
    else:
        commerciaux_list = list(COMMERCIAUX_DATA.keys())
    
    return render_template('liste_creances.html',
                         creances=creances,
                         commerciaux=commerciaux_list)

@app.route('/creances/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_creance():
    if current_user.role == 'user':
        flash('Vous n\'avez pas la permission d\'ajouter des créances', 'error')
        return redirect(url_for('liste_creances'))
    
    if request.method == 'POST':
        try:
            commercial = request.form.get('commercial')
            client_type = request.form.get('client_type')
            
            if current_user.role == 'commercial' and commercial != current_user.commercial:
                flash('Vous ne pouvez ajouter des créances que pour votre propre portefeuille', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if client_type == 'existant':
                client = request.form.get('client_select')
                marche = request.form.get('marche')
            else:
                prenom = request.form.get('nouveau_prenom', '').strip()
                nom = request.form.get('nouveau_nom', '').strip()
                if not prenom or not nom:
                    flash('Le prénom et le nom sont obligatoires', 'error')
                    return redirect(url_for('ajouter_creance'))
                client = f"{prenom} {nom}"
                marche = request.form.get('nouveau_marche', '').strip()
            
            try:
                montant = float(request.form.get('montant', 0))
                versement = float(request.form.get('versement', 0))
            except ValueError:
                flash('Les montants doivent être des nombres valides', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if montant <= 0:
                flash('Le montant doit être supérieur à 0', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if versement < 0:
                flash('Le versement ne peut pas être négatif', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if versement > montant:
                flash('Le versement ne peut pas dépasser le montant', 'error')
                return redirect(url_for('ajouter_creance'))
            
            solde = montant - versement
            
            date_facturation_str = request.form.get('date_facturation')
            if not date_facturation_str:
                flash('La date de facturation est obligatoire', 'error')
                return redirect(url_for('ajouter_creance'))
            
            try:
                date_facturation = datetime.strptime(date_facturation_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format de date invalide', 'error')
                return redirect(url_for('ajouter_creance'))
            
            date_echeance_str = request.form.get('date_echeance')
            date_echeance = None
            if date_echeance_str:
                try:
                    date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Format de date d\'échéance invalide', 'error')
                    return redirect(url_for('ajouter_creance'))
            
            commentaires = request.form.get('commentaires', '').strip()
            
            nouvelle_creance = Creance(
                commercial=commercial,
                client=client,
                marche=marche,
                montant=montant,
                versement=versement,
                solde=solde,
                date_facturation=date_facturation,
                date_echeance=date_echeance,
                commentaires=commentaires,
                created_by=current_user.username
            )
            
            nouvelle_creance.update_statut()
            
            db.session.add(nouvelle_creance)
            db.session.commit()
            
            flash(f'Créance ajoutée avec succès pour {client} !', 'success')
            return redirect(url_for('liste_creances'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout: {str(e)}', 'error')
    
    commerciaux_disponibles = []
    if current_user.role == 'commercial':
        commerciaux_disponibles = [current_user.commercial]
    else:
        commerciaux_disponibles = list(COMMERCIAUX_DATA.keys())
    
    return render_template('ajouter_creance.html',
                         commerciaux=commerciaux_disponibles,
                         commerciaux_data=COMMERCIAUX_DATA)

@app.route('/creances/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
def modifier_creance(id):
    creance = Creance.query.get_or_404(id)
    
    if current_user.role == 'commercial' and creance.commercial != current_user.commercial:
        flash('Vous n\'avez pas la permission de modifier cette créance', 'error')
        return redirect(url_for('liste_creances'))
    
    if request.method == 'POST':
        try:
            versement_str = request.form.get('versement', '0')
            try:
                nouveau_versement = float(versement_str)
            except ValueError:
                flash('Le versement doit être un nombre valide', 'error')
                return redirect(url_for('modifier_creance', id=id))
            
            if nouveau_versement < 0:
                flash('Le versement ne peut pas être négatif', 'error')
                return redirect(url_for('modifier_creance', id=id))
            
            if nouveau_versement > creance.montant:
                flash('Le versement ne peut pas dépasser le montant initial', 'error')
                return redirect(url_for('modifier_creance', id=id))
            
            creance.versement = nouveau_versement
            creance.solde = creance.montant - nouveau_versement
            
            date_echeance_str = request.form.get('date_echeance')
            if date_echeance_str:
                try:
                    creance.date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Format de date d\'échéance invalide', 'error')
                    return redirect(url_for('modifier_creance', id=id))
            
            creance.commentaires = request.form.get('commentaires', '').strip()
            creance.update_statut()
            db.session.commit()
            
            flash('Créance modifiée avec succès !', 'success')
            return redirect(url_for('liste_creances'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_creance.html', creance=creance)

@app.route('/creances/supprimer/<int:id>')
@login_required
def supprimer_creance(id):
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('liste_creances'))
    
    creance = Creance.query.get_or_404(id)
    
    try:
        client_name = creance.client
        db.session.delete(creance)
        db.session.commit()
        flash(f'Créance pour {client_name} supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('liste_creances'))

@app.route('/tableau-bord')
@login_required
def tableau_bord():
    # Récupérer les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    # Statistiques globales - AJOUTER DES VALEURS PAR DÉFAUT
    total_creances = sum(c.montant for c in creances) if creances else 0
    total_versement = sum(c.versement for c in creances) if creances else 0
    total_solde = sum(c.solde for c in creances) if creances else 0
    
    creances_retard = [c for c in creances if c.situation_paiement == 'EN RETARD']
    montant_retard = sum(c.solde for c in creances_retard) if creances_retard else 0
    
    montant_a_solder = total_solde
    
    # PROTECTION CONTRE DIVISION PAR ZÉRO
    if total_creances > 0:
        tpar = (montant_retard / total_creances * 100)
    else:
        tpar = 0
    
    # Statistiques par commercial
    stats_commerciaux = {}
    commerciaux_list = [current_user.commercial] if current_user.role == 'commercial' else COMMERCIAUX_DATA.keys()
    
    for commercial in commerciaux_list:
        if commercial:
            comm_creances = [c for c in creances if c.commercial == commercial]
            total_comm = sum(c.montant for c in comm_creances)
            retard_comm = sum(c.solde for c in comm_creances if c.situation_paiement == 'EN RETARD')
            solde_comm = sum(c.solde for c in comm_creances)
            
            # PROTECTION CONTRE DIVISION PAR ZÉRO
            performance = 0
            if total_comm > 0:
                performance = ((total_comm - retard_comm) / total_comm) * 100
            
            stats_commerciaux[commercial] = {
                'count': len(comm_creances),
                'total': total_comm,
                'retard': retard_comm,
                'solde': solde_comm,
                'performance': performance  # AJOUTER CE CHAMP
            }
    
    # Top retards
    top_retard = sorted(creances_retard, key=lambda x: x.jours_retard or 0, reverse=True)[:5]
    
    return render_template('tableau_bord.html',
                         total_creances=total_creances,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         montant_retard=montant_retard,
                         montant_a_solder=montant_a_solder,
                         tpar=tpar,
                         creances_retard=creances_retard,
                         top_retard=top_retard,
                         stats_commerciaux=stats_commerciaux)

@app.route('/recap-clients')
@login_required
def recap_clients():
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    clients_data = {}
    for creance in creances:
        client_key = creance.client
        if client_key not in clients_data:
            clients_data[client_key] = {
                'client': creance.client,
                'commercial': creance.commercial,
                'marche': creance.marche,
                'nombre_creances': 0,
                'total_montant': 0,
                'total_versement': 0,
                'total_solde': 0,
                'derniere_echeance': None
            }
        
        clients_data[client_key]['nombre_creances'] += 1
        clients_data[client_key]['total_montant'] += creance.montant
        clients_data[client_key]['total_versement'] += creance.versement
        clients_data[client_key]['total_solde'] += creance.solde
        
        if creance.date_echeance and (not clients_data[client_key]['derniere_echeance'] or 
                                      creance.date_echeance > clients_data[client_key]['derniere_echeance']):
            clients_data[client_key]['derniere_echeance'] = creance.date_echeance
    
    clients_recap = list(clients_data.values())
    
    total_montant = sum(c['total_montant'] for c in clients_recap)
    total_versement = sum(c['total_versement'] for c in clients_recap)
    total_solde = sum(c['total_solde'] for c in clients_recap)
    total_creances = len(creances)
    
    selected_commercial = request.args.get('commercial')
    if selected_commercial and current_user.role != 'commercial':
        clients_recap = [c for c in clients_recap if c['commercial'] == selected_commercial]
    
    if current_user.role == 'commercial':
        commerciaux_list = [current_user.commercial]
    else:
        commerciaux_list = list(COMMERCIAUX_DATA.keys())
    
    return render_template('recap_clients.html',
                         clients_recap=clients_recap,
                         total_montant=total_montant,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         total_creances=total_creances,
                         commerciaux=commerciaux_list,
                         selected_commercial=selected_commercial)

@app.route('/client/<string:client_name>')
@login_required
def detail_client(client_name):
    client_name = client_name.replace('_', ' ')
    
    query = Creance.query.filter_by(client=client_name)
    
    if current_user.role == 'commercial' and current_user.commercial:
        query = query.filter_by(commercial=current_user.commercial)
    
    creances = query.order_by(Creance.date_creation.desc()).all()
    
    if not creances:
        flash('Client non trouvé ou vous n\'avez pas accès à ce client', 'error')
        return redirect(url_for('recap_clients'))
    
    total_montant = sum(c.montant for c in creances) if creances else 0
    total_versement = sum(c.versement for c in creances) if creances else 0
    total_solde = sum(c.solde for c in creances) if creances else 0
    
    dates_echeance = [c.date_echeance for c in creances if c.date_echeance]
    derniere_date = max(dates_echeance) if dates_echeance else None
    
    return render_template('detail_client.html',
                         client_name=client_name,
                         creances=creances,
                         total_montant=total_montant,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         derniere_date=derniere_date)

@app.route('/commerciaux')
@login_required
def commerciaux():
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
        commerciaux_list = [current_user.commercial]
    else:
        creances = Creance.query.all()
        commerciaux_list = list(COMMERCIAUX_DATA.keys())
    
    stats = {}
    for commercial in commerciaux_list:
        if commercial:
            comm_creances = [c for c in creances if c.commercial == commercial]
            stats[commercial] = {
                'total_creances': len(comm_creances),
                'total_montant': sum(c.montant for c in comm_creances),
                'total_versement': sum(c.versement for c in comm_creances),
                'total_solde': sum(c.solde for c in comm_creances),
                'clients': len(set(c.client for c in comm_creances))
            }
    
    return render_template('commerciaux.html',
                         commerciaux=COMMERCIAUX_DATA,
                         stats=stats)

# Gestion utilisateurs
@app.route('/gestion-utilisateurs')
@login_required
def gestion_utilisateurs():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    utilisateurs = User.query.all()
    return render_template('gestion_utilisateurs.html', utilisateurs=utilisateurs)

@app.route('/creer-compte', methods=['GET', 'POST'])
@login_required
def creer_compte():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', 'user')
            commercial = request.form.get('commercial', '').strip() if role == 'commercial' else None
            
            if not username:
                flash('Le nom d\'utilisateur est obligatoire', 'error')
                return redirect(url_for('creer_compte'))
            
            if not password:
                flash('Le mot de passe est obligatoire', 'error')
                return redirect(url_for('creer_compte'))
            
            if len(password) < 6:
                flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
                return redirect(url_for('creer_compte'))
            
            if role == 'commercial' and not commercial:
                flash('Vous devez sélectionner un commercial pour un compte commercial', 'error')
                return redirect(url_for('creer_compte'))
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Ce nom d\'utilisateur existe déjà', 'error')
                return redirect(url_for('creer_compte'))
            
            nouvel_utilisateur = User(
                username=username,
                role=role,
                commercial=commercial
            )
            nouvel_utilisateur.set_password(password)
            
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            
            flash(f'Compte créé avec succès pour {username} !', 'success')
            return redirect(url_for('gestion_utilisateurs'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du compte: {str(e)}', 'error')
    
    return render_template('creer_compte.html')

@app.route('/supprimer-utilisateur/<int:id>')
@login_required
def supprimer_utilisateur(id):
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('gestion_utilisateurs'))
    
    if current_user.id == id:
        flash('Vous ne pouvez pas supprimer votre propre compte', 'error')
        return redirect(url_for('gestion_utilisateurs'))
    
    utilisateur = User.query.get_or_404(id)
    
    try:
        username = utilisateur.username
        db.session.delete(utilisateur)
        db.session.commit()
        flash(f'Utilisateur {username} supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('gestion_utilisateurs'))

# Export Excel
@app.route('/export-excel')
@login_required
def export_excel():
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    data = []
    for creance in creances:
        data.append({
            'ID': creance.id,
            'Commercial': creance.commercial,
            'Client': creance.client,
            'Marché': creance.marche or '',
            'Montant (FCFA)': creance.montant,
            'Versement (FCFA)': creance.versement,
            'Solde (FCFA)': creance.solde,
            'Date Facturation': creance.date_facturation.strftime('%d/%m/%Y'),
            'Date Échéance': creance.date_echeance.strftime('%d/%m/%Y') if creance.date_echeance else '',
            'Jours Retard': creance.jours_retard or 0,
            'Statut': creance.statut,
            'Situation': creance.situation_paiement,
            'Commentaires': creance.commentaires or '',
            'Créé par': creance.created_by or '',
            'Date Création': creance.date_creation.strftime('%d/%m/%Y %H:%M')
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Créances', index=False)
        
        if current_user.role != 'commercial':
            summary_data = {
                'Commercial': list(COMMERCIAUX_DATA.keys()),
                'Nombre Clients': [len(COMMERCIAUX_DATA[c]['clients']) for c in COMMERCIAUX_DATA.keys()]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Résumé', index=False)
    
    output.seek(0)
    
    filename = f'creances_socoma_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    if current_user.role == 'commercial':
        filename = f'creances_{current_user.commercial.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# Routes admin
@app.route('/admin/reset-creances', methods=['GET', 'POST'])
@login_required
def admin_reset_creances():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    commercial_selected = request.args.get('commercial')
    stats = None
    
    if commercial_selected:
        query = Creance.query
        if commercial_selected != 'TOUS':
            query = query.filter_by(commercial=commercial_selected)
        
        creances = query.all()
        
        stats = {
            'count': len(creances),
            'soldees': len([c for c in creances if c.solde <= 0]),
            'montant_total': sum(c.montant for c in creances),
            'montant_solde': sum(c.solde for c in creances)
        }
    
    if request.method == 'POST':
        action = request.form.get('action')
        commercial = request.form.get('commercial')
        reason = request.form.get('reason')
        confirmation_code = request.form.get('confirmation_code')
        
        flash(f'Action {action} programmée pour {commercial}. Raison: {reason}', 'info')
        return redirect(url_for('admin_reset_creances', commercial=commercial))
    
    return render_template('admin_reset_creances.html',
                         commercial_selected=commercial_selected,
                         stats=stats,
                         confirmation_code='SOC' + datetime.now().strftime('%H%M'))

@app.route('/import-creances', methods=['GET', 'POST'])
@login_required
def import_creances():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    import_results = None
    
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                imported = 0
                errors = 0
                ignored = 0
                
                for _, row in df.iterrows():
                    try:
                        commercial = row.get('Commercial')
                        client = row.get('Client')
                        montant = row.get('Montant')
                        
                        if not commercial or not client or montant is None:
                            ignored += 1
                            continue
                        
                        try:
                            montant_val = float(montant)
                            versement_val = float(row.get('Versement', 0))
                        except ValueError:
                            ignored += 1
                            continue
                        
                        date_facturation_str = str(row.get('Date Facturation', ''))
                        date_echeance_str = str(row.get('Date Échéance', ''))
                        
                        try:
                            if date_facturation_str:
                                date_facturation = datetime.strptime(date_facturation_str.split()[0], '%Y-%m-%d').date()
                            else:
                                date_facturation = datetime.now().date()
                        except:
                            date_facturation = datetime.now().date()
                        
                        date_echeance = None
                        if date_echeance_str and date_echeance_str.strip():
                            try:
                                date_echeance = datetime.strptime(date_echeance_str.split()[0], '%Y-%m-%d').date()
                            except:
                                pass
                        
                        nouvelle_creance = Creance(
                            commercial=str(commercial),
                            client=str(client),
                            marche=str(row.get('Marché', '')),
                            montant=montant_val,
                            versement=versement_val,
                            solde=montant_val - versement_val,
                            date_facturation=date_facturation,
                            date_echeance=date_echeance,
                            commentaires=str(row.get('Commentaires', '')),
                            created_by=current_user.username
                        )
                        
                        nouvelle_creance.update_statut()
                        db.session.add(nouvelle_creance)
                        imported += 1
                        
                    except Exception as e:
                        errors += 1
                
                db.session.commit()
                
                import_results = {
                    'imported': imported,
                    'errors': errors,
                    'ignored': ignored
                }
                
                flash(f'Import terminé ! {imported} créances importées, {errors} erreurs, {ignored} lignes ignorées.', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de l\'import du fichier: {str(e)}', 'error')
    
    return render_template('import_creances.html', import_results=import_results)

# ==================== GESTION DES ERREURS ====================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error=traceback.format_exc()), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# ==================== POINT D'ENTRÉE PRINCIPAL ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Application SOCOMA démarrée sur le port {port}")
    print("🔑 Accès par défaut:")
    print("   - DAOUDA CISSE / Csol2102@!* (admin)")
    print("   - CAMARA YAYA / Socoma2030@ (commercial)")
    print("   - BDM / Diallobdm2026@ (user)")
    app.run(debug=False, host='0.0.0.0', port=port)