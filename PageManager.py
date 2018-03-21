# padrão de envio = [codigo do comando, nome da tabela, [valores de entrada (delete não precisa ser em lista)]]

def Read(cmd):
    if(cmd[0] == 0):
    	CreateTable(cmd[1:])
    if(cmd[0] == 1):
    	InsertInto(cmd[1:])
    if(cmd[0] == 2):
    	DeleteFrom(cmd[1:])

def MetadataPage(name): #verifica se a página já existe
	try:
		file = open('__pages__/'+name+'meta.dat', 'rb')
		file.close()
		return False
	except IOError:
		return True

def CreateTable(cmd):
	if(not MetadataPage(cmd[0])): #se já existe n cria denovo e retorna nada
		print("Tabela "+cmd[0]+" já existente.")
		return
	values = []
	for a in cmd[1:]: #pega os atributos do comando
		v = []
		if(a[0] == 'int'): #caso o atributo seja inteiro
			v.append(1)
			v.append(4) #tamanho fixo, mas será desconsiderado
			v.append(len(a[1])) #tamanho do nome do campo
			v.append(a[1]) #nome do campo
		elif(a[0:4] == 'char'): #caso seja char
			v.append(2) 
			v.append(int((a[0].split('[')[1].split(']'))[0])) #tamanho do char
			v.append(len(a[1]))#tamanho do nome do campo
			v.append(a[1])#nome do campo
		else: #caso seja varchar
			v.append(3)
			v.append(int((a[0].split('[')[1].split(']'))[0])) #tamanho do char
			v.append(len(a[1])) #tamanho do nome do campo
			v.append(a[1]) #nome do campo
		values.append(v)
	CreateMetaPage(cmd[0],values)

def InsertInto(cmd):
	CreateFrame(cmd[0], cmd[1:])

def DeleteFrom(cmd):
	pass

def List(cmd, pageName):
	with open('page0.dat', 'rb') as file:
	    byte = file.read(1)
	    while byte != b'':
	        print(byte)
	        byte = file.read(1)

# PAGES/FRAMES SECTION #

def CreatePage(pageName,offset):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'wb')
		pageLen = 8*1024 # 8KB
		special = 4 # bytes do frame especial
		headerBytes = 12
		# criando o header
		pd_tli = 0 # TLI da última mudança
		pd_lower = headerBytes # Offset para começar o espaço livre
		pd_upper = pageLen - special - 1 # Offset ao fim do espaço livre
		pd_special = pageLen - special # Deslocamento para o início do espaço especial
		pd_tlist = 0
		file.write(pd_tli.to_bytes(4,'big'))
		file.write(pd_lower.to_bytes(2,'little'))
		file.write(pd_upper.to_bytes(2,'little'))
		file.write(pd_special.to_bytes(2,'little'))
		file.write(pd_tlist.to_bytes(2,'little'))
		# inicializando espaços vazios
		free = pageLen - headerBytes - special # bytes livres
		file.write(bytes(free))
		# alocando frame especial
		file.write(bytes(special))
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+str(offset)+'.dat')
		return False

def CreateFrame(pageName, values):
	try:
		file = open('__pages__/'+pageName+'.dat', 'r+b')
		# calculando somatório de bytes
		n = 0
		for a in values:
			if(isinstance(a, str)):
				n += len(a)
			else:
				n += 4
		# gerenciando pd_upper
		file.seek(16) # posição de início do pd_upper
		i = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
		file.seek(16) # posição de início do pd_upper
		file.write(int(i+4).to_bytes(2, 'little')) # atualizando o ponteiro
		# criando o item
		file.seek(i)
		file.write(n.to_bytes(4,'little'))

		# gerenciando pd_lower
		file.seek(18) # posição de início do pd_lower
		i = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar a próxima tupla
		file.seek(18) # posição de início do pd_lower
		file.write((i+4).to_bytes(2, 'little')) # atualizando o ponteiro
		# criando a tupla
		file.seek(i)
		for a in values:
			if(isinstance(a, str)):
				file.write(a.encode())
			else:
				file.write(a.to_bytes(4, 'litte'))

		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error opening '+pageName+'.dat')
		return False

def InsertInto(cmd): #ainda não existe eauhhaehauehuea, mas verifica se a tabela existe pra inserir
	try:
		file = open('__pages__/'+cmd[0]+'meta.dat', 'rb')
		return
	except IOError:
		print("\nTabela "+cmd[0]+" não encontrada.")

	
	return

def CreateMetaPage(pageName,attr): # [[type,typeLen,nameLen,name],...] | cria a página com os campos da tupla
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'wb')
		# pega os atributos já verificados e insere um por vez
		for a in attr:
			file.write(a[0].to_bytes(1,'little')) #tipo do campo
			file.write(a[1].to_bytes(1,'little')) #tamanho do campo
			file.write(a[2].to_bytes(1,'little')) #tamanho do nome
			file.write(a[3].encode()) #pra string
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+'meta.dat') #não deu pra criar a página
		return False

def getMeta(pageName): #pegar os atributos da tabela
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'rb')
		attr = []
		a = int.from_bytes(file.read(1), byteorder='little') #tipo do primeiro campo, se não existir retorna um vetor vazio
		while(a):
			v = []			
			v.append(a)
			a = int.from_bytes(file.read(1), byteorder='little') #tamanho do campo
			v.append(a)
			a = int.from_bytes(file.read(1), byteorder='little')#tamanho do nome do campo
			a = file.read(a).decode()
			v.append(a)
			attr.append(v)
			a = int.from_bytes(file.read(1), byteorder='little') #nome do campo
		print(attr) #só teste msm
		file.close()
		return attr
	except IOError:
		print('Error opening '+pageName+'meta.dat') #página não existe
		return False