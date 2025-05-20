from sqlmodel import SQLModel, Session, create_engine
from main import Treino  # Certifique-se de que 'Treino' vem do seu modelo atual

engine = create_engine("sqlite:///treinos.db")

treinos_padrao = [
    # Semana 1
    {"semana": "Semana 4", "dia": "Segunda", "tipo": "Leve", "descricao": "30min corrida leve", "tempo": "00:30:00",
     "distancia": 5},
    {"semana": "Semana 4", "dia": "Quarta", "tipo": "Intervalado", "descricao": "5x800m com pausa de 1min",
     "tempo": "00:25:00", "distancia": 5},
    {"semana": "Semana 4", "dia": "Sexta", "tipo": "Tempo Run", "descricao": "20min em ritmo moderado",
     "tempo": "00:20:00", "distancia": 4.5},
    {"semana": "Semana 4", "dia": "Domingo", "tipo": "Longão", "descricao": "8km em ritmo confortável",
     "tempo": "00:50:00", "distancia": 8},

    # SEMANA 2
    {"semana": "Semana 3", "dia": "Segunda", "tipo": "Fortalecimento A",
     "descricao": "Treino de pernas e core - https://www.youtube.com/watch?v=UoC_O3HzsH0"},
    {"semana": "Semana 3", "dia": "Quarta", "tipo": "Leve", "descricao": "35min corrida leve", "tempo": "00:35:00",
     "distancia": 6},
    {"semana": "Semana 3", "dia": "Sexta", "tipo": "Intervalado", "descricao": "6x400m com ritmo forte",
     "tempo": "00:22:00", "distancia": 4},
    {"semana": "Semana 3", "dia": "Domingo", "tipo": "Longão", "descricao": "9km em ritmo constante",
     "tempo": "00:55:00", "distancia": 9},

    # SEMANA 3
    {"semana": "Semana 1", "dia": "Segunda", "tipo": "Fortalecimento B",
     "descricao": "Treino de mobilidade e estabilidade - https://www.youtube.com/watch?v=3p8EBPVZ2Iw"},
    {"semana": "Semana 1", "dia": "Quarta", "tipo": "Tempo Run", "descricao": "25min com progressão",
     "tempo": "00:25:00", "distancia": 5.5},
    {"semana": "Semana 1", "dia": "Sexta", "tipo": "Intervalado", "descricao": "4x1km com ritmo de prova",
     "tempo": "00:30:00", "distancia": 6},
    {"semana": "Semana 1", "dia": "Domingo", "tipo": "Longão", "descricao": "10km em pace confortável",
     "tempo": "01:00:00", "distancia": 10},

    # SEMANA 4 (preparação 14km)
    {"semana": "Semana 2", "dia": "Segunda", "tipo": "Fortalecimento A",
     "descricao": "Treino funcional - https://www.youtube.com/watch?v=mhHY8mOQ5eI"},
    {"semana": "Semana 2", "dia": "Quarta", "tipo": "Tempo Run", "descricao": "30min em pace de 10km",
     "tempo": "00:30:00", "distancia": 6},
    {"semana": "Semana 2", "dia": "Sexta", "tipo": "Leve", "descricao": "30min trote regenerativo", "tempo": "00:30:00",
     "distancia": 5},
    {"semana": "Semana 2", "dia": "Domingo", "tipo": "Longão", "descricao": "14km simulado da prova",
     "tempo": "01:20:00", "distancia": 14},

]

with Session(engine) as session:
    for treino in treinos_padrao:
        session.add(Treino(**treino))
    session.commit()

print("✅ Treinos padrão inseridos com sucesso!")
