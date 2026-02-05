import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generar_datos_maquina():
    # 1. Configuración de tiempo: 1 semana de datos, registro cada hora
    fecha_inicio = datetime.now() - timedelta(days=7)
    rango_tiempo = pd.date_range(start=fecha_inicio, periods=168, freq='h') # 168 horas en una semana

    data = []

    for timestamp in rango_tiempo:
        # 2. Simular estado de la máquina
        # Probabilidades: 80% Operando, 15% Paro (Setup/Espera), 5% Falla
        estado = np.random.choice(['Operando', 'Paro', 'Falla'], p=[0.80, 0.15, 0.05])
        
        id_maquina = "MAQ-01"
        
        if estado == 'Operando':
            # Si opera, produce entre 40 y 65 piezas (algunas veces supera la meta, otras no)
            piezas_producidas = random.randint(40, 65)
            # De esas, entre 0 y 5 salen defectuosas
            piezas_defectuosas = random.randint(0, 5)
        else:
            # Si está parada o en falla, no produce nada
            piezas_producidas = 0
            piezas_defectuosas = 0

        data.append([timestamp, id_maquina, estado, piezas_producidas, piezas_defectuosas])

    # 3. Crear DataFrame y guardar a CSV
    df = pd.DataFrame(data, columns=['Timestamp', 'ID_Maquina', 'Estado', 'Piezas_Producidas', 'Piezas_Defectuosas'])
    
    # Guardamos el archivo para que la App lo lea después
    df.to_csv('OEE/datos_produccion.csv', index=False)
    print("✅ Archivo 'datos_produccion.csv' generado con éxito.")

if __name__ == "__main__":
    generar_datos_maquina()