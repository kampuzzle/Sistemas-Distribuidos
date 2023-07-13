Publish Subscribe com MQTT e Autenticação por Assinatura Digital
Instruções para execução
Execute o código main.py, acrescentando o argumento N que representa o número de clientes que irão participar.

Por padrão, o código se conecta ao broker "broker.emqx.io", mas pode ser alterado se, ao executar o main.py, receber um segundo argumento que representa o endereço do broker.

O código main simula uma situação em que N clientes se inscrevem e dividem-se em threads. Cada Cliente irá se manifestar no terminal, sendo diferenciado pelos ids e cores do terminal.

Quando todos os clientes se conectarem, um menu irá perguntar se deseja encerrar o programa ou gerar um novo desafio. Digite 'e' para encerrar o programa ou 'n' para gerar um novo desafio.

Vídeo demonstrativo
Link para o vídeo

Descrição da implementação
O código main.py se conecta a um broker MQTT e a N clientes. Cada cliente é dividido em uma thread. Cada cliente se inscreve em um tópico e publica mensagens nesse tópico. O broker recebe as mensagens e as distribui para os clientes inscritos no tópico.

A classe Cliente implementa as funções que irão coordenar a eleição. Quando n clientes forem iniciados, a eleição começa e, através de votação aleatória, um líder é escolhido. O líder é responsável por enviar mensagens de controle para os outros clientes utilizando as funções de controle implementadas na classe Controlador. O líder também é responsável por enviar os desafios criptográficos para os outros clientes, alimentando uma fila no MQTT que será consumida pelos outros clientes. Esses desafios são acompanhados de uma assinatura digital gerada pelo cliente emissor.

A autenticação por assinatura digital é implementada usando criptografia assimétrica. Cada cliente possui um par de chaves, uma chave privada e uma chave pública. A chave privada é usada para assinar as mensagens, enquanto a chave pública é usada para verificar a assinatura das mensagens recebidas. Dessa forma, cada mensagem enviada contém uma assinatura digital que é validada pelos outros clientes usando a chave pública do cliente emissor.

A classe Controlador implementa as funções de controle que são usadas pelo líder para enviar mensagens aos outros clientes. Essas mensagens também são assinadas digitalmente pelo líder. Os outros clientes recebem as mensagens, verificam a assinatura usando a chave pública do líder e executam a ação solicitada na mensagem de controle.

A classe Minerador recebe os desafios do líder, verifica a assinatura do líder usando sua chave pública e, em seguida, tenta resolver o desafio. Se o minerador encontrar a solução correta, ele assina digitalmente a solução e envia de volta para o líder. O líder verifica a assinatura do minerador usando a chave pública do minerador e valida a solução.

Conclusão
Com este trabalho, foi possível implementar a autenticação por assinatura digital em um sistema de Publish/Subscribe com MQTT. A adição da funcionalidade de assinatura digital aumenta a segurança do sistema, permitindo a verificação da autenticidade e integridade das mensagens trocadas entre os clientes.

A utilização da criptografia assimétrica proporciona um método robusto de autenticação, em que cada cliente possui uma chave privada secreta e uma chave pública compartilhada. A assinatura digital garante que somente o cliente legítimo tenha assinado a mensagem, e a verificação da assinatura usando a chave pública garante a autenticidade do emissor.

Dessa forma, o sistema implementado oferece uma forma segura e confiável de comunicação entre os clientes, garantindo que as mensagens não tenham sido adulteradas ou falsificadas durante o processo de troca. A autenticação por assinatura digital é uma adição valiosa para aplicações que exigem segurança e integridade na troca de informações.

Em resumo, a implementação da autenticação por assinatura digital em um sistema de Publish/Subscribe com MQTT demonstrou-se eficaz e relevante para o contexto proposto. A adição dessa funcionalidade fortalece a segurança do sistema, tornando-o mais confiável e adequado para aplicações que exigem autenticidade e integridade na troca de mensagens
