# 1. Introdução

O arroz é um alimento básico para cerca de 4,0 bilhões de pessoas e o Brasil produziu 10,6 milhões de toneladas em 2024 (SILVA; WANDER, 2026). As doenças foliares como a queima bacteriana (bacterial blight), a brusone (blast), a mancha parda (brown spot) e o tungro ameaçam a renda de quem produz e a oferta de alimento, e são identificadas por inspeção visual feita por especialistas, que consome tempo e confunde lesões de cores parecidas (SETHY et al., 2020).

# 2. Problema

Sethy et al. (2020) trataram o diagnóstico como classificação de imagens e chegaram a um F1 de 0,9838 com ResNet50 e SVM, mas classificar a folha inteira não mostra onde está a lesão nem quanto da folha foi atingida.

# 3. Solução

A segmentação semântica atribui uma classe a cada pixel e a base RiceSeg-5932 trouxe máscaras manuais para as 5.932 imagens deles, o que permite a este trabalho treinar e comparar modelos U-Net com e sem encoders pré-treinados (ResNet50, ResNet101 e EfficientNetB0) e medir a generalização em uma base externa.

O objetivo geral é treinar um modelo de segmentação semântica para identificar lesões em folhas de arroz. Para isso o trabalho compara a arquitetura U-Net com outros modelos pré-treinados aplicados a ela para encontrar o melhor resultado, compara duas funções de perda (SparseCategoricalCrossEntropy e Dice com SparseCategoricalCrossEntropy) e testa a generalização dos modelos em uma base de dados externa.

As metas da proposta são um Dice de 0,70 e uma acurácia de pelo menos 0,75 no teste externo.


# 4. Metodologia

## 4.1 Segmentação semântica

A segmentação semântica atribui uma classe a cada pixel da imagem e difere da segmentação de instância, que trata cada objeto da mesma classe como um objeto separado. Ela foi escolhida porque o objetivo do trabalho é identificar o tipo de lesão e calcular a área afetada na folha, e quando a folha tem lesões em partes diferentes a segmentação semântica marca todas com a mesma classe enquanto a de instância as trataria como lesões diferentes.

## 4.2 Arquitetura U-Net

O encoder extrai as características da imagem. Ele aplica convoluções que aumentam o número de filtros (feature maps) e a cada etapa reduz a imagem pela metade com MaxPooling, levando para a próxima convolução apenas as características mais relevantes. O decoder pega essas características e gera a máscara de segmentação, e em cada bloco a Conv2DTranspose aumenta a resolução na mesma escala em que o encoder diminuiu até voltar ao tamanho original.

As skip connections ligam os mapas de características do encoder aos do decoder de mesma resolução. O MaxPooling pode perder detalhes e as skips devolvem esses detalhes ao decoder como referência para recriar a máscara, o que deixa as bordas da lesão mais precisas. A saída da U-Net é um softmax por pixel com 5 canais (4 doenças e o fundo), onde cada pixel recebe uma probabilidade por classe e a classe escolhida é a de maior probabilidade.

## 4.3 Encoders pré-treinados

O transfer learning reaproveita uma rede já treinada em outra base e o fine-tuning continua treinando os pesos dela na nova base sem congelá-los. Neste trabalho o fine-tuning foi usado com encoders ResNet e EfficientNet treinados na ImageNet, que tem cerca de 1,28 milhões de imagens em 1.000 classes, e a vantagem é que eles já reconhecem bordas, texturas e cores de uma base diversificada.

A ResNet50 e a ResNet101 foram escolhidas por serem muito usadas em pesquisas de visão computacional. O número no nome indica a profundidade da rede, isto é, a quantidade de camadas com pesos, e a característica da ResNet são as conexões residuais, em que cada bloco soma a sua entrada à sua saída e facilita o treino de redes profundas. A EfficientNetB0 é mais leve porque escala profundidade, largura e resolução em conjunto, o que permite comparar duas redes da mesma família com uma de outra família.

## 4.4 Funções de perda

