from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    source_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Package {self.name}=={self.version}>"

class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    output = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    package = db.relationship('Package', backref=db.backref('builds', lazy=True))

    def __repr__(self):
        return f"<Build {self.id} for {self.package.name}=={self.version} - {self.status}>"

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Repository {self.name} ({self.url})>"

class EntryScript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    script_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    package = db.relationship('Package', backref=db.backref('entry_scripts', lazy=True))

    def __repr__(self):
        return f"<EntryScript for {self.package.name}: {self.script_path}>"
