# Abrir o arquivo JPEG e ler os 6 primeiros bytes
with open("IMG_20250509_184205.jpg", "rb") as f:
    header = f.read(6)

# Extrair os bytes 4 e 5 que indicam o tamanho dos metadados (app1DataSize)
app1DataSize = int.from_bytes(header[4:6], byteorder='big')
print(f"Tamanho dos metadados (app1DataSize): {app1DataSize} bytes")

# Abrir novamente o arquivo
with open("IMG_20250509_184205.jpg", "rb") as f:
    f.read(4)  # Ignorar os 4 primeiros bytes
    app1Data = f.read(app1DataSize)  # Ler os metadados

# Extrair os 2 bytes na posição 16, que indicam a quantidade de metadados
qtd_metadados = int.from_bytes(app1Data[16:18], byteorder='big')
print(f"Quantidade de metadados: {qtd_metadados}")

# Variáveis para armazenar a largura e altura encontradas
largura = None
altura = None

# Começa na posição 18 onde começam os metadados
pos = 18

# Constantes dos códigos de metadado
LARGURA_TAG = 0x0100
ALTURA_TAG = 0x0101

# Laço para percorrer todos os metadados
for i in range(qtd_metadados):
    tag = int.from_bytes(app1Data[pos:pos+2], byteorder='big')
    tipo = int.from_bytes(app1Data[pos+2:pos+4], byteorder='big')
    repeticoes = int.from_bytes(app1Data[pos+4:pos+8], byteorder='big')
    valor = int.from_bytes(app1Data[pos+8:pos+12], byteorder='big')

    # Verifica se o tag corresponde à largura ou altura
    if tag == LARGURA_TAG:
        largura = valor
    elif tag == ALTURA_TAG:
        altura = valor

    # Avança 12 bytes para o próximo metadado
    pos += 12

# Exibe os resultados
print(f"Largura da imagem: {largura} pixels")
print(f"Altura da imagem: {altura} pixels")
