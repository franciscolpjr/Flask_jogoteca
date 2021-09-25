#pip3 install flask~=0.12.2
from flask import Flask,render_template,request,redirect,session,flash,url_for
#dao faz toda ponte com o banco de dados MySQL
from dao import JogoDao,UsuarioDao
#Para instanciar o banco de dados
from flask_mysqldb import MySQL
#Models
from models import Jogo,Usuario
#Caminho para pasta img
import os

app = Flask(__name__)

#secret key para uso de informações salvas no session
app.secret_key = 'sexcret'

#Instancia Banco de Dados
app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "admin"
app.config['MYSQL_DB'] = "jogoteca"
app.config['MYSQL_PORT'] = 3306
db = MySQL(app)

jogo_dao_db = JogoDao(db)
usuario_dao_db = UsuarioDao(db)

#caminho para pasta de uploads - img
#__file__ é o caminho para o jogoteca.py
app.config['UPLOAD_PATH'] = os.path.dirname(os.path.abspath(__file__)) + '/img'

#Index
@app.route('/')
def index():
    lista = jogo_dao_db.listar()
    return render_template('lista.html',titulo='Jogos', jogos=lista)

#rota para incluir novo jogo na lista
@app.route('/incluir')
def novo():
    if( session['usuario_logado'] != None and session['usuario_logado'] != '' ):
        return render_template('novo.html',titulo='Incluir Novo Jogo')
    else:
        #após o login quero que retorne para a tela de incluir
        #return redirect('/login?proxima=incluir')
        return redirect(url_for('login',proxima='incluir'))

#rota de entrada do formulário do novo.html
@app.route('/criar',methods=['POST',])
def input():
    nome = request.form['nome'] #name no form
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console)
    #lista.append(jogo)
    #Usando o JogoDao para salvar o dado no BD
    jogo = jogo_dao_db.salvar(jogo)
    #return render_template('lista.html', titulo='Jogos', jogos=lista)
    #return redirect('/')

    #upload imagem
    arquivo = request.files['arquivo'] #arquivo.filename
    nome_arquivo = jogo.id
    pasta_img = app.config['UPLOAD_PATH']
    arquivo.save(f'{pasta_img}/{nome_arquivo}.jpg')
    return redirect(url_for('index'))

#tela login
@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

#autenticar
@app.route('/autenticar',methods=['POST',])
def autenticar():
    usuario = usuario_dao_db.buscar_por_id(request.form['usuario'])
    if usuario:
        if usuario.senha == request.form['senha']:
            session['usuario_logado'] = usuario.id
            flash(usuario.nome + ' logado com sucesso!')
            proxima_pagina = request.form['proxima']
            #return redirect('/{}'.format(proxima_pagina))
            return redirect(proxima_pagina)

    flash('Login falhou. Tente novamente!')
    #return redirect('/login')
    return redirect(url_for('login'))

#Efetuar logout
@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado.')
    #return redirect('/login')
    return redirect(url_for('login'))

#Renderizar página Editar.html
@app.route('/editar/<int:id>')
def editar(id):
    if (session['usuario_logado'] != None and session['usuario_logado'] != ''):
        jogo = jogo_dao_db.busca_por_id(id)
        return render_template('editar.html', titulo='Editar Jogo', jogo=jogo)
    else:
        # após o login quero que retorne para a tela de editar
        # return redirect('/login?proxima=editar')
        return redirect(url_for('editar', proxima='editar'))

#rota de entrada do formulário do editar.html
@app.route('/update', methods=['POST',])
def update():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    id = request.form['id']
    jogo = Jogo(nome,categoria,console,id)
    jogo_dao_db.salvar(jogo)
    return redirect(url_for('index'))

@app.route('/apagar/<int:id>')
def apagar(id):
    if (session['usuario_logado'] != None and session['usuario_logado'] != ''):
        jogo = jogo_dao_db.busca_por_id(id)
        jogo_dao_db.deletar(jogo.id)
        flash("O jogo - " + jogo.nome + " foi removido com sucesso.")
        return redirect(url_for('index'))
    else:
        # após o login quero que retorne para a tela de editar
        # return redirect('/login?proxima=editar')
        return redirect(url_for('login'))


#debug=True - Ambiente de Dev
app.run(debug=True)