A Sparse Categorical Crossentropy penaliza a baixa probabilidade dada à classe correta de cada pixel e o valor final é a média sobre os pixels. Diferente da CategoricalCrossentropy tradicional que exige rótulos em one-hot ela aceita números inteiros para representar cada classe.

O Dice loss é baseado na métrica Dice, que mede a sobreposição entre a máscara prevista e a real pela fórmula 2 vezes a interseção dividida pela soma das áreas das duas máscaras. A loss é 1 menos o Dice e como ela compara só a região de cada classe o fundo, que ocupa a maior parte da imagem, não domina o valor.

A CE+Dice (Ma et al., 2021) é a soma das duas funções, em que a crossentropy fornece um gradiente estável pixel a pixel e o Dice foca na sobreposição da região. No estudo de Ma et al. (2021) as perdas compostas desse tipo foram as mais robustas entre as comparadas, e um levantamento de competições do Kaggle mostrou que o Dice e o IoU são as métricas mais usadas na avaliação de segmentação semântica.

## 4.5 Métricas

O IoU (Intersection over Union) compara a máscara real com a prevista pela área da interseção dividida pela área da união das duas, com valor entre 0 e 1. O Dice usa 2 vezes a interseção dividida pela soma das áreas e é sempre maior que o IoU. Para uma lesão real de 100 pixels com 80 em comum com a prevista o IoU é 80 ÷ 120 = 0,67 e o Dice é 160 ÷ 200 = 0,80. As duas métricas são calculadas por classe e a média considera só as quatro doenças para que o fundo, que é a classe predominante, não domine o resultado.

A matriz de confusão compara a classe real (linhas) com a prevista (colunas), e a diagonal mostra os acertos enquanto o restante mostra quais classes o modelo confunde entre si. A precision mede quanto do que o modelo previu como uma classe realmente era dela e o recall mede quanto da classe o modelo encontrou. O F1 é a média harmônica das duas, 2 × precision × recall ÷ (precision + recall), e ajuda a medir o desbalanceamento de classes, e o F1 macro é a média simples entre as classes.

## 4.6 Dados

A base de treino é a de Sethy et al. (2020), com 5.932 patches de fotos de campo de 300×300 das quatro doenças coletadas em Odisha, e as máscaras são as da RiceSeg-5932, feitas manualmente e pareadas com as imagens pelo nome do arquivo. A base de teste externo é a de Hasan et al., da qual foram usadas só as quatro classes em comum com o treino, o que dá 2.623 imagens com um rótulo por imagem e sem máscara.

## 4.7 Pré-processamento

Cada imagem foi pareada com a sua máscara pelo nome do arquivo, que é o mesmo nas duas pastas. A classe de cada par vem da pasta da doença, numerada de 0 a 3 (bacterial blight, blast, brown spot e tungro), e a classe 4 ficou para o fundo, de modo que cada amostra é uma tupla com o caminho da imagem, o caminho da máscara e o número da classe.

As imagens foram lidas em RGB e redimensionadas para 288×288. A escolha inicial era 300×300, que é o tamanho da maior parte das imagens, mas o encoder da ResNet reduz a imagem pela metade a cada estágio e 300 não é divisível por 32, o que fazia o Concatenate falhar por causa da diferença de tamanho entre encoder e decoder.

As máscaras são arquivos .jpg, que deixam os pixels ao redor da lesão com valores diferentes de 0 e 255. Por isso cada máscara foi lida em escala de cinza, redimensionada com o vizinho mais próximo (nearest-neighbor) para não criar valores intermediários e binarizada com limiar 127, ficando 1 onde há lesão e 0 no resto. No remapeamento de pixel para classe o pixel de lesão recebe o número da doença da pasta e todo o resto recebe 4.

O resultado são arrays de imagens com formato (N, 288, 288, 3) e de máscaras com formato (N, 288, 288, 1) salvos em arquivos .npy para que o processamento não precise ser refeito a cada treino. Os dados de teste seguem o mesmo caminho com as quatro doenças em comum com o treino, redimensionados para 288×288 e com um rótulo por imagem porque essa base não tem máscaras.

