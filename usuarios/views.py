from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Usuario, Maquinas, EstadoMaquina, ComandoMaquina, SesionTerapia
from django.views.decorators.csrf import csrf_exempt
import json, re
import requests
import time
from django.conf import settings

# -------------------------------
# Vistas principales (CON autenticación)
# -------------------------------

def home(request):
    return render(request, "home.html")

def login_views(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=nombre, password=password)
            if user is not None:
                login(request, user)
                request.session['usuario_id'] = user.id
                request.session['usuario_nombre'] = user.nombre
                request.session['usuario_rol'] = user.rol

                if user.rol == 'paciente':
                    return redirect('dashboard_paciente')
                elif user.rol == 'doctor':
                    return redirect('dashboard_doctor')
                else:
                    messages.error(request, 'Rol de usuario no válido.')
                    return redirect('login')
            else:
                messages.error(request, 'Nombre o contraseña incorrectos.')
        except Exception as e:
            print(f"Error en login: {e}")
            messages.error(request, 'Ocurrió un error en el login.')
    return render(request, 'login.html')

@login_required
def dashboard_paciente(request):
    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'paciente_dashboard.html', {'nombre': nombre})

@login_required
def dashboard_doctor(request):
    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'doctor_dashboard.html', {'nombre': nombre})

# -------------------------------
# Gestión de pacientes (CON autenticación)
# -------------------------------

@login_required
def gestion_pacientes(request):
    user = request.user
    try:
        perfil = Usuario.objects.get(nombre=user.username)
        nombre = perfil.nombre
    except Usuario.DoesNotExist:
        nombre = user.username
    return render(request, "gestion_pacientes.html", {"nombre": nombre})

@login_required
def lista_pacientes(request):
    pacientes = list(Usuario.objects.filter(rol='paciente').values(
        "id", "nombre", "peso", "tamano_de_la_pantorrilla", "sesiones", "altura"
    ))
    return JsonResponse(pacientes, safe=False)

@login_required
def lista_maquinas(request):
    maquinas = list(Maquinas.objects.values("numero"))
    return JsonResponse(maquinas, safe=False)

@login_required
def listar_maquinas_estado(request):
    maquinas = Maquinas.objects.all()
    resultado = []
    
    for maquina in maquinas:
        estado_memoria = ULTIMO_ESTADO_POR_DISP.get(maquina.numero, {})
        estado_bd = EstadoMaquina.objects.filter(maquina=maquina).first()
        
        tiempo_ahora = time.time()
        conectado = False
        
        if estado_memoria:
            conectado = (tiempo_ahora - estado_memoria.get("ultimo_timestamp", 0)) <= 60
        elif estado_bd:
            conectado = (tiempo_ahora - estado_bd.ultimo_timestamp) <= 60
        
        resultado.append({
            "numero": maquina.numero,
            "ip": maquina.ip,
            "conectado": conectado,
            "activo": estado_memoria.get("activo", estado_bd.activo if estado_bd else False),
            "grados_actuales": estado_memoria.get("grados_actuales", estado_bd.grados_actuales if estado_bd else 0),
            "repeticiones": estado_memoria.get("repeticiones", estado_bd.repeticiones if estado_bd else 0),
        })
    
    return JsonResponse({"maquinas": resultado})

# -------------------------------
# VISTAS DEL ESP32 - SIN AUTENTICACIÓN (CORREGIDAS)
# -------------------------------

# MEMORIA EN PROCESO
ULTIMO_ESTADO_POR_DISP = {}
COMANDOS_PENDIENTES = {}

def esp32_authorize(request):
    """Solo verifica token API, NO autenticación de usuario Django"""
    token = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"error": "Falta header Authorization"}, status=403)
    
    if token.startswith("Token "):
        token = token[6:]
    
    if token != getattr(settings, 'ESP32_API_TOKEN', 'default_token_here'):
        return JsonResponse({"error": "Token inválido"}, status=403)
    return True

