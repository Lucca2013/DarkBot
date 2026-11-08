from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route("/")
def create_home():
    return render_template('home/index.html')

@pages_bp.route("/create_embed")
def create_embed():
    return render_template('create_embed/index.html')

@pages_bp.route("/create_ticket")
def create_ticket():
    return render_template('create_ticket/index.html')