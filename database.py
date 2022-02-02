import sqlite3

def exists_table(db_cursor, name):
	query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
	return db_cursor.execute(query, (name,)).fetchone() is not None

def existing_tables(db_cursor):
	query = "SELECT * FROM sqlite_master WHERE type='table'"
	return [x[2] for x in db_cursor.execute(query).fetchall()]


def matrix_to_db(filename, tablename): # TEMPORARIA
	data = []
	with open("filmes_cup.txt", encoding="utf8") as f:
		for line in f:
			data.append(line.replace('\n', ''))

	matrix = []
	for movie in data:
		matrix.append((movie, "", 0, "", 1))

	cols = """(
		title text,
		imdbId text,
		year integer,
		genres text,
		priority integer
	)"""

	mydb = SQLdb(filename)
	mydb.create_table(tablename, cols)
	mydb.add_many_to_table(matrix)
	for item in mydb.get_table(limit=2000):
		print(item)


class SQLdb():
	# CRIA CONEXÃO E CURSOR
	def __init__(self, file="database.db", table=None):
		self.file = file
		self.con = sqlite3.connect(file)
		self.cursor = self.con.cursor()

		if table:
			self.load_table(table)


	def _get_placeholder(self):
		query = f"SELECT COUNT(*) FROM pragma_table_info('{self.name}')"; 
		num_cols = self.cursor.execute(query).fetchone()[0]

		placeholder = f"({','.join(['?' for x in range(num_cols)])})"

		# query = "SELECT * FROM sqlite_master WHERE type='table' and name = ?"
		# cols = self.cursor.execute(query, (self.name,)).fetchone()[4]
		# cols = cols.replace("\n", "?")[cols.index("("):-3] + ")"

		# placeholder = ""
		# for char in cols:
		# 	if char in {"(", "?", ",", ")"}:
		# 		placeholder += char

		return placeholder


	# CRIA A TABELA DE DADOS DOS FILMES
	def create_table(self, name, columns):
		self.cursor.execute(f"CREATE TABLE if not exists {name} {columns}")
		self.con.commit()
		self.name = name
		self.placeholder = self._get_placeholder()


	# DEFINE A TABELA ATUAL A SER TRABALHADA
	def load_table(self, name):
		if not self.has_table(name):
			self.name = ""
			self.placeholder = ""
			print("Tabela nao encontrada")
			return False

		self.name = name
		self.placeholder = self._get_placeholder()
		return True


	# TROCA A TABELA ATUAL
	def change_table(self, new_table, columns):
		if columns:
			create_table(new_table, columns)

		return load_table(new_table)


	# ADICIONA UM DADO A TABELA DE DADOS
	def add_one_to_table(self, entry):
		self.cursor.execute(f"INSERT INTO {self.name} VALUES {self.placeholder}", entry)
		self.con.commit()


	# ADICIONA VARIOS DADOS A TABELA
	def add_many_to_table(self, entries):
		self.cursor.executemany(f"INSERT INTO {self.name} VALUES {self.placeholder}", entries)
		self.con.commit()


	# ATUALIZA DADO
	def update_entry(self, index, **kwargs):
		update = ",".join([f"{key} = '{value}'" for key, value in kwargs.items() if value])
		# print(f"UPDATE {self.name} SET {update} WHERE rowid = {str(index)}")
		self.cursor.execute(f"UPDATE {self.name} SET {update} WHERE rowid = {str(index)}")
		self.con.commit()


	# DELETA DADO
	def delete_entry(self, index):
		self.cursor.execute(f"DELETE from {self.name} WHERE rowid = {index}")
		self.con.commit()


	# PEGA O NUMERO DE ENTRADAS NA TABELA ATUAL
	def get_table_len(self):
		self.cursor.execute(f"SELECT COUNT(*) FROM {self.name}")
		return self.cursor.fetchall()


	# SELECIONA TODOS DADOS
	def get_table(self, complement=""):
		self.cursor.execute(f"SELECT * FROM {self.name} {complement}")
		return self.cursor.fetchall()


	# SELECIONA TODOS DADOS E O ROWID
	def get_table_rowid(self, complement=""):
		self.cursor.execute(f"SELECT rowid, * FROM {self.name} {complement}")
		return self.cursor.fetchall()


	# DELETA TABELA DE DADOS
	def delete_table(self):
		self.cursor.execute(f"DROP TABLE {self.name}")
		self.con.commit()

	# PROCURA NA TABELA
	def search_table(self, **kwargs):
		query = "WHERE "
		for key, value in kwargs.items():
			query += f"{key} = '{value}' AND "
		query = query[:-5]

		result = self.get_table_rowid(query)

		return result[0] if result else []


	# FECHA A CONEXÃO
	def close(self):
		self.cursor.close()
		self.con.close()


	# LISTA AS TABELAS EXISTENTES
	def tables(self):
		query = "SELECT * FROM sqlite_master WHERE type='table'"
		return [x[2] for x in self.cursor.execute(query).fetchall()]


	# TESTA SE A DB TEM A TABELA ESPECIFICADA
	def has_table(self, name):
		query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
		return self.cursor.execute(query, (name,)).fetchone() is not None


	# MOSTRA TODOS ITENS DA TABELA
	def show_table_items(self):
		for item in self.get_table():
			print(item)


	# MOSTRA TODOS ITEMS DE TODAS TABELAS
	def show_all_tables_items(self):
		loaded_table = self.name

		for table in self.tables():
			self.load_table(table)
			self.show_table_items()
			print("--------------------------------------------------------------")

		self.load_table(loaded_table)



# COMANDOS:
# mydb = SQLdb("C:/Users/pedro/Appdata/Roaming/cinefile/" + "movies_data.db", "pedro_minha_lista")

# mydb._get_placeholder()
# mydb.add_one_to_table(("Avengers: Endgame", "", 2019, "super-heroi,acao", 2))
# print(mydb.get_table())

# mydb.con.close() # FECHA A CONEXÃO (BEST PRACTICE)
#self.con.rollback() # CANCELA A EXECUÇÃO DO COMANDO
#self.con.commit() # CONFIRMA A EXECUÇÃO DO COMANDO