# ✅ VISTA CORREGIDA - SIN @login_required
@csrf_exempt
def recibir_datos_esp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
    print("Datos crudos:", request.body)
    # Solo verifica token API
    auth = esp32_authorize(request)
    if auth is not True:
        return auth

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)

    nombre = data.get("nombre")
    if not nombre:
        return JsonResponse({"success": False, "error": "Falta 'nombre' del dispositivo"}, status=400)

    activo = data.get("activo", False)
    grados_actuales = int(data.get("grados_actuales", 0))
    repeticiones = int(data.get("repeticiones", 0))

    # Guardar en memoria
    ULTIMO_ESTADO_POR_DISP[nombre] = {
        "nombre": nombre,
        "activo": bool(activo),
        "grados_actuales": grados_actuales,
        "repeticiones": repeticiones,
        "ultimo_timestamp": time.time()
    }

    # Guardar en base de datos
    try:
        maquina, created = Maquinas.objects.get_or_create(numero=nombre)
        estado_maquina, created = EstadoMaquina.objects.get_or_create(
            maquina=maquina,
            defaults={
                'activo': activo,
                'grados_actuales': grados_actuales,
                'repeticiones': repeticiones,
                'ultimo_timestamp': time.time(),
                'conectado': True
            }
        )
        if not created:
            estado_maquina.activo = activo
            estado_maquina.grados_actuales = grados_actuales
            estado_maquina.repeticiones = repeticiones
            estado_maquina.ultimo_timestamp = time.time()
            estado_maquina.conectado = True
            estado_maquina.save()
    except Exception as e:
        print(f"Error guardando en BD: {e}")

    return JsonResponse({
        "status": "ok",
        "nombre": nombre,
        "nuevo_estado": ULTIMO_ESTADO_POR_DISP[nombre]
    })

# ✅ VISTA CORREGIDA - SIN @login_required
@csrf_exempt
def controlar_sesion(request):
    numero = request.GET.get("numero")  # nombre de la máquina
    if not numero:
        return JsonResponse({"error": "Falta numero"}, status=400)

    # 1. Buscar o crear máquina
    maquina, creada = Maquinas.objects.get_or_create(
        numero=numero,
        defaults={"ip": request.META.get("REMOTE_ADDR")}
    )

    # 2. Buscar o crear estado
    estado, _ = EstadoMaquina.objects.get_or_create(
        maquina=maquina,
        defaults={"conectado": True, "ultimo_timestamp": time.time()}
    )

    # Marcar como conectada
    estado.conectado = True
    estado.ultimo_timestamp = time.time()
    estado.save()

    # 3. Buscar comando NO ejecutado más reciente
    comando = ComandoMaquina.objects.filter(
        maquina=maquina,
        ejecutado=False
    ).order_by("timestamp_creacion").first()

    if comando:
        print("📤 Enviando comando:", comando.accion)

        # Marcar como ejecutado
        comando.ejecutado = True
        comando.timestamp_ejecucion = time.time()
        comando.save()

        return JsonResponse({
            "accion": comando.accion,
            "grados": comando.grados,
            "repeticiones": comando.repeticiones
        })

    # 4. Si NO hay comandos
    return JsonResponse({
        "accion": None,
        "mensaje": "No hay comandos"
    })

