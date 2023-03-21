from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os


app = Flask(__name__)

app.secret_key = 'castagnari'

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='jconde'
#app.config['MYSQL_DATABASE_PASSWORD']='basededatos6c' 
app.config['MYSQL_DATABASE_PASSWORD']='jc2021'
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)


@app.route('/')
def index():

    sql = "SELECT * FROM `empleados`;"
    conexionBD = mysql.connect()
    cursor = conexionBD.cursor()
    cursor.execute(sql)

    _empleados = cursor.fetchall()
    print(_empleados)
    conexionBD.commit()

    return render_template('empleados/index.html',empleados=_empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conexionBD = mysql.connect()
    cursor = conexionBD.cursor()

    cursor.execute("SELECT foto FROM `empleados` WHERE id=%s",(id))
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM `empleados` WHERE id=%s",(id))
    conexionBD.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conexionBD = mysql.connect()
    cursor = conexionBD.cursor()
    cursor.execute("SELECT * FROM `empleados` WHERE id=%s",(id))
    _empleados = cursor.fetchall()
    conexionBD.commit()
    return render_template('empleados/edit.html',empleados=_empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['inputNombre']
    _correo=request.form['inputCorreo']
    _foto=request.files['inputFoto']
    _ID = request.form['inputID']

    sql = "UPDATE `empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"

    datos = (_nombre, _correo, _ID)
    conexionBD = mysql.connect()
    cursor = conexionBD.cursor()


    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        
        cursor.execute("SELECT foto FROM `empleados` WHERE id=%s",(_ID))
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE `empleados` SET `foto`=%s, WHERE id=%s;",nuevoNombreFoto,_ID)
        conexionBD.commit()


    cursor.execute(sql, datos)
    conexionBD.commit()
    return redirect('/')

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route("/store",methods=['POST'])
def storage():
    _nombre=request.form['inputNombre']
    _correo=request.form['inputCorreo']
    _foto=request.files['inputFoto']

    if _nombre=='' or _correo=='' or _foto.filename=='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    #nuevoNombreFoto

    if _foto.filename!='':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`nombre`, `correo`, `foto`) VALUES (%s,%s,%s);"

    datos = (_nombre, _correo, nuevoNombreFoto)
    conexionBD = mysql.connect()
    cursor = conexionBD.cursor()
    cursor.execute(sql, datos)
    conexionBD.commit()
    return redirect(url_for('index'))

if __name__== '__main__':
    app.run(debug=True)