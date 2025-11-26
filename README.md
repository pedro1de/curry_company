# 🍛 Projeto Curry Company - Dashboard de Entregas

## 🧩 1. Problema de Negócio

A **Cury Company** é uma empresa de tecnologia que criou um aplicativo que conecta **restaurantes**, **entregadores** e **clientes**.
Por meio do app, os usuários podem fazer pedidos de refeições em restaurantes cadastrados e recebê-las em casa através de entregadores também registrados na plataforma.

A empresa coleta diversos dados — sobre **entregas, tipos de pedidos, condições climáticas, avaliações de entregadores** e outros — mas o **CEO não possui visibilidade completa dos principais KPIs** de crescimento do negócio.

Você foi contratado como **Cientista de Dados** para criar uma solução que organize esses indicadores estratégicos em um **painel interativo**, permitindo que o CEO acompanhe o desempenho da empresa e tome decisões rápidas e eficazes.

O modelo de negócio da Cury Company é do tipo **Marketplace**, intermediando as relações entre **restaurantes**, **entregadores** e **clientes**.

O CEO deseja visualizar as seguintes métricas:

### 📊 Métricas da Empresa

1. Quantidade de pedidos por dia
2. Quantidade de pedidos por semana
3. Distribuição dos pedidos por tipo de tráfego
4. Comparação do volume de pedidos por cidade e tipo de tráfego
5. Quantidade de pedidos por entregador por semana
6. Localização central de cada cidade por tipo de tráfego

### 🏍️ Métricas dos Entregadores

1. Menor e maior idade dos entregadores
2. Pior e melhor condição dos veículos
3. Avaliação média por entregador
4. Avaliação média por tipo de tráfego
5. Avaliação média por condições climáticas
6. Top 10 entregadores mais rápidos por cidade
7. Top 10 entregadores mais lentos por cidade

### 🍽️ Métricas dos Restaurantes

1. Quantidade de entregadores únicos
2. Distância média entre restaurantes e locais de entrega
3. Tempo médio e desvio padrão de entrega durante festivais
4. Tempo médio e desvio padrão de entrega fora de festivais
5. Tempo médio de entrega por cidade

O objetivo do projeto é **criar um conjunto de gráficos e tabelas interativas** que exibam essas métricas de forma clara e intuitiva para o CEO.

---

## 📅 2. Premissas da Análise

1. A análise foi realizada com dados entre **11/02/2022 e 06/04/2022**.
2. O modelo de negócio considerado foi o **Marketplace**.
3. Foram consideradas três principais visões de negócio:

   * Visão de pedidos (transações)
   * Visão de entregadores
   * Visão de restaurantes
  
---

## 🧠 3. Estratégia da Solução

O **painel estratégico** foi desenvolvido com base em três visões principais do negócio:

### 🔹 Visão do Crescimento da Empresa

* Pedidos por dia
* Porcentagem de pedidos por condições de trânsito
* Quantidade de pedidos por tipo e cidade
* Pedidos por semana
* Quantidade de pedidos por tipo de entrega
* Quantidade de pedidos por condições de trânsito e tipo de cidade

### 🔹 Visão do Crescimento dos Entregadores

* Idade do entregador mais velho e mais novo
* Avaliação dos veículos (melhor e pior)
* Avaliação média por entregador
* Avaliação média por condições de trânsito
* Avaliação média por condições climáticas
* Tempo médio dos entregadores mais rápidos
* Tempo médio dos entregadores mais rápidos por cidade

### 🔹 Visão do Crescimento dos Restaurantes

* Quantidade de pedidos únicos
* Distância média percorrida
* Tempo médio de entrega em festivais e dias normais
* Desvio padrão do tempo de entrega em festivais e dias normais
* Tempo médio de entrega por cidade
* Distribuição do tempo médio de entrega por cidade
* Tempo médio de entrega por tipo de pedido

---

## 💡 4. Top 3 Insights de Dados

1. A **sazonalidade dos pedidos é diária**, com variação de cerca de **10% entre dias consecutivos**.
2. As **cidades semi-urbanas** não apresentam condições de trânsito classificadas como ruins.
3. As **maiores variações no tempo de entrega** ocorrem durante **climas ensolarados**.

---

## 🌐 5. Produto Final

O resultado do projeto é um **painel online**, hospedado em nuvem, acessível por qualquer dispositivo conectado à internet.

🔗 **Acesse o painel:** [https://project-currycompany.streamlit.app/](https://project-currycompany.streamlit.app/)

---

## 🏁 6. Conclusão

O painel desenvolvido permite visualizar as métricas mais relevantes do negócio de forma centralizada.
Com base na análise, observou-se que o **número de pedidos cresceu entre a semana 6 e a semana 13 de 2022**, indicando um movimento positivo no desempenho da empresa.

---

## 🚀 7. Próximos Passos

1. Reduzir o número de métricas exibidas para maior clareza
2. Criar novos filtros interativos
3. Adicionar novas visões de negócio

