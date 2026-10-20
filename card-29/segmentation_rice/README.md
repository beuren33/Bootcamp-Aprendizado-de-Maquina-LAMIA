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

