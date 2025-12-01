import time
import multiprocessing

# Esta función simula una tarea pesada que tarda 1 segundo en completarse
def tarea_pesada(numero):
    print(f"Procesando el dato: {numero}")
    time.sleep(1) # Duerme 1 segundo simulando calculo complejo
    return numero * numero

if __name__ == "__main__":
    datos = [1, 2, 3, 4, 5] # Tenemos 5 datos para procesar

    print("--- INICIO EJECUCIÓN SECUENCIAL ---")
    inicio_secuencial = time.time()
    
    # Ejecución uno por uno
    resultados_sec = []
    for d in datos:
        resultados_sec.append(tarea_pesada(d))
        
    fin_secuencial = time.time()
    print(f"Tiempo Secuencial: {fin_secuencial - inicio_secuencial:.2f} segundos")
    print("-" * 30)

    print("\n--- INICIO EJECUCIÓN PARALELA ---")
    inicio_paralelo = time.time()
    
    # Creamos un 'Pool' (grupo) de procesos. 
    # Python detectará cuántos núcleos tiene tu CPU y usará varios a la vez.
    with multiprocessing.Pool() as pool:
        # 'map' reparte los datos entre los núcleos disponibles automáticamente
        resultados_par = pool.map(tarea_pesada, datos)
        
    fin_paralelo = time.time()
    print(f"Tiempo Paralelo: {fin_paralelo - inicio_paralelo:.2f} segundos")
    
    print("-" * 30)
    print("Conclusión: La versión paralela es mucho más rápida.")