## 4.8 Divisão dos dados

Os 5.932 pares imagem-máscara pré-processados foram divididos de forma estratificada pela classe da doença em 80% para treino (4.745 pares) e 20% para validação (1.187 pares), de modo que as duas partes mantêm a mesma proporção de cada doença.

A validação serve apenas para controlar o treino por meio de três callbacks: o ModelCheckpoint salva o melhor modelo pelo IoU médio de validação, o EarlyStopping interrompe o treino após oito épocas sem melhora na loss de validação e o ReduceLROnPlateau reduz a taxa de aprendizado após três épocas sem melhora. Como a validação vem da mesma base do treino ela tende a dar um resultado bom, e por isso a generalização é medida na base de teste externo, que não participa do treino.

## 4.9 Arquitetura

Todos os modelos seguem a estrutura U-Net com entrada de 288×288×3 e saída de 288×288×5. O bloco de convolução é o mesmo em toda a rede e consiste em duas camadas Conv2D com kernel 3×3, cada uma seguida de BatchNormalization e ReLU. O decoder também é igual nos modelos e cada bloco aplica uma Conv2DTranspose 2×2 que dobra a resolução, concatena o resultado com a skip da mesma resolução e passa pelo bloco de convolução, e a saída é uma Conv2D 1×1 com softmax e 5 canais (quatro doenças e o fundo).

Na U-Net sem pré-treino o encoder tem quatro estágios com 64, 128, 256 e 512 filtros, cada um com o bloco de convolução e um MaxPooling que reduz a resolução pela metade, e a base tem 1.024 filtros. A imagem chega a 18×18 na base e o decoder devolve ao tamanho original com 512, 256, 128 e 64 filtros.

Na ResNet50 e na ResNet101 o encoder é a rede pré-treinada na ImageNet sem a parte de classificação e com a entrada passando pelo preprocess_input da própria ResNet. As skips e a base saem dos outputs das camadas de convolução da ResNet e a imagem de entrada é a skip de maior resolução. A base chega a 18×18 nas duas e a diferença é que a ResNet101 tem mais camadas no último estágio do encoder, e o decoder usa 512, 256, 128 e 64 filtros. A variante da ResNet101 com decoder maior usa o mesmo encoder e as mesmas skips com o decoder dobrado para 1.024, 512, 256 e 128 filtros, para testar se o decoder era o limite do desempenho.

Na EfficientNetB0 o encoder também é pré-treinado na ImageNet e como ele já normaliza a imagem internamente não usa preprocess_input. Ele reduz a imagem cinco vezes e por isso o decoder tem cinco blocos com 512, 256, 128, 64 e 32 filtros, com as skips vindas de block6a, block4a, block3a e block2a e da imagem de entrada. Em todos os modelos com encoder pré-treinado os pesos do encoder continuam treináveis, sem congelamento.

## 4.10 Treinamento

Cada arquitetura foi treinada com duas funções de perda, a Sparse Categorical Crossentropy e a soma dela com o Dice loss (CE+Dice nos notebooks). Como as máscaras são mapas de números inteiros de 0 a 4 a sparse recebe o rótulo direto sem converter para one-hot, e só o Dice precisa dessa conversão, que é feita dentro da própria loss.

Os hiperparâmetros foram os mesmos para todos os modelos, com otimizador Adam, batch de 16 e no máximo 50 épocas. A taxa de aprendizado inicial é 0,00001 na U-Net sem pré-treino e 0,000001 nos modelos com encoder pré-treinado, já que eles vêm com pesos da ImageNet. A métrica acompanhada durante o treino é o MeanIoU com 5 classes, porque a acurácia não serve quando um modelo que prevê tudo como fundo já teria um valor alto, e o IoU por classe dá ao fundo o mesmo peso de cada doença.

## 4.11 Modelos treinados

