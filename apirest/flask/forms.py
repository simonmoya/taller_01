from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,TextAreaField
from wtforms.validators import DataRequired, Email, Length

class CrearForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    dorsal = StringField('Dorsal', validators=[DataRequired()])
    
    submit = SubmitField('Crear')

class ModificarForm(FlaskForm):

    nombreBusq = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    dorsal = StringField('Dorsal', validators=[DataRequired()])
    
    submit = SubmitField('Modificar')

class BorrarForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Borrar')