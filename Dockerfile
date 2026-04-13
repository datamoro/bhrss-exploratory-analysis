# Usa a imagem base oficial do Superset
FROM apache/superset:latest 

# Troca para o usuário root para instalar pacotes
USER root

# Instala o driver Python necessário para PostgreSQL
RUN pip install psycopg2-binary

# Volta para o usuário padrão do Superset (segurança)
USER superset