Foram treinados 9 modelos, que são as quatro arquiteturas com as duas funções de perda mais a ResNet101 com decoder maior treinada só com CE+Dice. Todos usam os mesmos dados, hiperparâmetros e callbacks e o que muda entre eles é o encoder, o decoder e a loss.

| Encoder | Filtros do decoder | Loss |
|---|---|---|
| U-Net sem pré-treino | 512, 256, 128, 64 | SparseCategoricalCrossEntropy |
| U-Net sem pré-treino | 512, 256, 128, 64 | Dice e SparseCategoricalCrossEntropy |
| ResNet50 | 512, 256, 128, 64 | SparseCategoricalCrossEntropy |
| ResNet50 | 512, 256, 128, 64 | Dice e SparseCategoricalCrossEntropy |
| ResNet101 | 512, 256, 128, 64 | SparseCategoricalCrossEntropy |
| ResNet101 | 512, 256, 128, 64 | Dice e SparseCategoricalCrossEntropy |
| ResNet101 (decoder maior) | 1024, 512, 256, 128 | Dice e SparseCategoricalCrossEntropy |
| EfficientNetB0 | 512, 256, 128, 64, 32 | SparseCategoricalCrossEntropy |
| EfficientNetB0 | 512, 256, 128, 64, 32 | Dice e SparseCategoricalCrossEntropy |

A ResNet101 com decoder maior foi treinada para testar se o decoder limitava o desempenho, já que o encoder da ResNet101 é bem maior que o da ResNet50.

# 5. Resultados
## 5.1 Avaliação
Os 9 modelos foram avaliados na validação (1.187 imagens), onde a máscara real existe e permite medir o IoU e o Dice pixel a pixel. As duas métricas foram calculadas para cada doença, comparando a classe com o resto da imagem, e a média considera só as quatro doenças, deixando o fundo de fora para que ele não infle o resultado.

| Modelo | Bacterialblight | Blast | Brownspot | Tungro | IoU médio | Dice médio |
|---|---|---|---|---|---|---|
| U-Net, SparseCategoricalCrossEntropy | 0,7588 | 0,7318 | 0,7096 | 0,7176 | 0,7295 | 0,8434 |
| U-Net, Dice e SparseCategoricalCrossEntropy | 0,7590 | 0,7424 | 0,7130 | 0,7233 | 0,7344 | 0,8468 |
| ResNet50, SparseCategoricalCrossEntropy | 0,7529 | 0,7255 | 0,6981 | 0,7040 | 0,7201 | 0,8371 |
| ResNet50, Dice e SparseCategoricalCrossEntropy | 0,7512 | 0,7265 | 0,6991 | 0,7104 | 0,7218 | 0,8383 |
| ResNet101, SparseCategoricalCrossEntropy | 0,7524 | 0,7263 | 0,6979 | 0,7101 | 0,7217 | 0,8382 |
| ResNet101, Dice e SparseCategoricalCrossEntropy | 0,7544 | 0,7241 | 0,6953 | 0,7092 | 0,7208 | 0,8375 |
| ResNet101 decoder maior, Dice e SparseCategoricalCrossEntropy | 0,7532 | 0,7288 | 0,6967 | 0,7107 | 0,7223 | 0,8386 |
| EfficientNetB0, SparseCategoricalCrossEntropy | 0,7498 | 0,7231 | 0,6846 | 0,6997 | 0,7143 | 0,8331 |
| EfficientNetB0, Dice e SparseCategoricalCrossEntropy | 0,7466 | 0,7185 | 0,6916 | 0,7001 | 0,7142 | 0,8331 |

As colunas das doenças mostram o IoU de cada uma. O IoU médio ficou entre 0,714 e 0,734 e o Dice médio entre 0,833 e 0,847, uma diferença de no máximo 0,02 entre os modelos, e o melhor foi a U-Net com Dice e SparseCategoricalCrossEntropy. Os encoders pré-treinados não superaram a U-Net sem pré-treino, e a EfficientNetB0 teve os menores valores. A Bacterialblight é a doença mais bem segmentada em todos os modelos e a Brownspot a pior.

