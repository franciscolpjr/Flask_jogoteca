#pip3 install flask~=0.12.2
from flask import Flask,render_template,request,redirect,session,flash,url_for
#dao faz toda ponte com o banco de dados MySQL
from dao import JogoDao,UsuarioDao
#Para instanciar o banco de dados
from flask_mysqldb import MySQL
#Models
from models import Jogo,Usuario

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
    jogo_dao_db.salvar(jogo)
    #return render_template('lista.html', titulo='Jogos', jogos=lista)
    #return redirect('/')
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
            session['usuario_logado'] = dadosUser.id
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

#debug=True - Ambiente de Dev
app.run(debug=True)

