este es un sistema de tele-rehabilitacion con la cual se busca ayudara al mayor numero de personas en rehabilitacion.

este sistema se basa en una esp32 y un servidor en django con un tunel atraves de cloudflare, la combinacion de estos sistemas crean 
rehabilitatec este sistema permite a los doctores mantener y guiar el proceso de rehabilitacion a raves de esta pagona ademas que hemos 
desarollado un rehabilitador especifico para cuariceps el cual puede ser tele_dirigido desde cualquier parte del mundo, esta pagina web guarda datos del paciente 
al mismo tiempo que es capaz de monitorear su progreso y darle es informacion a un doctor capacitado.

aunque no es la version finalizada se planea poder donarlo a centros de rehabilitacion de todo mexico y que cada centro pueda llevarlo a las 
casas de las personas que lo necesiten asi logrando una rehabilitacionde calidad desde su casa, esta tecnologia ayudar a personas de la 3 edad que ya no
pueda salir de sus casas a tener una rehablitacion pos operatoria o simplemente para mantener un estado fisico desde sus casas.

etse sistema esta basado en una esp32 que atraves de un conjunto de reles y un driver para motores trifasicos controlamos atraves de la
red a un motor trifasico que ejecuta el movimiento.

la esp32 atraves de wifi manda una solicitud POST y GET a el backend que es manejado por django la cual es la encargada de gestionar las solicitudes
y peticiones que llegan al servidor y usamos cloudflare para evitar tener que usar un modem estativo y nos permite tener una capa extra de seguridad en 
nuestor proyecto, en la solicitud POST actualiza su estado actual y informacion basica como el nombre de esa maquina y su estado actual (puede ser ser activo que es cuando esta ejecutando 
una accion o un movimiento o inactivo que es cuando la maquina esta en reposo pero conecta a internet) y en la peticion GET pide al servidor 
si hay actualizacion de la informacion (en la base de datos se crea un perfil para cada maquina en el que se guardan las repeticiones, los grados de las repeticiones
si es necesario activarlo o solo guardar la infomacion, etc) despues de verificar si hay actualizacion en caso de o haberla el servidor regresa que no hay y la 
esp32 lo vuelve a intentar en cierto tiempo, en caso contrario de que si haya una actualizacion en el perfil de la maquina la esp32 pide y recibe esos
datos y ejecuta el movimiento en caso de que se le indique, lugo se reinicia ele stado del perfil para que no se repita y al perfil del paciente 
se le agrega una sesion a un contador que esta incuye.

ademas este dispositivo es de bajo costo, en su prototipado llevamos un gasto dde alredor de 6000 pesos mexicanos que es un precion barato para este tipo de dispositivos
se planea que este sea un rehabilitador que se pueda construir con materiales reciclados en su mayoria para que sea un producto con bajo costo de produccion
e incluso amigable con el medio ambiente 

aunque esta no es la verision final y no todas las funciones estan detalladas esta es una version mejorable y escalable para que cada persona que lo necesite
tenga uno en su casa.

a futuro se planea integrar un registro para que los pacientes puedan checar su progreso y sus recomendaciones desde la propia pagina web
se planea que cada person pueda monitoriear su avance en tiempo real.

por: Nestor Tec y Williams Cauntu

![WhatsApp Image 2026-01-31 at 12 41 43 AM](https://github.com/user-attachments/assets/28128db2-f4ce-4bc0-807b-44a9b4e08d1c)

