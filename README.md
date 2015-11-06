# Classificador de texto bayesiano

## Descrição dos arquivos

* /documents: Coleção de arquivos extraídos da base Reuters-21578
* /src: Arquivos fonte em python
* /tests: resultados dos testes feitos sobre o conjunto de treinamento
  * /on test documents: resultado dos testes feitos sobre o conjunto de teste

## Para executar o código

1. É necessário ter instalado os pacotes NLTK e BeautifulSoup 4
2. Dentro da pasta /src inicie o console python
3. Uma vez no console invoque a rotina de processamento de texto e salve o resultado
  * >>> import file_reader
  * >>> data = file_reader.create_vocabulary()
4. Então execute a rotina de classificação do texto usando os parâmetros retornados
  * >>> import classifier
  * >>> classifier.tests(data['raw_test_documents'],data['mega_documents'],data['a_priori_probabilities'],data['vocabulary'])

Os resultados de precisão, recall, acurácia e F1 devem ser imprimidos no console.
