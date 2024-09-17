from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_simplelogin import SimpleLogin, login_required
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padaria.db" #especificando que vamos criar um SQLite e que o nome dele vai ser padaria.db
app.config["SECRET_KEY"] = "MinhaChave10000#"
app.config["SIMPLELOGIN_USERNAME"] = "guilherme"
app.config["SIMPLELOGIN_PASSWORD"] = "abc123"
db = SQLAlchemy() #juntando a aplicação com o banco de dados
db.init_app(app) #inicializar o banco de dados com a minha aplicação
SimpleLogin(app) #por padrão o login é "admmin" e a senha é "secret"

class Product(db.Model):
     __tablename__ = 'produto'
     id = db.Column(db.Integer, primary_key=True)
     nome = db.Column(db.String(100), nullable=False) #aqui o nullable ta garantindo que não haja espaços em branco na coluna nome, ela precisa de um dado
     descricao = db.Column(db.String(500))
     ingredientes = db.Column(db.String(500))
     origem = db.Column(db.String(100))
     imagem = db.Column(db.String(100))
     
     def __init__(self, 
             nome: str, 
             descricao: str, 
             ingredientes: str, 
             origem: str, 
             imagem: str) ->None:
          self.nome = nome
          self.descricao = descricao
          self.ingredientes = ingredientes
          self.origem = origem
          self.imagem = imagem



@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/listar_produtos", methods=["GET", "POST"])
@login_required
def produtos():
     if request.method == "POST":
          termo = request.form["pesquisa"]
          resultado = db.session.execute(db.select(Product).filter(Product.nome.like(f'%{termo}%'))).scalars()
          return render_template("produtos.html", produtos=resultado)
     else:
          produtos = db.session.execute(db.select(Product)).scalars()
          return render_template("produtos.html", produtos=produtos)


@app.route("/cadastrar_produtos", methods=["GET", "POST"])
@login_required
def cadastrar_produtos():
     if request.method == "POST":
          status = {"type": "sucesso", "message": "Produto cadastrado com sucesso!"}
          dados = request.form
          imagem = request.files['imagem']
          try:
               produto = Product(dados['nome_produto'],
                            dados['descricao'],
                            dados['ingredientes'],
                            dados['origem'],
                            imagem.filename)
          
               imagem.save(os.path.join('static\imagens', imagem.filename))
               db.session.add(produto)
               db.session.commit()
          except:
               status = {"type": "erro", "message": f"Houve um problema ao cadastrar o produto {dados['nome_produto']}!"}
          return render_template("cadastrar_produtos.html", status=status)
     else:
          return render_template("cadastrar_produtos.html")


@app.route("/editar_produtos/<int:id>", methods=["GET", "POST"])
@login_required
def editar_produtos(id):
     if request.method == "POST":
          dados_editados = request.form
          imagem = request.files['imagem']
          produto = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()

          produto.nome = dados_editados["nome_produto"]
          produto.descricao = dados_editados["descricao"]
          produto.ingredientes = dados_editados["ingredientes"]
          produto.origem = dados_editados["origem"]

          db.session.commit()
          return redirect("/listar_produtos")
               

     else:   
          produto_editado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
          return render_template("editar_produto.html", produto=produto_editado)



@app.route("/deletar_produtos/<int:id>")
@login_required
def deletar_produtos(id):
     produto_deletado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
     db.session.delete(produto_deletado)
     db.session.commit()
     return redirect("/listar_produtos")



if __name__ == '__main__':
     with app.app_context():
          db.create_all() #falando pro Flask que se já não foi criado, é necessário criar esse banco de dados
          app.run()