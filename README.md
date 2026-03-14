# ShopBR — Django E-commerce

E-commerce backend construído com Django, seguindo arquitetura em camadas (Services + Selectors). Projeto de portfólio com foco em organização de código, testes automatizados e boas práticas de desenvolvimento.

---

## Funcionalidades

- Catálogo de produtos com controle de estoque
- Carrinho de compras por sessão
- Checkout com preço travado no momento da compra
- Histórico de pedidos por usuário
- Sistema de autenticação completo (registro, login, logout)
- Painel administrativo customizado
- API REST paralela à interface web

---

## Stack

- **Python 3.12** + **Django 6.0**
- **Django REST Framework** — API REST
- **PostgreSQL 16** — banco de dados em produção
- **Docker + Docker Compose** — ambiente containerizado
- **SQLite** — banco de dados em desenvolvimento local

---

## Arquitetura

O projeto segue o padrão **Services + Selectors**, baseado no [HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide). Cada camada tem uma responsabilidade única:

```
Request HTTP
    ↓
View          → recebe o request, chama o service, retorna response
    ↓
Service       → regras de negócio, nunca acessa request diretamente
    ↓
Selector      → consultas ao banco (somente leitura)
    ↓
Model         → estrutura de dados + comportamentos simples do domínio
```

**Por que essa arquitetura?**

A lógica de negócio fica em services — independente de HTTP. O mesmo service é chamado pela view HTML e pela API REST, sem duplicação de código. E é testável sem precisar de um servidor rodando.

```
store/
├── models/       # estrutura de dados e métodos de domínio
├── selectors/    # queries ao banco — somente leitura
├── services/     # regras de negócio
├── views/        # thin views — só lidam com HTTP
├── api/          # API REST com DRF
│   ├── serializers/
│   ├── views/
│   └── urls.py
└── templates/
```

---

## Como rodar

### Com Docker (recomendado)

Requisitos: Docker e Docker Compose instalados.

```bash
# Clone o repositório
git clone https://github.com/guipolaci/django-ecommerce.git
cd django-ecommerce

# Configure as variáveis de ambiente
cp .env.example .env

# Suba os containers (Django + PostgreSQL)
docker-compose up --build
```

Acesse em **http://localhost:8000**

O `migrate` roda automaticamente quando o container sobe.

### Sem Docker (desenvolvimento local)

```bash
# Clone o repositório
git clone https://github.com/guipolaci/django-ecommerce.git
cd django-ecommerce

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Rode as migrations
python manage.py migrate

# Suba o servidor
python manage.py runserver
```

Sem a variável `DATABASE_URL` no ambiente, o projeto usa SQLite automaticamente.

### Criando um superusuário

```bash
# Com Docker
docker-compose exec web python manage.py createsuperuser

# Sem Docker
python manage.py createsuperuser
```

---

## Testes

```bash
# Rodar todos os testes
python manage.py test store --verbosity=2
```

36 testes cobrindo:

| Classe | O que testa |
|---|---|
| `RegisterUserServiceTest` | Registro de usuário — sucesso, senhas diferentes, username duplicado |
| `CartServiceTest` | Adicionar, aumentar, diminuir, remover, atualizar quantidade |
| `CheckoutServiceTest` | Checkout — carrinho vazio, criação do pedido, preço travado |
| `StockServiceTest` | Validação de estoque, race condition, desconto após compra |
| `AccountViewTest` | Views de login e registro — GET, POST, redirecionamentos |
| `OrderViewTest` | Checkout, lista de pedidos, segurança entre usuários |

---

## API REST

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/products/` | Lista todos os produtos |
| GET | `/api/products/<id>/` | Detalhe de um produto |
| GET | `/api/cart/` | Carrinho da sessão atual |
| POST | `/api/cart/add/` | Adiciona produto ao carrinho |
| POST | `/api/cart/increase/<id>/` | Aumenta quantidade de um item |
| POST | `/api/cart/decrease/<id>/` | Diminui quantidade de um item |
| DELETE | `/api/cart/remove/<id>/` | Remove item do carrinho |
| PUT | `/api/cart/update/<id>/` | Define quantidade exata |

---

## Decisões técnicas

**Carrinho por sessão, não por usuário**
O carrinho é identificado pela `session_key`. Isso permite que usuários não autenticados naveguem e adicionem produtos. O login só é exigido no checkout.

**Preço travado no OrderItem**
O preço é copiado do produto no momento do checkout e salvo no `OrderItem`. Mudanças futuras no preço do produto não afetam pedidos já realizados.

**Validação de estoque em dois pontos**
O estoque é validado ao adicionar ao carrinho e novamente no checkout. O segundo ponto protege contra race conditions — dois usuários comprando o último item ao mesmo tempo.

**Services sem acesso ao request**
Services recebem dados simples (`session_key: str`, `user: User`) e nunca acessam `request` diretamente. Isso os torna reutilizáveis em qualquer contexto e testáveis sem HTTP.