## 5.2 Teste externo

Na base externa só existe o rótulo da imagem e por isso a doença prevista para cada imagem foi a que teve mais pixels na máscara prevista, ou "sem lesão" quando o modelo não previu nenhum pixel de lesão. A acurácia compara essa doença com o rótulo da imagem e o F1, a precision e o recall são médias entre as quatro doenças, e as imagens previstas como "sem lesão" contam como erro mas ficam fora da média.

| Modelo | Acurácia | F1 macro | Precision macro | Recall macro |
|---|---|---|---|---|
| U-Net, SparseCategoricalCrossEntropy | 0,4708 | 0,5436 | 0,6858 | 0,5070 |
| U-Net, Dice e SparseCategoricalCrossEntropy | 0,4380 | 0,4689 | 0,6268 | 0,4855 |
| ResNet50, SparseCategoricalCrossEntropy | 0,5925 | 0,6156 | 0,6644 | 0,6089 |
| ResNet50, Dice e SparseCategoricalCrossEntropy | 0,5852 | 0,6056 | 0,6682 | 0,6087 |
| ResNet101, SparseCategoricalCrossEntropy | 0,4773 | 0,4658 | 0,5809 | 0,5213 |
| ResNet101, Dice e SparseCategoricalCrossEntropy | 0,5490 | 0,5626 | 0,6389 | 0,5798 |
| ResNet101 decoder maior, Dice e SparseCategoricalCrossEntropy | 0,5536 | 0,5799 | 0,6487 | 0,5779 |
| EfficientNetB0, SparseCategoricalCrossEntropy | 0,5196 | 0,5048 | 0,6352 | 0,5335 |
| EfficientNetB0, Dice e SparseCategoricalCrossEntropy | 0,5124 | 0,5544 | 0,6654 | 0,5447 |

O desempenho no teste externo ficou bem abaixo do da validação e variou muito entre os modelos, com acurácia de 0,438 a 0,593 e F1 macro de 0,466 a 0,616. O melhor modelo foi a ResNet50 com SparseCategoricalCrossEntropy e nenhum chegou à meta de 0,75 de acurácia. Como a base externa não tem máscaras o Dice e o IoU não podem ser calculados nela, e a meta de 0,70 só foi verificada na validação.

## 5.3 Comparação

O efeito da função de perda não seguiu um padrão. A soma do Dice melhorou a ResNet101 (F1 de 0,466 para 0,563) e a EfficientNetB0 (de 0,505 para 0,554) mas piorou a U-Net (de 0,544 para 0,469) e mudou pouco a ResNet50 (de 0,616 para 0,606). Como cada modelo foi treinado uma única vez essas diferenças podem ser ruído do treino e não efeito real da loss.

Entre os encoders a ResNet50 foi a mais consistente nas duas losses, com os maiores valores de acurácia e F1, enquanto a ResNet101 com SparseCategoricalCrossEntropy teve o pior F1. Um encoder maior não garantiu melhor generalização, e na validação todos ficaram praticamente iguais. O decoder maior da ResNet101 teve um F1 de 0,580 contra 0,563 do decoder normal com a mesma loss, uma diferença pequena que indica que o decoder não era a limitação do desempenho.

## 5.4 Análise de erros

