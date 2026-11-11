from database import engine, Base  # Ajuste os nomes conforme os arquivos do seu projeto
import models  # Importante importar os modelos para que o SQLAlchemy os reconheça

Base.metadata.create_all(bind=engine)
