import socket
import threading
import os
import glob
import hashlib

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 5000
BUFFER_SIZE = 1024
SERVER_DIR = 'arquivos'

if not os.path.exists(SERVER_DIR):
    os.makedirs(SERVER_DIR)

def listar_arquivos():
    arquivos = os.listdir(SERVER_DIR)
    resposta = "OKDIR"
    for nome in arquivos:
        caminho = os.path.join(SERVER_DIR, nome)
        if os.path.isfile(caminho):
            tamanho = os.path.getsize(caminho)
            resposta += f"|{nome}|{tamanho}"
    return resposta if resposta != "OKDIR" else "ERRO|Nenhum arquivo encontrado"

def enviar_arquivo(conn, nome):
    caminho = os.path.join(SERVER_DIR, nome)
    if not os.path.isfile(caminho):
        conn.sendall(f"ERRODOW|Arquivo não encontrado\n".encode())
        return
    try:
        tamanho = os.path.getsize(caminho)
        conn.sendall(f"OKDOW|{nome}|{tamanho}\n".encode())
        with open(caminho, 'rb') as f:
            while True:
                dados = f.read(BUFFER_SIZE)
                if not dados:
                    break
                conn.sendall(dados)
    except:
        conn.sendall(f"ERRODOW|Erro ao enviar arquivo\n".encode())

def calcular_md5(nome, pos):
    caminho = os.path.join(SERVER_DIR, nome)
    if not os.path.isfile(caminho):
        return "ERROMD5|Arquivo não encontrado"
    try:
        with open(caminho, 'rb') as f:
            dados = f.read(int(pos))
        hash_md5 = hashlib.md5(dados).hexdigest()
        return f"OKMD5|{hash_md5}"
    except:
        return "ERROMD5|Erro ao calcular hash"

def continuar_download(conn, nome, pos, hash_cliente):
    caminho = os.path.join(SERVER_DIR, nome)
    if not os.path.isfile(caminho):
        conn.sendall("ERRODRA|Arquivo não encontrado\n".encode())
        return
    try:
        with open(caminho, 'rb') as f:
            dados = f.read(int(pos))
            hash_local = hashlib.md5(dados).hexdigest()
            if hash_local != hash_cliente:
                conn.sendall("ERRODRA|Hash incorreto\n".encode())
                return
            restante = f.read()
        conn.sendall(f"OKDRA|{len(restante)}\n".encode())
        conn.sendall(restante)
    except:
        conn.sendall("ERRODRA|Erro ao continuar download\n".encode())

def download_multiplos(conn, mascara):
    caminho_busca = os.path.join(SERVER_DIR, mascara)
    arquivos = glob.glob(caminho_busca)
    arquivos = [f for f in arquivos if os.path.isfile(f)]
    if not arquivos:
        conn.sendall("ERRODMA|Nenhum arquivo encontrado\n".encode())
        return
    conn.sendall(f"OKDMA|{len(arquivos)}\n".encode())
    for caminho in arquivos:
        nome = os.path.basename(caminho)
        tamanho = os.path.getsize(caminho)
        conn.sendall(f"OKDOW|{nome}|{tamanho}\n".encode())
        with open(caminho, 'rb') as f:
            while True:
                dados = f.read(BUFFER_SIZE)
                if not dados:
                    break
                conn.sendall(dados)

def tratar_cliente(conn, addr):
    print(f"[+] Conectado: {addr}")
    try:
        while True:
            requisicao = conn.recv(BUFFER_SIZE).decode().strip()
            if not requisicao:
                break
            partes = requisicao.split('|')
            comando = partes[0].upper()

            if comando == 'DIR':
                resposta = listar_arquivos()
                conn.sendall(f"{resposta}\n".encode())
            elif comando == 'DOW' and len(partes) == 2:
                enviar_arquivo(conn, partes[1])
            elif comando == 'MD5' and len(partes) == 3:
                resposta = calcular_md5(partes[1], partes[2])
                conn.sendall(f"{resposta}\n".encode())
            elif comando == 'DRA' and len(partes) == 4:
                continuar_download(conn, partes[1], partes[2], partes[3])
            elif comando == 'DMA' and len(partes) == 2:
                download_multiplos(conn, partes[1])
            elif comando == 'SAIR':
                conn.sendall("BYE\n".encode())
                break
            else:
                conn.sendall("ERRO|Comando inválido ou formato incorreto\n".encode())
    except Exception as e:
        print(f"[!] Erro com {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Desconectado: {addr}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[+] Servidor iniciado em {HOST}:{PORT}")

    while True:
        conn, addr = servidor.accept()
        thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    iniciar_servidor()