# ✅ VISTA CORREGIDA - SIN @login_required
@csrf_exempt
def estado_arduino(request):
    """Devuelve o actualiza el estado de la máquina según GET o POST."""
    if request.method == "GET":
        nombre = request.GET.get("numero")
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            nombre = data.get("numero")
            estado_enviado = data.get("estado")
        except:
            return JsonResponse({"error": "JSON inválido"}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

    if not nombre:
        return JsonResponse({"error": "Falta parámetro 'numero'"}, status=400)

    # Inicializar en memoria si no existe
    if nombre not in ULTIMO_ESTADO_POR_DISP:
        try:
            maquina = Maquinas.objects.get(numero=nombre)
            estado_bd = EstadoMaquina.objects.filter(maquina=maquina).first()
            if estado_bd:
                ULTIMO_ESTADO_POR_DISP[nombre] = {
                    "nombre": nombre,
                    "activo": estado_bd.activo,
                    "grados_actuales": estado_bd.grados_actuales,
                    "repeticiones": estado_bd.repeticiones,
                    "ultimo_timestamp": estado_bd.ultimo_timestamp or 0,
                    "conectado": estado_bd.conectado
                }
            else:
                ULTIMO_ESTADO_POR_DISP[nombre] = {
                    "ultimo_timestamp": 0,
                    "conectado": False,
                    "activo": False,
                    "grados_actuales": 0,
                    "repeticiones": 0,
                    "estado": "sin_datos",
                }
        except Maquinas.DoesNotExist:
            ULTIMO_ESTADO_POR_DISP[nombre] = {
                "ultimo_timestamp": 0,
                "conectado": False,
                "activo": False,
                "grados_actuales": 0,
                "repeticiones": 0,
                "estado": "maquina_no_registrada",
            }

    estado = ULTIMO_ESTADO_POR_DISP[nombre]

    # Si es POST, actualizar estado recibido
    if request.method == "POST":
        if estado_enviado is not None:
            estado["activo"] = bool(estado_enviado)
            estado["ultimo_timestamp"] = time.time()
            # Guardar también en BD
            try:
                maquina = Maquinas.objects.get(numero=nombre)
                estado_bd, created = EstadoMaquina.objects.get_or_create(maquina=maquina)
                estado_bd.activo = estado["activo"]
                estado_bd.ultimo_timestamp = estado["ultimo_timestamp"]
                estado_bd.conectado = True
                estado_bd.save()
            except Exception as e:
                print("Error guardando estado POST:", e)

    # Conectividad según tiempo
    tiempo_ahora = time.time()
    estado_copy = dict(estado)
    estado_copy["conectado"] = (tiempo_ahora - estado.get("ultimo_timestamp", 0) <= 60)

    return JsonResponse(estado_copy)


# -------------------------------
# Otras vistas
# -------------------------------


#@login_required
@csrf_exempt
def recibir_datos(request):
    """Recibe datos desde el frontend y registra máquina y estado."""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        print("Datos recibidos:", data)

        # Tu frontend ENVÍA "maquina", NO "numero"
        numero_maquina = data.get('maquina')
        if not numero_maquina:
            return JsonResponse({'error': "Falta 'maquina' en el JSON"}, status=400)

        # Crear la máquina si no existe
        maquina, created = Maquinas.objects.get_or_create(
            numero=numero_maquina,
            defaults={'ip': '0.0.0.0'}
        )

        # Obtener o crear el estado
        estado, estado_creado = EstadoMaquina.objects.get_or_create(
            maquina=maquina
        )

        # Guardar SOLO lo que envías
        estado.activo = True if data.get("accion") == "iniciar" else False
        estado.grados_actuales = int(data.get("grados", 0))
        estado.repeticiones = int(data.get("repeticiones", 0))
        estado.stop_grados = int(data.get("stop_grados", 0))
        estado.modo = data.get("modo", "normal")
        estado.conectado = True
        estado.save()

        print(f"Estado de máquina {numero_maquina} actualizado")

        return JsonResponse({
            'mensaje': 'Datos recibidos correctamente',
            'maquina': numero_maquina,
            'accion': data.get("accion"),
            'modo': data.get("modo"),
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON mal formado'}, status=400)
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'error': str(e)}, status=400)



@csrf_exempt
@login_required
def agregar_paciente(request):
    """Agregar paciente - CON autenticación"""
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        tamano_de_la_pantorrilla = data.get("tamano_de_la_pantorrilla")
        peso = data.get("peso")
        altura = data.get("altura")

        base = nombre.lower().replace(" ", "_")
        if not Usuario.objects.filter(username=base).exists():
            username = base
        else:
            usuarios = Usuario.objects.filter(username__startswith=base)
            max_num = 0
            for u in usuarios:
                match = re.match(rf"{base}_?(\d+)$", u.username)
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num
            username = f"{base}_{max_num + 1}"

        Usuario.objects.create(
            nombre=nombre,
            tamano_de_la_pantorrilla=tamano_de_la_pantorrilla,
            peso=peso,
            altura=altura,
            username=username,
            rol="paciente",
        )
        return JsonResponse({"status": "ok", "username": username})
    return JsonResponse({"error": "Método no permitido"}, status=400)


def lista_maquinas_json(request):
    maquinas = []

    for m in Maquinas.objects.all():
        estado = getattr(m, "estado_actual", None)

        maquinas.append({
            "id": m.id,
            "numero": m.numero,
            "ip": m.ip,
            "conectado": estado.conectado if estado else False,
            "activo": estado.activo if estado else False,
            "grados_actuales": estado.grados_actuales if estado else 0,
            "repeticiones": estado.repeticiones if estado else 0,
        })

    return JsonResponse(maquinas, safe=False)

# Guardas los datos del frontend en un dict global
ULTIMOS_COMANDOS = {}

@csrf_exempt
def guardar_comando(request):
    if request.method == "POST":
        data = json.loads(request.body)
        maquina = data.get("maquina")
        if not maquina:
            return JsonResponse({"error": "Falta 'maquina'"}, status=400)
        ULTIMOS_COMANDOS[maquina] = {
            "accion": data.get("accion"),
            "grados": int(data.get("grados", 0)),
            "repeticiones": int(data.get("repeticiones", 0)),
            "stop_grados": int(data.get("stop_grados", 0)),
            "modo": data.get("modo", "normal")
        }
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def comando_esp(request):
    numero = request.GET.get('maquina')
    if not numero:
        return JsonResponse({"error": "Falta parámetro 'maquina'"}, status=400)

    # Obtener o crear máquina
    maquina, _ = Maquinas.objects.get_or_create(
        numero=numero,
        defaults={'ip': '0.0.0.0'}
    )

    # Obtener o crear estado de la máquina
    estado, _ = EstadoMaquina.objects.get_or_create(
        maquina=maquina,
        defaults={
            'activo': False,
            'grados_actuales': 0,
            'repeticiones': 0,
            'stop_grados': 0,
            'modo': 'normal',
            'conectado': True
        }
    )

    # Construir respuesta usando solo lo que viene de la BD
    # Se asume que lo que guardaste desde el frontend son los valores "grados_actuales", "repeticiones", etc.
    respuesta = {
        "accion": "normal" if estado.grados_actuales == 0 and estado.repeticiones == 0 else "iniciar",
        "grados": estado.grados_actuales,
        "repeticiones": estado.repeticiones,
        "stop_grados": estado.stop_grados,
        "modo": estado.modo
    }

    # Reiniciar valores para que no se reenvíen
    estado.activo = False
    estado.grados_actuales = 0
    estado.repeticiones = 0
    estado.stop_grados = 0
    estado.modo = "normal"
    estado.save()

    return JsonResponse(respuesta)

@csrf_exempt
def comando_esp_detener(request):
    numero = request.GET.get('maquina')
    if not numero:
        return JsonResponse({"error": "Falta parámetro 'maquina'"}, status=400)

    # Obtener o crear máquina
    maquina, _ = Maquinas.objects.get_or_create(
        numero=numero,
        defaults={'ip': '0.0.0.0'}
    )

    # Obtener o crear estado de la máquina
    estado, _ = EstadoMaquina.objects.get_or_create(
        maquina=maquina,
        defaults={
            'activo': False,
            'grados_actuales': 0,
            'repeticiones': 0,
            'stop_grados': 0,
            'modo': 'normal',
            'conectado': True
        }
    )

    # Construir respuesta: DETENER con todos los valores en 0
    respuesta = {
        "accion": "detener",
        "grados": 0,
        "repeticiones": 0,
        "stop_grados": 0,
        "modo": "normal"
    }

    # Reiniciamos todo para que no se vuelva a enviar
    estado.activo = False
    estado.grados_actuales = 0
    estado.repeticiones = 0
    estado.stop_grados = 0
    estado.modo = "normal"
    estado.save()

    return JsonResponse(respuesta)


