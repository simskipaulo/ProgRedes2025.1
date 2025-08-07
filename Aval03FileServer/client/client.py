import socket
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
BUFFER_SIZE = 1024
CLIENT_DIR = 'arquivos'

if not os.path.exists(CLIENT_DIR):
    os.makedirs(CLIENT_DIR)

def receber_linha(sock):
    dados = b''
    while not dados.endswith(b'\n'):
        parte = sock.recv(1)
        if not parte:
            break
        dados += parte
    return dados.decode().strip()

def receber_bytes(sock, tamanho):
    dados = b''
    while len(dados) < tamanho:
        parte = sock.recv(min(BUFFER_SIZE, tamanho - len(dados)))
        if not parte:
            break
        dados += parte
    return dados

def comando_dir(sock):
    sock.sendall(b'DIR\n')
    resposta = receber_linha(sock)
    print("[DIR] Resposta do servidor:")
    if resposta.startswith("OKDIR"):
        partes = resposta.split('|')[1:]
        for i in range(0, len(partes), 2):
            print(f"- {partes[i]} ({partes[i+1]} bytes)")
    else:
        print(resposta)

def comando_dow(sock):
    nome = input("Nome do arquivo para baixar: ").strip()
    sock.sendall(f"DOW|{nome}\n".encode())
    resposta = receber_linha(sock)
    if resposta.startswith("OKDOW"):
        _, nome_arq, tamanho = resposta.split('|')
        tamanho = int(tamanho)
        dados = receber_bytes(sock, tamanho)
        caminho = os.path.join(CLIENT_DIR, nome_arq)
        with open(caminho, 'wb') as f:
            f.write(dados)
        print(f"[DOW] Arquivo '{nome_arq}' salvo com sucesso.")
    else:
        print("[DOW]", resposta)

def comando_md5(sock):
    nome = input("Nome do arquivo: ").strip()
    pos = input("Quantidade de bytes para o hash: ").strip()
    sock.sendall(f"MD5|{nome}|{pos}\n".encode())
    resposta = receber_linha(sock)
    print("[MD5]", resposta)

def comando_dra(sock):
    nome = input("Nome do arquivo para continuar: ").strip()
    caminho = os.path.join(CLIENT_DIR, nome)
    if not os.path.exists(caminho):
        print("[DRA] Arquivo não existe localmente.")
        return
    pos = os.path.getsize(caminho)
    with open(caminho, 'rb') as f:
        dados = f.read()
    hash_local = hashlib.md5(dados).hexdigest()
    sock.sendall(f"DRA|{nome}|{pos}|{hash_local}\n".encode())
    resposta = receber_linha(sock)
    if resposta.startswith("OKDRA"):
        _, tamanho = resposta.split('|')
        restante = receber_bytes(sock, int(tamanho))
        with open(caminho, 'ab') as f:
            f.write(restante)
        print("[DRA] Download continuado com sucesso.")
    else:
        print("[DRA]", resposta)

def comando_dma(sock):
    mascara = input("Informe a máscara (ex: *.txt): ").strip()
    sock.sendall(f"DMA|{mascara}\n".encode())
    resposta = receber_linha(sock)
    if not resposta.startswith("OKDMA"):
        print("[DMA]", resposta)
        return

    qtd = int(resposta.split('|')[1])
    for _ in range(qtd):
        cabecalho = receber_linha(sock)
        if not cabecalho.startswith("OKDOW"):
            print("[DMA] Erro em um dos arquivos:", cabecalho)
            continue
        _, nome_arq, tamanho = cabecalho.split('|')
        tamanho = int(tamanho)
        caminho = os.path.join(CLIENT_DIR, nome_arq)
        if os.path.exists(caminho):
            resp = input(f"'{nome_arq}' já existe. Sobrescrever? (s/n): ").strip().lower()
            if resp != 's':
                sock.recv(tamanho)  # descarta dados
                continue
        dados = receber_bytes(sock, tamanho)
        with open(caminho, 'wb') as f:
            f.write(dados)
        print(f"[DMA] '{nome_arq}' salvo com sucesso.")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(f"[+] Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
        except:
            print("[!] Não foi possível conectar ao servidor.")
            return

        while True:
            print("\nComandos: DIR, DOW, MD5, DRA, DMA, SAIR")
            cmd = input("Digite um comando: ").strip().upper()

            if cmd == 'DIR':
                comando_dir(sock)
            elif cmd == 'DOW':
                comando_dow(sock)
            elif cmd == 'MD5':
                comando_md5(sock)
            elif cmd == 'DRA':
                comando_dra(sock)
            elif cmd == 'DMA':
                comando_dma(sock)
            elif cmd == 'SAIR':
                sock.sendall(b'SAIR\n')
                print("[-] Encerrando conexão...")
                break
            else:
                print("[!] Comando inválido.")

if __name__ == '__main__':
    import hashlib
    main()
