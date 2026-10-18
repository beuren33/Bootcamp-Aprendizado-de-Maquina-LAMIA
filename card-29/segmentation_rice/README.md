# Processamento dos dados

## 1. Fontes dos dados
Foram selecionados tres datasets para a composição deste projeto final. A principal base de dados que será usada é a junção dp Rice Leaf Disease Images com as suas respectivas mascaras da base Rice_Leaf_Disease_Segmentation_Masks. Uma terceira base de dados será utilizada para a validação do modelo, ou seja, usar essa base como teste para ver o desempenho do modelo ao encarar dados nunca vistos antes.

## 2. Pareamento imagem e máscara
A junção das imagens de folhas de arroz a suas respectivas mascaras, foi realizada através da nomeclatura de cada arquivo, onde cada arquivo é numerado respectivamente com sua mascara. Assim, foi adicionado a uma lista as tuplas que possuem o caminho da imagem original, o caminho para o arquivo da mascara, e sua classe.

## 3. Classes e mapeamento de ID
Os arquivos de fotos e mascaras, estvam separados por pastas nomeadas com a respectiva doença, com isso uma enumeração foi possivel saber quais imagens pertencem a qual classe. Gerando a seguinte tabela de rotulação:

classe_id | treino (Rice Leaf Disease Images)	| teste (A Rice Leaf Disease Image Dataset for Multi-Class)
          |                                     |
0	      | Bacterialblight	                    | bacterial_leaf_blight
1	      | Blast	                            | leaf_blast
2	      | Brownspot	                        | brown_spot
3	      | Tungro	                            | tungro
4         | fundo/não lesão                     | fundo/não doença

De zero até três, são os tipos de lesões presentes no dataset, e o id quatro se refere a quando o pixxel é um fundo ou não tem lesão. O motivo de fazer essa separação de lesão e fundo, se define por conta do modelo aprender a identificar os pixels que possuem lesão, nisso para classificar o fundo ou a folha sem lesão foi criado esta classe quatro.

## 4. Resize das imagens e máscaras
Para todas as imagens foram realizados um redimensionamento, pelo desbalnceamneto entre o dataset de treino e o de teste. A escolha inicial foi 300x300, pois a maioria das imagens ja estao neste tamanho, porém esse valor foi trocado para 288x288, já que a arquitetura com encoder RESNET50 reduz a imagem por fatores de 2 em cada bloco do encoder, e 300 não é divisível de forma limpa por essas reduções, gerando incompatibilidade de tamanho entre o encoder e o decoder na hora do Concatenate. 288 é múltiplo de 32, evitando esse problema. As imagens de folha são RGBs enquanto as mascaras apnas possuem a segmentação da lesão na imagem com o fundo preto, nisso temos as imagens com três canais e um unico canal que é o caso das mascaras.

## 5. Binarização da máscara
Ao realizar uma amostragem das imagens e suas mascaras após o processamento, pela mascara ser .jpg ela nao possuia o pixel 0 ou 255, tendo pontos fracos ao redor da segmentação. Isso foi causado pelo tipo definido na matriz de zeros, nesse caso o booleano. Para resolver, foi alterado o tipo para inteiro e tambem criado uma mascara binária, garantindo que os pixels sejam parte do fundo ou da segmentação.

## 6. Remapeamento pixel para classe
O mapeamento das lesões foi feita com a mascara binária e um condição que, onde possuia uma lesão era associado o rótulo da classe que foi extraída como dito anteriormente pela pasta de onde esta presente a imagem.

## 7. Split treino/validação
A separação dos dados de treino e validação seguiu a porcentagem de 90% para o treino e 10% validação que será feita durante o treino. O motivo para escolher essa validação e não definir como dados de teste, se define tanto por boa prática mas tambem para testar o modelo em uma base diferente da de treino.

## 8. Dados de teste externo
O processamento dos dados de teste, se define pela escolha das classes que estavam no treino, pois o dataset de teste possuia classes que não estavam no treino, por isso foi necessário a limpeza.