| Modelo | Precision Bacterialblight | Precision Blast | Precision Brownspot | Precision Tungro | Recall Bacterialblight | Recall Blast | Recall Brownspot | Recall Tungro |
|---|---|---|---|---|---|---|---|---|
| U-Net, SparseCategoricalCrossEntropy | 0,651 | 0,402 | 0,849 | 0,841 | 0,250 | 0,557 | 0,340 | 0,881 |
| U-Net, Dice e SparseCategoricalCrossEntropy | 0,615 | 0,358 | 0,797 | 0,737 | 0,285 | 0,645 | 0,129 | 0,883 |
| ResNet50, SparseCategoricalCrossEntropy | 0,703 | 0,338 | 0,833 | 0,784 | 0,508 | 0,541 | 0,499 | 0,887 |
| ResNet50, Dice e SparseCategoricalCrossEntropy | 0,769 | 0,318 | 0,807 | 0,779 | 0,454 | 0,612 | 0,482 | 0,887 |
| ResNet101, SparseCategoricalCrossEntropy | 0,569 | 0,293 | 0,925 | 0,536 | 0,189 | 0,587 | 0,342 | 0,968 |
| ResNet101, Dice e SparseCategoricalCrossEntropy | 0,624 | 0,295 | 0,866 | 0,771 | 0,433 | 0,620 | 0,356 | 0,910 |
| ResNet101 decoder maior, Dice e SparseCategoricalCrossEntropy | 0,679 | 0,304 | 0,844 | 0,767 | 0,394 | 0,559 | 0,469 | 0,890 |
| EfficientNetB0, SparseCategoricalCrossEntropy | 0,501 | 0,271 | 0,853 | 0,916 | 0,731 | 0,409 | 0,114 | 0,880 |
| EfficientNetB0, Dice e SparseCategoricalCrossEntropy | 0,542 | 0,327 | 0,875 | 0,918 | 0,424 | 0,593 | 0,275 | 0,887 |

O padrão de erro foi parecido em todos os modelos. O Tungro foi a doença mais bem reconhecida com recall entre 0,88 e 0,97, e o Blast teve a precision mais baixa, entre 0,27 e 0,40, o que mostra que muitas imagens de outras doenças foram classificadas como Blast. A Bacterialblight e a Brownspot tiveram recall baixo na maioria dos modelos, com valores de 0,11 a 0,73, ou seja, os modelos deixaram de reconhecer boa parte dessas imagens.

A causa desses erros não foi testada. As hipóteses são uma mudança de domínio entre as duas bases, já que o treino é feito de patches de lesões e o teste vem de outra fonte, o redimensionamento para 288×288 de imagens com outras proporções e a regra de escolher a doença com mais pixels, que pode favorecer doenças de lesões grandes. A matriz de confusão e a comparação visual das máscaras previstas ainda precisam ser feitas para confirmar quais classes são confundidas.

## 5.5 Overfitting

Nos modelos com encoder pré-treinado o IoU médio de treino ao fim do treino ficou bem acima do de validação, como 0,853 contra 0,768 na ResNet101 e 0,891 contra 0,765 na ResNet101 com decoder maior. Na U-Net sem pré-treino a diferença foi menor, de 0,809 contra 0,780, e a loss de treino e de validação ficaram próximas. Isso indica que quanto maior a capacidade do modelo mais ele se ajusta ao treino sem ganho equivalente na validação.

O melhor IoU de validação foi atingido cedo nas ResNets, entre as épocas 17 e 32, e depois disso a validação ficou parada enquanto o treino continuou melhorando, e o ModelCheckpoint guardou justamente essas épocas. O maior problema de generalização está na diferença para a base externa, onde a acurácia ficou abaixo de 0,60 contra um IoU de validação acima de 0,71. Isso não é só ajuste excessivo ao treino, porque a validação vem da mesma base do treino e não detecta a mudança de domínio.

# 6. Conclusão

Este trabalho treinou e comparou nove modelos de segmentação semântica de lesões em folhas de arroz, combinando a U-Net com encoders ResNet50, ResNet101 e EfficientNetB0 e duas funções de perda. Na validação todos os modelos passaram de 0,70 de IoU e de Dice médios, com diferenças de no máximo 0,02 entre eles, e por isso a validação não separou os modelos.

No teste externo o melhor modelo foi a ResNet50 com SparseCategoricalCrossEntropy, com acurácia de 0,593 e F1 macro de 0,616, abaixo da meta de 0,75. A soma da loss Dice com a crossentropy não teve efeito muito bom, e o decoder maior não resolveu a limitação e tambem o encoder maior não garantiu melhor generalização. 

O Tungro foi bem reconhecido e o Blast foi a doença mais confundida com as outras

