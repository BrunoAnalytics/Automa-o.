function storeSelectedBoardId() {
    var selectBoard = document.getElementById('select-board');
    var selectedBoardId = selectBoard.value;
    document.getElementById('selected-board-id').value = selectedBoardId;
}

function executarAutomacao() {
    var selectedBoardId = document.getElementById('selected-board-id').value;

    // Exibir indicador de progresso
    document.getElementById('loading').style.display = 'block';

    // Desabilitar o botão de execução durante a automação
    document.getElementById('executar-automacao').disabled = true;

    // Aqui você pode adicionar a lógica para chamar a rota /executar_automacao_asana via fetch ou AJAX
    fetch('/executar_automacao_asana', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ board_id: selectedBoardId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao executar automação: ' + response.status);
        }
        return response.text();
    })
    .then(result => {
        // Ocultar indicador de progresso
        document.getElementById('loading').style.display = 'none';

        // Exibir mensagem de sucesso
        document.getElementById('success-message').style.display = 'block';

        // Habilitar o botão de execução novamente
        document.getElementById('executar-automacao').disabled = false;

        // Exibir resultado ou tomar ações necessárias com base no resultado
        console.log(result); // Exemplo: exibir no console
    })
    .catch(error => console.error('Erro ao executar automação:', error));
}

function showLists() {
    var selectBoard = document.getElementById('select-board');
    var selectedBoardId = selectBoard.value;

    fetch('/get_lists', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ board_id: selectedBoardId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao obter listas do Trello: ' + response.status);
        }
        return response.json();
    })
    .then(lists => {
        var listsContainer = document.getElementById('lists-container');
        listsContainer.innerHTML = ''; // Limpa o conteúdo atual

        lists.forEach(lista => {
            var listaDiv = document.createElement('div');
            listaDiv.classList.add('list-item');
            listaDiv.innerHTML = `
                <input type="checkbox" name="selected-lists[]" value="${lista.id}" id="${lista.id}">
                <label for="${lista.id}">${lista.name}</label>
            `;
            listsContainer.appendChild(listaDiv);
        });
    })
    .catch(error => console.error('Erro ao obter listas do Trello:', error));
}
