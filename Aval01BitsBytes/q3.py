arquivo = "IMG_20250509_184205.jpg"

with open(arquivo, "rb") as f:
    f.read(2)  # ignora SOI
    while True:
        marker = f.read(2)
        if len(marker) < 2: exit("Fim do arquivo sem encontrar APP1.")
        if marker[0] != 0xFF: continue
        if marker == b'\xFF\xE1':
            size = int.from_bytes(f.read(2), 'big')
            app1 = f.read(size - 2)
            break
        else:
            sz = int.from_bytes(f.read(2), 'big')
            f.read(sz - 2)

# Verifica se há dados suficientes
if len(app1) < 18:
    exit("APP1 muito curto")

qtd = int.from_bytes(app1[16:18], 'big')
print(f"Quantidade de metadados: {qtd}")

pos = 18
largura = altura = None

for _ in range(qtd):
    if pos + 12 > len(app1): break
    tag = int.from_bytes(app1[pos:pos+2], 'big')
    tipo = int.from_bytes(app1[pos+2:pos+4], 'big')
    n = int.from_bytes(app1[pos+4:pos+8], 'big')
    val_or_offset = int.from_bytes(app1[pos+8:pos+12], 'big')

    if tag == 0x0100 or tag == 0x0101:
        if tipo == 3 and n == 1:
            valor = val_or_offset >> 16  # unsigned short no início
        else:
            offset = val_or_offset + 12
            if offset + 4 <= len(app1):
                valor = int.from_bytes(app1[offset:offset+4], 'big')
            else:
                valor = None

        if tag == 0x0100: largura = valor
        elif tag == 0x0101: altura = valor

    pos += 12

print(f"Largura da imagem: {largura or 'não encontrada'} px")
print(f"Altura da imagem: {altura or 'não encontrada'} px")