Os resultados têm limitações, pois cada modelo foi treinado uma única vez, o teste externo tem só o rótulo por imagem e a validação vem da mesma base do treino. Outra limitação é o tamanho da base que tem 4.745 pares imagem e máscara no treino e por isso é pequena para encoders grandes como a ResNet101. Nenhuma técnica de data augmentation foi aplicada, podendo ter variações de rotação, espelhamento, brilho ou contraste que ajudariam a aumentar a variedade dos dados e a generalizar para fotos tiradas em outros cenários como as da base externa. Além disso só foi testado a arquitetura U-Net com três encoders e outras arquiteturas de segmentação(mais atuais) podem ter maior efeito na base. Como próximos passos fica para aplicar o data augmentation testar outras arquiteturas de segmentação

# 7. Instruções de uso

Para utilizar o projeto clone o repositório do bootcamp e entre na pasta do projeto que é a card-29/segmentation_rice. Os modelos '.keras' e as imagens das bases não vêm no clone na seção 7.3 será explicado como baixá-los.

```bash
git clone https://github.com/beuren33/Bootcamp-Aprendizado-de-Maquina-LAMIA.git
cd Bootcamp-Aprendizado-de-Maquina-LAMIA/card-29/segmentation_rice
```

## 7.1 Requisitos

- Python 3.10
- GPU recomendada para o treino. Os notebooks de arquiteturas/ e avaliacao/ foram executados no Google Colab.

```bash
pip install tensorflow numpy opencv-python scikit-learn matplotlib pandas tqdm jupyter
```

## 7.2 Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| raw/ | Bases originais baixadas (raw/zips/) e extraídas (raw/data/) |
| preprocessing/ | Notebook que gera os arrays .npy |
| processed/ | Arrays prontos: train/ e test/ |
| arquiteturas/ | Um notebook de treino por encoder e por função de perda |
| models/ | Pesos treinados '.keras'. Não estão no repositório porque passam de 100 MB(seção 7.3) |
| avaliacao/ | Notebook que avalia os 9 modelos |

## 7.3 Obter os dados e os modelos

Baixe as bases e extraia em raw/data/:

| Base | Uso | Link |
|---|---|---|
| Rice Leaf Disease Images | Imagens de treino | https://data.mendeley.com/datasets/fwcj7stb8r/1 |
| Rice Leaf Disease Segmentation Masks | Máscaras de treino | https://data.mendeley.com/datasets/92jc6w6mcy/1 |
| A Rice Leaf Disease Image Dataset for Multi-Class | Teste externo | https://data.mendeley.com/datasets/n8jpkpfz5p/1 |

Os arrays já processados e os 9 modelos treinados estão no Drive do projeto: https://drive.google.com/drive/folders/1ygX12Npk6KUlE9s6wGCiMN2cDcIgj7UX?usp=sharing. Se usar o Drive, pulae para a seção 7.5 ou 7.6 colocando os arquivos em processed/ e models/.

## 7.4 Pré-processar

1. Abra preprocessing/preprocessing.ipynb
2. Ajuste as listas list_path_img, list_path_mask e list_path_test para a pasta onde as bases foram extraídas e os caminhos dos np.save para processed/
3. Execute todas as células

O notebook compara cada imagem com a máscara de mesmo nome, redimensiona para 288×288, binariza a máscara com limiar 127, e divide em 80% treino e 20% validação, sendo feita a divisão com que cada classe fique balanceada com a divisão. No teste externo usa só as pastas bacterial_leaf_blight, leaf_blast, brown_spot e tungro.

Saídas em processed/: train/x_train.npy, y_train.npy, x_val.npy, y_val.npy e test/x_test.npy, y_test.npy. Imagens com formato (N, 288, 288, 3) e máscaras de treino com formato (N, 288, 288, 1). 
Classes: 0 Bacterialblight, 1 Blast, 2 Brownspot, 3 Tungro, 4 fundo.

## 7.5 Treinar

- Escolha o notebook em 'arquiteturas/':

