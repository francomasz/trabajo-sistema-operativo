import socket
import os
import time

class ClienteArchivos:
    def __init__(self, host='localhost', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.directorio_archivos = "archivos_cliente"
        self.crear_directorio()
        self.socket = None
        
    def crear_directorio(self):
        """Crea el directorio para almacenar archivos si no existe"""
        if not os.path.exists(self.directorio_archivos):
            os.makedirs(self.directorio_archivos)
            print(f"Directorio '{self.directorio_archivos}' creado")
    
    def conectar_servidor(self):
        """Establece conexión con el servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            print(f"Conectado al servidor {self.host}:{self.puerto}")
            return True
        except Exception as e:
            print(f"Error al conectar con el servidor: {e}")
            return False
    
    def enviar_archivo(self, nombre_archivo):
        """Envía un archivo al servidor"""
        try:
            ruta_archivo = os.path.join(self.directorio_archivos, nombre_archivo)
            
            if not os.path.exists(ruta_archivo):
                print(f"El archivo '{nombre_archivo}' no existe en el directorio cliente")
                return
            
            print(f"Preparando para enviar: {nombre_archivo}")
            
            # Lee el contenido del archivo primero
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
            
            print(f"Contenido del archivo ({len(contenido)} caracteres):")
            print(contenido[:100] + "..." if len(contenido) > 100 else contenido)
            
            # Envia comando al servidor
            comando = f"ENVIAR {nombre_archivo}"
            self.socket.send(comando.encode('utf-8'))
            
            # Pequeña pausa para asegurar que el servidor procese el comando
            time.sleep(0.1)
            
            # Envia el contenido del archivo
            self.socket.send(contenido.encode('utf-8'))
            
            # Recibe confirmación
            respuesta = self.socket.recv(1024).decode('utf-8')
            print(f"Respuesta del servidor: {respuesta}")
                
        except Exception as e:
            print(f"Error al enviar archivo: {e}")
    
    def recibir_archivo(self, nombre_archivo):
        """Recibe un archivo del servidor"""
        try:
            # Envia comando al servidor
            comando = f"RECIBIR {nombre_archivo}"
            self.socket.send(comando.encode('utf-8'))
            
            # Espera respuesta del servidor
            respuesta = self.socket.recv(1024).decode('utf-8')
            
            if respuesta == "EXISTE":
                # Recibe el contenido del archivo
                contenido = self.socket.recv(4096).decode('utf-8')
                
                # Guarda el archivo localmente
                ruta_archivo = os.path.join(self.directorio_archivos, nombre_archivo)
                with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                    archivo.write(contenido)
                
                print(f"Archivo '{nombre_archivo}' recibido y guardado exitosamente")
                
            elif respuesta == "NO_EXISTE":
                print(f"El archivo '{nombre_archivo}' no existe en el servidor")
            else:
                print(f"Error: {respuesta}")
                
        except Exception as e:
            print(f"Error al recibir archivo: {e}")
    
    def listar_archivos_servidor(self):
        """Solicita y muestra la lista de archivos del servidor"""
        try:
            self.socket.send("LISTAR".encode('utf-8'))
            lista = self.socket.recv(4096).decode('utf-8')
            print("\n--- Archivos disponibles en el servidor ---")
            print(lista)
            print("--------------------------------------------")
        except Exception as e:
            print(f"Error al listar archivos: {e}")
    
    def listar_archivos_locales(self):
        """Muestra la lista de archivos locales"""
        try:
            archivos = os.listdir(self.directorio_archivos)
            archivos_txt = [archivo for archivo in archivos if archivo.endswith('.txt')]
            
            print("\n--- Archivos disponibles localmente ---")
            if archivos_txt:
                for archivo in archivos_txt:
                    print(archivo)
            else:
                print("No hay archivos .txt disponibles")
            print("----------------------------------------")
        except Exception as e:
            print(f"Error al listar archivos locales: {e}")
    
    def mostrar_menu(self):
        """Muestra el menú de opciones"""
        print("\n" + "="*50)
        print("          CLIENTE DE TRANSFERENCIA DE ARCHIVOS")
        print("="*50)
        print("1. Enviar archivo al servidor")
        print("2. Recibir archivo del servidor")
        print("3. Listar archivos en el servidor")
        print("4. Listar archivos locales")
        print("5. Salir")
        print("="*50)
    
    def ejecutar(self):
        """Ejecuta la aplicación cliente"""
        if not self.conectar_servidor():
            return
        
        try:
            while True:
                self.mostrar_menu()
                opcion = input("Seleccione una opción (1-5): ").strip()
                
                if opcion == "1":
                    self.listar_archivos_locales()
                    nombre_archivo = input("Ingrese el nombre del archivo a enviar: ").strip()
                    if nombre_archivo:
                        self.enviar_archivo(nombre_archivo)
                
                elif opcion == "2":
                    self.listar_archivos_servidor()
                    nombre_archivo = input("Ingrese el nombre del archivo a recibir: ").strip()
                    if nombre_archivo:
                        self.recibir_archivo(nombre_archivo)
                
                elif opcion == "3":
                    self.listar_archivos_servidor()
                
                elif opcion == "4":
                    self.listar_archivos_locales()
                
                elif opcion == "5":
                    self.socket.send("SALIR".encode('utf-8'))
                    print("Desconectando del servidor...")
                    break
                
                else:
                    print("Opción no válida. Intente nuevamente.")
                    
        except Exception as e:
            print(f"Error en el cliente: {e}")
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    cliente = ClienteArchivos()
    cliente.ejecutar()