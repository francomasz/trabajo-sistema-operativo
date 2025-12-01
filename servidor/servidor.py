import socket
import os
import threading

class ServidorArchivos:
    def __init__(self, host='localhost', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.directorio_archivos = "archivos_servidor"
        self.crear_directorio()
        
    def crear_directorio(self):
        """Crea el directorio para almacenar archivos si no existe"""
        if not os.path.exists(self.directorio_archivos):
            os.makedirs(self.directorio_archivos)
            print(f"Directorio '{self.directorio_archivos}' creado")
    
    def manejar_cliente(self, cliente_socket, direccion):
        """Maneja la comunicación con un cliente específico"""
        print(f"Conexión establecida con {direccion}")
        
        try:
            while True:
                # Recibe comando del cliente
                comando = cliente_socket.recv(1024).decode('utf-8')
                
                if not comando:
                    break
                    
                print(f"Comando recibido: {comando}")
                
                if comando.startswith("ENVIAR"):
                    # Formato: ENVIAR nombre_archivo
                    _, nombre_archivo = comando.split(" ", 1)
                    self.recibir_archivo(cliente_socket, nombre_archivo)
                    
                elif comando.startswith("RECIBIR"):
                    # Formato: RECIBIR nombre_archivo
                    _, nombre_archivo = comando.split(" ", 1)
                    self.enviar_archivo(cliente_socket, nombre_archivo)
                    
                elif comando == "LISTAR":
                    self.listar_archivos(cliente_socket)
                    
                elif comando == "SALIR":
                    print(f"Cliente {direccion} se desconectó")
                    break
                    
        except Exception as e:
            print(f"Error con cliente {direccion}: {e}")
        finally:
            cliente_socket.close()
    
    def recibir_archivo(self, cliente_socket, nombre_archivo):
        """Recibe un archivo del cliente"""
        try:
            ruta_archivo = os.path.join(self.directorio_archivos, nombre_archivo)
            
            # Envia confirmación inmediatamente
            cliente_socket.send("LISTO".encode('utf-8'))
            
            # Recibe el contenido del archivo (sin esperar otra confirmación)
            contenido = cliente_socket.recv(4096).decode('utf-8')
            
            # Guarda el archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write(contenido)
            
            mensaje = f"Archivo '{nombre_archivo}' recibido exitosamente"
            cliente_socket.send(mensaje.encode('utf-8'))
            print(mensaje)
            
        except Exception as e:
            error_msg = f"Error al recibir archivo: {e}"
            cliente_socket.send(error_msg.encode('utf-8'))
    
    def enviar_archivo(self, cliente_socket, nombre_archivo):
        """Envía un archivo al cliente"""
        try:
            ruta_archivo = os.path.join(self.directorio_archivos, nombre_archivo)
            
            if os.path.exists(ruta_archivo):
                # Envia confirmación
                cliente_socket.send("EXISTE".encode('utf-8'))
                
                # Lee y envia el contenido del archivo
                with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                    contenido = archivo.read()
                
                cliente_socket.send(contenido.encode('utf-8'))
                print(f"Archivo '{nombre_archivo}' enviado exitosamente")
            else:
                cliente_socket.send("NO_EXISTE".encode('utf-8'))
                
        except Exception as e:
            error_msg = f"Error al enviar archivo: {e}"
            cliente_socket.send(error_msg.encode('utf-8'))
    
    def listar_archivos(self, cliente_socket):
        """Envía la lista de archivos disponibles al cliente"""
        try:
            archivos = os.listdir(self.directorio_archivos)
            archivos_txt = [archivo for archivo in archivos if archivo.endswith('.txt')]
            
            if archivos_txt:
                lista = "\n".join(archivos_txt)
                cliente_socket.send(lista.encode('utf-8'))
            else:
                cliente_socket.send("No hay archivos .txt disponibles".encode('utf-8'))
                
        except Exception as e:
            error_msg = f"Error al listar archivos: {e}"
            cliente_socket.send(error_msg.encode('utf-8'))
    
    def iniciar_servidor(self):
        """Inicia el servidor y acepta conexiones"""
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            servidor_socket.bind((self.host, self.puerto))
            servidor_socket.listen(5)
            print(f"Servidor escuchando en {self.host}:{self.puerto}")
            print("Directorio de archivos:", self.directorio_archivos)
            print("Esperando conexiones...")
            
            while True:
                cliente_socket, direccion = servidor_socket.accept()
                
                # Crea un hilo para cada cliente
                hilo_cliente = threading.Thread(
                    target=self.manejar_cliente, 
                    args=(cliente_socket, direccion)
                )
                hilo_cliente.daemon = True
                hilo_cliente.start()
                
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario")
        except Exception as e:
            print(f"Error en el servidor: {e}")
        finally:
            servidor_socket.close()

if __name__ == "__main__":
    servidor = ServidorArchivos()
    servidor.iniciar_servidor()