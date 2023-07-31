from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class AddForm(FlaskForm):
    new_device = StringField("Device Name", validators=[DataRequired()])
    new_ip = StringField("IP Address Ex. 0.0.0.0", validators=[DataRequired()])
    new_status = SelectField("Status (on/off)", choices=["on", "off"], validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    ip_edit = StringField("IP Address Ex. 0.0.0.0", validators=[DataRequired()])
    status_edit = SelectField("Status (on/off)", choices=["on", "off"], validators=[DataRequired()])
    submit = SubmitField('Submit')

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devices.db"
db = SQLAlchemy()
# initialize the app with the extension
db.init_app(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    ip = db.Column(db.String)
    status = db.Column(db.String)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/devices")
def devices():
    result = db.session.execute(db.select(Device).order_by(Device.name))
    all_devices = result.scalars().all()
    return render_template("devices.html", all_devices=all_devices)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        with app.app_context():
            new_device = Device(name=form.new_device.data, ip=form.new_ip.data, status=form.new_status.data)
            db.session.add(new_device)
            db.session.commit()
        return redirect(url_for("devices"))

    return render_template("add.html", form=form)

@app.route("/edit/<device_name>", methods=["GET", "POST"])
def edit(device_name):
    form=EditForm()
    if form.validate_on_submit():
        with app.app_context():
            device_to_update = db.session.execute(db.select(Device).where(Device.name == device_name)).scalar()
            device_to_update.ip = form.ip_edit.data
            device_to_update.status = form.status_edit.data
            db.session.commit()
        return redirect(url_for("devices"))

    return render_template("edit.html", form= form, device_name=device_name)

@app.route("/delete/<device_name>")
def delete(device_name):
    with app.app_context():
        device_to_delete = db.session.execute(db.select(Device).where(Device.name == device_name)).scalar()
        db.session.delete(device_to_delete)
        db.session.commit()
    return redirect(url_for("devices"))

if __name__ == '__main__':
    app.run(debug=True)