| Notebook | Encoder | Loss |
|---|---|---|
| U_Net.ipynb | Sem pré-treino | SparseCategoricalCrossEntropy |
| U_Net_dice_loss.ipynb | Sem pré-treino | CE+Dice |
| U_Net_RESNET50.ipynb | ResNet50 | SparseCategoricalCrossEntropy |
| U_Net_RESNET50_dice_loss.ipynb | ResNet50 | CE+Dice |
| U_Net_RESNET101.ipynb | ResNet101 | SparseCategoricalCrossEntropy |
| U_Net_RESNET101_dice_loss.ipynb | ResNet101 | CE+Dice |
| U_Net_RESNET101_decoder_maior_dice_loss.ipynb | ResNet101, decoder maior | CE+Dice |
| U_Net_EfficientNetB0.ipynb | EfficientNetB0 | SparseCategoricalCrossEntropy |
| U_Net_EfficientNetB0_dice_loss.ipynb | EfficientNetB0 | CE+Dice |

- Ajuste os caminhos dos .npy e a variável path_model, onde o melhor modelo é salvo. Se não usar Colab remova a célula drive.mount
- Execute todas as células.
- Os hiperparâmetros são iguais em todos os notebooks: Adam, batch size 16 e até 50 épocas. O ModelCheckpoint guarda em path_model a época com maior IoU médio de validação

## 7.6 Avaliar

- Abra avaliacao/models_evaluation.ipynb
- Ajuste os caminhos dos .npy e dos .keras em cada célula de modelo.
- Execute todas as células.
- O notebook calcula IoU e Dice por doença na validação, e acurácia, F1 macro, precision e recall no teste externo. A previsão do teste é feita em blocos de 100 imagens porque ao tentar prever as 2.623 de uma vez, pode esgotar a memória da GPU do Colab, como ocorrido em outras tentativas.

## 7.7 Prever em uma imagem nova

```python
import numpy as np
import cv2
from keras.models import load_model

modelo = load_model("models/modelo_unet_resnet.keras", compile=False)

# le a imagem em RGB e ajusta para o tamanho do treino
img = cv2.cvtColor(cv2.imread("folha.jpg"), cv2.COLOR_BGR2RGB)
# troque o nome da imagem
img = cv2.resize(img, (288, 288))

# o modelo da a probabilidade das cinco classes em cada pixel
prob = modelo.predict(img[np.newaxis].astype("float32"))
# cria um novo canal para guardar as probs

# classe de cada pixel de zero a tres sao as doencas e quatro e o fundo
mascara = prob[0].argmax(axis=-1)

# conta os pixels de cada doenca
pixels = []
for c in range(4):
    pixels.append((mascara == c).sum())

# a doenca da imagem e a que tem mais pixels
doenca = np.argmax(pixels)

# se nao ha pixel de doenca o resultado e quatro, sem lesao
if sum(pixels) == 0:
    doenca = 4

print(doenca)
```

A entrada é a imagem RGB 288×288 com valores de 0 a 255, sem normalização, porque o preprocess_input da ResNet já está dentro do modelo e a EfficientNetB0 normaliza internamente. Para muitas imagens, chame predict em blocos e aplique o argmax em cada bloco.

## 7.8 Limitações

O melhor modelo no teste externo foi a ResNet50 com SparseCategoricalCrossEntropy (acurácia 0,593 e F1 macro 0,616) sendo abaixo da meta de 0,75. A quantidade de dados também limita o trabalho já que o treino usa 4.745 pares de imagem e máscara e a validação 1.187 imagens, o que é pouco para encoders grandes como a ResNet101

## 7.9 Trabalhos futuros

- Aplicar data augmentation (rotação, espelhamento, variação de brilho e contraste) para aumentar a quantidade dos dados de treino e reduzir a diferença entre o desempenho dos modelos na validação e o teste externo.
- Testar outras arquiteturas de segmentação além da U-Net, como por exemplo DeepLabV3+, SegFormer ou U-Net++.
