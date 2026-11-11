import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import init_db


if __name__ == "__main__":
    init_db()
    print("Tabelas criadas com sucesso.")
