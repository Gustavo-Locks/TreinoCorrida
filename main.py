from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select, Field
from typing import Optional
from datetime import datetime, date
import json
from collections import defaultdict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///treinos.db"
engine = create_engine(DATABASE_URL)

class Treino(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    semana: str
    dia: str
    tipo: str
    descricao: str
    feito: bool = False
    tempo: Optional[str] = None
    distancia: Optional[float] = Field(default=None)
    tempo_realizado: Optional[str] = None
    distancia_realizada: Optional[float] = Field(default=None)
    observacoes: Optional[str] = None
    pace: Optional[str] = None
    status: Optional[str] = None

SQLModel.metadata.create_all(engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    semana_filtro = request.query_params.get("semana") or semana_atual()
    tipo_filtro = request.query_params.get("tipo")

    hoje_dia_semana = datetime.now().strftime("%A").lower()
    traducao_dias = {
        "monday": "Segunda",
        "tuesday": "Terca",
        "wednesday": "Quarta",
        "thursday": "Quinta",
        "friday": "Sexta",
        "saturday": "Sabado",
        "sunday": "Domingo"
    }
    hoje = traducao_dias.get(hoje_dia_semana, "")

    dias_ordenados = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]

    with Session(engine) as session:
        statement = select(Treino)
        if semana_filtro:
            statement = statement.where(Treino.semana == semana_filtro)
        if tipo_filtro:
            statement = statement.where(Treino.tipo == tipo_filtro)
        treinos = session.exec(statement).all()

    treinos.sort(key=lambda t: (t.semana, dias_ordenados.index(t.dia) if t.dia in dias_ordenados else 99))
    treino_hoje = next((t for t in treinos if t.dia == hoje), None)

    labels = []
    tempos = []
    for treino in treinos:
        if treino.tempo_realizado:
            try:
                tempo_parts = treino.tempo_realizado.split(":")
                tempo_float = int(tempo_parts[0]) * 60 + int(tempo_parts[1]) + int(tempo_parts[2]) / 60
                label = f"{treino.semana}-{treino.dia}"
                labels.append(label)
                tempos.append(tempo_float)
            except:
                continue

    chart_data = json.dumps({"labels": labels, "tempos": tempos})

    for t in treinos:
        if t.tempo_realizado and t.distancia_realizada:
            try:
                h, m, s = map(int, t.tempo_realizado.split(":"))
                total_min = h * 60 + m + s / 60
                pace = total_min / t.distancia_realizada
                t.pace = f"{int(pace):02d}:{int((pace - int(pace)) * 60):02d}/km"
            except:
                t.pace = "-"
        else:
            t.pace = "-"

        t.status = "Feito" if (t.tempo_realizado and t.distancia_realizada) or t.feito else "Pendente"

    dias_da_semana = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
    treinos_por_dia = defaultdict(list)
    for t in treinos:
        treinos_por_dia[t.dia].append(t)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "treinos": treinos,
        "treino_hoje": treino_hoje,
        "chart_data": chart_data,
        "semana": semana_filtro or "",
        "tipo": tipo_filtro or "",
        "dias_da_semana": dias_da_semana,
        "treinos_por_dia": dict(treinos_por_dia)
    })

@app.get("/estatisticas", response_class=HTMLResponse)
def estatisticas(request: Request):
    with Session(engine) as session:
        treinos = session.exec(select(Treino)).all()

    pace_por_semana = defaultdict(list)
    dist_por_semana = defaultdict(float)
    tipo_contagem = defaultdict(int)

    for t in treinos:
        if t.tempo_realizado and t.distancia_realizada:
            try:
                h, m, s = map(int, t.tempo_realizado.split(":"))
                total_min = h * 60 + m + s / 60
                pace = total_min / t.distancia_realizada
                pace_por_semana[t.semana].append(pace)
                dist_por_semana[t.semana] += t.distancia_realizada
            except:
                pass
        tipo_contagem[t.tipo] += 1

    pace_medio = {sem: sum(p)/len(p) for sem, p in pace_por_semana.items() if p}
    semanas = list(sorted(pace_medio.keys()))

    estatisticas_data = {
        "semanas": semanas,
        "pace_medio": [round(pace_medio[s], 2) for s in semanas],
        "distancias": [round(dist_por_semana[s], 2) for s in semanas],
        "tipos": list(tipo_contagem.keys()),
        "contagem_tipos": list(tipo_contagem.values())
    }

    return templates.TemplateResponse("estatisticas.html", {
        "request": request,
        "data": json.dumps(estatisticas_data)
    })

