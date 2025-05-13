def ip_str_para_int(ip_str):
    #Converte um IP em string (ex: '192.168.0.1') para um inteiro de 32 bits
    octetos = list(map(int, ip_str.split('.')))
    ip_int = (octetos[0] << 24) | (octetos[1] << 16) | (octetos[2] << 8) | octetos[3]
    return ip_int

def int_para_ip_str(ip_int):
    # Converte um inteiro de 32 bits para string no formato de IP
    return '.'.join(str((ip_int >> (8 * i)) & 0xFF) for i in reversed(range(4)))

def calcular():
    ip_str = input("Digite o IP (ex: 200.17.143.131): ")
    mascara_bits = int(input("Digite a máscara em bits (ex: 18): "))

    # Converte o IP para inteiro
    ip = ip_str_para_int(ip_str)

    # Cria a máscara em inteiro (ex: 18 bits 1 seguidos de 14 bits 0)
    mascara = (0xFFFFFFFF << (32 - mascara_bits)) & 0xFFFFFFFF

    # Endereço da rede: IP & máscara
    endereco_rede = ip & mascara

    # Endereço de broadcast: IP | bits de host todos 1
    endereco_broadcast = endereco_rede | (~mascara & 0xFFFFFFFF)

    # Gateway: último IP válido (broadcast - 1)
    gateway = endereco_broadcast - 1

    # Número de hosts válidos
    hosts_validos = (2 ** (32 - mascara_bits)) - 2

    # Impressão dos resultados
    print("\nResultados:")
    print("a) Endereço de rede:     ", int_para_ip_str(endereco_rede))
    print("b) Endereço de broadcast:", int_para_ip_str(endereco_broadcast))
    print("c) Gateway:              ", int_para_ip_str(gateway))
    print("d) Total de hosts válidos:", hosts_validos)

# Chamada principal
calcular()
