# 1. Introdução

O arroz é um alimento básico para cerca de 4,0 bilhões de pessoas e o Brasil produziu 10,6 milhões de toneladas em 2024 (SILVA; WANDER, 2026). As doenças foliares como a queima bacteriana (bacterial blight), a brusone (blast), a mancha parda (brown spot) e o tungro ameaçam a renda de quem produz e a oferta de alimento, e são identificadas por inspeção visual feita por especialistas, que consome tempo e confunde lesões de cores parecidas (SETHY et al., 2020).

# 2. Problema

Sethy et al. (2020) trataram o diagnóstico como classificação de imagens e chegaram a um F1 de 0,9838 com ResNet50 e SVM, mas classificar a folha inteira não mostra onde está a lesão nem quanto da folha foi atingida.

# 3. Solução

A segmentação semântica atribui uma classe a cada pixel e a base RiceSeg-5932 trouxe máscaras manuais para as 5.932 imagens deles, o que permite a este trabalho treinar e comparar modelos U-Net com e sem encoders pré-treinados (ResNet50, ResNet101 e EfficientNetB0) e medir a generalização em uma base externa.

O objetivo geral é treinar um modelo de segmentação semântica para identificar lesões em folhas de arroz. Para isso o trabalho compara a arquitetura U-Net com outros modelos pré-treinados aplicados a ela para encontrar o melhor resultado, compara duas funções de perda (SparseCategoricalCrossEntropy e Dice com SparseCategoricalCrossEntropy) e testa a generalização dos modelos em uma base de dados externa.

As metas da proposta são um Dice e um IoU médios de pelo menos 0,70 e uma acurácia de pelo menos 0,75 no teste externo.