@app.get("/novo", response_class=HTMLResponse)
def novo_treino_form(request: Request):
    return templates.TemplateResponse("treino.html", {"request": request, "treino": None, "modo_edicao": False})

@app.post("/novo")
def criar_treino(
    request: Request,
    semana: str = Form(...),
    dia: str = Form(...),
    tipo: str = Form(...),
    descricao: str = Form(...),
    horas: Optional[str] = Form("00"),
    minutos: Optional[str] = Form("00"),
    segundos: Optional[str] = Form("00"),
    distancia: Optional[str] = Form(None),
    horas_real: Optional[str] = Form("00"),
    minutos_real: Optional[str] = Form("00"),
    segundos_real: Optional[str] = Form("00"),
    distancia_realizada: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None)
):
    tempo = f"{horas.zfill(2)}:{minutos.zfill(2)}:{segundos.zfill(2)}"
    tempo_realizado = f"{horas_real.zfill(2)}:{minutos_real.zfill(2)}:{segundos_real.zfill(2)}"
    try:
        distancia_float = float(distancia) if distancia not in (None, "") else None
    except:
        distancia_float = None
    try:
        distancia_real_float = float(distancia_realizada) if distancia_realizada not in (None, "") else None
    except:
        distancia_real_float = None

    with Session(engine) as session:
        novo = Treino(
            semana=semana,
            dia=dia,
            tipo=tipo,
            descricao=descricao,
            tempo=tempo,
            distancia=distancia_float,
            tempo_realizado=tempo_realizado,
            distancia_realizada=distancia_real_float,
            observacoes=observacoes
        )
        session.add(novo)
        session.commit()
    return RedirectResponse(url="/", status_code=302)

@app.get("/editar/{id}", response_class=HTMLResponse)
def editar_treino_form(request: Request, id: int):
    with Session(engine) as session:
        treino = session.get(Treino, id)
        if not treino:
            return RedirectResponse(url="/", status_code=302)
        return templates.TemplateResponse("treino.html", {"request": request, "treino": treino, "modo_edicao": True})


@app.post("/editar/{id}")
def atualizar_treino(
    id: int,
    semana: str = Form(...),
    dia: str = Form(...),
    tipo: str = Form(...),
    descricao: str = Form(...),
    horas: Optional[str] = Form("00"),
    minutos: Optional[str] = Form("00"),
    segundos: Optional[str] = Form("00"),
    distancia: Optional[str] = Form(None),
    horas_real: Optional[str] = Form("00"),
    minutos_real: Optional[str] = Form("00"),
    segundos_real: Optional[str] = Form("00"),
    distancia_realizada: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    feito: Optional[str] = Form(None)
):
    tempo = f"{horas.zfill(2)}:{minutos.zfill(2)}:{segundos.zfill(2)}"
    tempo_realizado = f"{horas_real.zfill(2)}:{minutos_real.zfill(2)}:{segundos_real.zfill(2)}"
    try:
        distancia_float = float(distancia) if distancia not in (None, "") else None
    except:
        distancia_float = None
    try:
        distancia_real_float = float(distancia_realizada) if distancia_realizada not in (None, "") else None
    except:
        distancia_real_float = None

    with Session(engine) as session:
        treino = session.get(Treino, id)
        if treino:
            treino.semana = semana
            treino.dia = dia
            treino.tipo = tipo
            treino.descricao = descricao
            treino.tempo = tempo
            treino.distancia = distancia_float
            treino.tempo_realizado = tempo_realizado
            treino.distancia_realizada = distancia_real_float
            treino.observacoes = observacoes
            treino.feito = feito == "true"
            session.add(treino)

            session.commit()
    return RedirectResponse(url="/", status_code=302)

def semana_atual():
    hoje = date.today()
    semana_do_mes = (hoje.day - 1) // 7 + 1
    return f"Semana {semana_do_mes}"
