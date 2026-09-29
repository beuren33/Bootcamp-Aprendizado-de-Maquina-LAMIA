import torch
import torch.nn as nn
from torch.nn import functional as F

batch_size = 64 # quantas sequencias processadas em paralelo
block_size = 256 # contexto de tokens
max_iters = 5000
eval_interval = 500
learning_rate = 3e-4 # taxa de aprenndizado
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200
n_embd = 384 # dimensao do embedding 
n_head = 6 # numero de headers de self-attention em paralelo
n_layer = 6 # numero de blocos transformers
dropout = 0.2 

torch.manual_seed(1337)

with open('/home/beuren/Documentos/Bootcamp-LAMIA/card-27/course/GPT/input.txt', 'r', encoding='utf-8') as f:
    text = f.read()
    # abre o arquivo

# criando uma lista ordenada dos carcteres no texto
chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])
#fazendo o mapeamento dos indices para seus respectivos carcteres
# encode pega uma string e retorna seus indices em uma lista
# decode pega uma lista de numeros e transforma emm uma string


data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9*len(data))
train_data = data[:n]
val_data = data[n:]
#separando os dados de treino e teste

def get_batch(split):
    # gera um batch aleatorio de inputs e targets
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    x, y = x.to(device), y.to(device) # move pra GPU se disponivel
    return x, y

@torch.no_grad() # desliga calculo de gradiente para a avaliacao
def estimate_loss():
    # calcula loss medio pra treino e validacao
    out = {}
    model.eval() # modo avaliacao
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train() # volta pro modo treino
    return out

class Head(nn.Module):
    """ uma cabeca de self-attention """

    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        # register_buffer guarda a mascara junto do modelo mas nao como parametro treinavel
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # entrada (batch, tempo, canais) 
        # saida (batch, tempo, head_size)
        B,T,C = x.shape
        k = self.key(x)
        q = self.query(x)
        # calcula as afinidades entre as posicoes
        wei = q @ k.transpose(-2,-1) * k.shape[-1]**-0.5 # escala por raiz de head_size
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf')) # mascara causal
        wei = F.softmax(wei, dim=-1) # normaliza em distribuicao de probabilidade
        wei = self.dropout(wei) # dropout nos pesos
        v = self.value(x)
        out = wei @ v # media ponderada da posição dado os tokens passados
        return out

class MultiHeadAttention(nn.Module):
    """ multiplas cabecas de self-attention rodando em paralelo """

    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        # cria varios headers cada uma com seus proprios pesos
        self.proj = nn.Linear(head_size * num_heads, n_embd)
        # projeta a junção dos headers de volta pra dimensao do embedding
        self.dropout = nn.Dropout(dropout)
        #desligaa alguns neuronios

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        # roda cada header e junta os resultados na ultima dimensao
        out = self.dropout(self.proj(out))
        return out

class FeedFoward(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd), # expande a dimensao
            nn.ReLU(), 
            nn.Linear(4 * n_embd, n_embd), # volta pra dimensao original
            nn.Dropout(dropout),
        )
        

    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_head):
        # dimensao do embedding e quantidade de headers
        super().__init__()
        head_size = n_embd // n_head # divide a dimensao total entre as cabecas para que seja processado paralelamente
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedFoward(n_embd) # proccessa cada token
        self.ln1 = nn.LayerNorm(n_embd) # camada de normalização antes do attention e do feedfoward
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        # soma a saida do attention com o input original
        x = x + self.ffwd(self.ln2(x))
        # mesma logica do attention mas aplicado ao feed forward
        return x

class GPTLanguageModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
        # empilha n_layer blocos transformer em sequencia
        self.ln_f = nn.LayerNorm(n_embd) # normalizacao 
        self.lm_head = nn.Linear(n_embd, vocab_size) # projecao final pra logits

        # inicializacao customizada dos pesos
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        # inicializa pesos com distribuicao normal
        # ajuda o treino a comecar de forma mais estavel

    def forward(self, idx, targets=None):
        B, T = idx.shape

        tok_emb = self.token_embedding_table(idx) # indices de cada token
        pos_emb = self.position_embedding_table(torch.arange(T, device=device)) # sua posição
        x = tok_emb + pos_emb # soma seu indice e sua posição
        x = self.blocks(x) # passa pela quantidade de layers blocos transformer
        x = self.ln_f(x) # normalizacao final
        logits = self.lm_head(x) # saida nao normalizada

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def generate(self, idx, max_new_tokens):
        # idx é um array (B,T) de indices no contexto atual
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]
            # corta o contexto pros ultimos block_size tokens
            # necessario porque a posição do embedding so tem block_size posicoes cadastradas
            logits, loss = self(idx_cond)
            logits = logits[:, -1, :] # so a previsao da ultima posicao importa
            probs = F.softmax(logits, dim=-1)# transformando em probabilidade
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

model = GPTLanguageModel()
m = model.to(device)
print(sum(p.numel() for p in m.parameters())/1e6, 'M parameters')
# soma o total de parametros treinaveis do modelo

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

for iter in range(max_iters):

    if iter % eval_interval == 0 or iter == max_iters - 1:
        losses = estimate_loss()
        print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

    xb, yb = get_batch('train')

    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

context = torch.zeros((1, 1), dtype=torch.long, device=device)
print(decode(m.generate(context, max_new_tokens=500)[0].tolist()))
#open('more.txt', 'w').write(decode(m.generate(context, max_new_tokens=10000)[0].tolist()))
